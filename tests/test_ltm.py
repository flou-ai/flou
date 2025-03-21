from copy import deepcopy

import pytest
from pydantic import BaseModel

from flou.database import get_db
from flou.engine import get_engine
from flou.conf import Engine
from flou.ltm import LTM
from .utils import convert_lists_to_sets, patch_settings


class Child(LTM):
    name = "child"

    def get_initial_store(self):
        return {"test": "test"}


class Root(LTM):
    init = [Child]
    name = "root"


# leaving this (not needed) for when we need to override env / conf
@pytest.mark.parametrize(
    "patch_settings",
    [
        {"engine": Engine(engine="flou.engine.dummy.DummyEngine")},
    ],
    indirect=True,
)
def test_initial_and_get_store(patch_settings, session):

    root = Root()
    root._init_ltms()

    assert root.store["_status"] == "init"
    assert root._sub_ltms["child"].store["_status"] == "init"
    assert root._sub_ltms["child"].store["test"] == "test"


def test_update_store(session):

    db = get_db(session)

    root = Root()
    id = root.start()
    root.update_store({"str": "test"})
    root.update_store({"int": 1})
    root.update_store({"bool": True})
    root.update_store({"dict": {"test": "test"}})
    root.update_store({"list": [1, 2, 3]})
    db.update_store(root, "test", "test")

    root2 = db.load_ltm(id)

    assert root2.store["str"] == "test"
    assert root2.store["int"] == 1
    assert root2.store["bool"] == True
    assert root2.store["dict"] == {"test": "test"}
    assert root2.store["list"] == [1, 2, 3]

    root2.update_store({"new_key": [1, 2, 3]})
    db.update_store(root2, "test2", "test")

    ltm = db.load_ltm(id, snapshots=True)
    snapshots = ltm._snapshots
    assert snapshots[0]["reason"] == "start"
    assert snapshots[1]["reason"] == "execute"
    assert snapshots[1]["item"]["fqn"] == "root"
    assert snapshots[2]["reason"] == "execute"
    assert snapshots[2]["item"]["fqn"] == "root.child"
    assert snapshots[3]["reason"] == "test"
    assert snapshots[3]["item"] == "test"
    assert snapshots[4]["reason"] == "test2"
    assert snapshots[4]["item"] == "test"

    recreation = {}
    import jsonpatch

    for snapshot in snapshots:
        recreation = jsonpatch.apply_patch(recreation, snapshot["patch"])

    assert recreation == root2._store


class Start(LTM):
    name = "start"

    def run(self, payload=None):
        self.transition("go")


class End(LTM):
    name = "end"


class LinearLTM(LTM):
    name = "linear"
    init = [Start]
    transitions = [{"from": Start, "label": "go", "to": End}]


def test_transition(session):
    linear = LinearLTM()
    id = linear.start()


    db = get_db(session)
    linear_loaded = db.load_ltm(id)

    assert linear_loaded.store["_status"] == "active"
    assert linear_loaded.store["start"]["_status"] == "finished"
    assert linear_loaded.store["end"]["_status"] == "active"


class NestedLTM(LTM):
    name = "nested"
    init = [Start]
    transitions = [{"from": Start, "to": LinearLTM, "label": "go"}]


def test_structure(session):
    ltm = LinearLTM()
    structure = ltm.as_json()
    # as lists are not ordered, we need to convert them to sets
    assert convert_lists_to_sets(structure) == convert_lists_to_sets(
        {
            "name": "linear",
            "fqn": "linear",
            "init": ["start"],
            "transitions": [
                {
                    "from": "start",
                    "label": "go",
                    "to": "end",
                    "namespace": "linear",
                    "display_label": "go",
                }
            ],
            "ltms": [
                {"name": "start", "fqn": "linear.start"},
                {"name": "end", "fqn": "linear.end"},
            ],
        }
    )
    
    # Test payload schema
    ltm = PayloadLTM()
    structure = ltm.as_json()
    
    assert "transitions" in structure
    assert len(structure["transitions"]) == 1
    assert "payload_schema" in structure["transitions"][0]
    
    schema = structure["transitions"][0]["payload_schema"]
    assert schema["title"] == "PayloadModel"
    assert "properties" in schema
    assert "some_kwarg" in schema["properties"]
    assert "other_kwarg" in schema["properties"]
    ltm = NestedLTM()
    ltm.start()
    structure = ltm.as_json()
    assert convert_lists_to_sets(structure) == convert_lists_to_sets(
        {
            "name": "nested",
            "fqn": "nested",
            "init": ["start"],
            "transitions": [
                {
                    "from": "start",
                    "label": "go",
                    "to": "linear",
                    "namespace": "nested",
                    "display_label": "go",
                }
            ],
            "ltms": [
                {"name": "start", "fqn": "nested.start"},
                {
                    "name": "linear",
                    "fqn": "nested.linear",
                    "init": ["start"],
                    "transitions": [
                        {
                            "from": "start",
                            "label": "go",
                            "to": "end",
                            "namespace": "nested.linear",
                            "display_label": "go",
                        }
                    ],
                    "ltms": [
                        {"name": "start", "fqn": "nested.linear.start"},
                        {"name": "end", "fqn": "nested.linear.end"},
                    ],
                },
            ],
        }
    )


def test_snapshots_queues(session):
    ltm = NestedLTM()
    id = ltm.start()

    def remove_item_id(queue):
        return [{key: value for key, value in q.items() if key != "item_id"} for q in queue]

    assert len(ltm._snapshots) == 8
    assert convert_lists_to_sets(
        remove_item_id(ltm._snapshots[1]["execute_queue"])
    ) == convert_lists_to_sets([{"fqn": "nested.start", "payload": None}])
    assert convert_lists_to_sets(
        remove_item_id(ltm._snapshots[1]["transitions_queue"])
    ) == convert_lists_to_sets([])
    assert convert_lists_to_sets(
        remove_item_id(ltm._snapshots[2]["execute_queue"])
    ) == convert_lists_to_sets([])
    assert convert_lists_to_sets(
        remove_item_id(ltm._snapshots[2]["transitions_queue"])
    ) == convert_lists_to_sets(
        [{"label": "go", "params": None, "namespace": "nested", "payload": None}]
    )
    assert convert_lists_to_sets(
        remove_item_id(ltm._snapshots[3]["execute_queue"])
    ) == convert_lists_to_sets([{"fqn": "nested.linear", "payload": None}])
    assert convert_lists_to_sets(
        remove_item_id(ltm._snapshots[3]["transitions_queue"])
    ) == convert_lists_to_sets([])
    assert convert_lists_to_sets(
        remove_item_id(ltm._snapshots[4]["execute_queue"])
    ) == convert_lists_to_sets([{"fqn": "nested.linear.start", "payload": None}])
    assert convert_lists_to_sets(
        remove_item_id(ltm._snapshots[4]["transitions_queue"])
    ) == convert_lists_to_sets([])
    assert convert_lists_to_sets(
        remove_item_id(ltm._snapshots[5]["execute_queue"])
    ) == convert_lists_to_sets([])
    assert convert_lists_to_sets(
        remove_item_id(ltm._snapshots[5]["transitions_queue"])
    ) == convert_lists_to_sets(
        [{"label": "go", "params": None, "namespace": "nested.linear", "payload": None}]
    )
    assert convert_lists_to_sets(
        remove_item_id(ltm._snapshots[6]["execute_queue"])
    ) == convert_lists_to_sets([{"fqn": "nested.linear.end", "payload": None}])
    assert convert_lists_to_sets(
        remove_item_id(ltm._snapshots[6]["transitions_queue"])
    ) == convert_lists_to_sets([])
    assert convert_lists_to_sets(
        remove_item_id(ltm._snapshots[7]["execute_queue"])
    ) == convert_lists_to_sets([])
    assert convert_lists_to_sets(
        remove_item_id(ltm._snapshots[7]["transitions_queue"])
    ) == convert_lists_to_sets([])


class PayloadModel(BaseModel):
    some_kwarg: bool = True
    other_kwarg: bool = False


class PayloadState(LTM):
    name = "payload_state"

    def run(self, payload=None):
        if payload:  # at init there's no payload
            self.update_store(payload)


class PayloadLTM(LTM):
    name = "payload"
    init = [PayloadState]
    transitions = [{"from": PayloadState, "label": "go", "to": PayloadState}]
    transition_payloads = {
        "go": PayloadModel
    }


def test_payload():
    ltm = PayloadLTM()
    ltm.start()

    engine = get_engine()

    engine.transition(ltm, "go", payload={"some_kwarg": True})
    assert ltm.store["payload_state"]["some_kwarg"] == True

    engine.transition(ltm, "go", payload={"other_kwarg": False})

    assert ltm.store["payload_state"]["other_kwarg"] == False


def test_rollback(session):
    ltm = PayloadLTM()
    ltm.start()
    init_store = deepcopy(ltm._store)

    engine = get_engine()

    engine.transition(ltm, "go", payload={"some_kwarg": True})
    middle_store = deepcopy(ltm._store)

    engine.transition(ltm, "go", payload={"other_kwarg": False})


    db = get_db(session)
    ltm_final = db.load_ltm(ltm.id, snapshots=True, rollbacks=True)

    assert len(ltm_final._snapshots) == 7

    # rollback to after first transition/execution
    ltm_rollback = db.rollback(ltm_final, 4)

    # check the same object
    assert len(ltm_rollback._snapshots) == 5
    assert len(ltm_rollback._rollbacks) == 1
    assert ltm_rollback._store == middle_store

    # check a reloaded object
    ltm_rollback1 = db.load_ltm(ltm.id, snapshots=True, rollbacks=True)
    assert len(ltm_rollback1._snapshots) == 5
    assert len(ltm_rollback1._rollbacks) == 1
    assert ltm_rollback1._store == middle_store

    # rollback to after init
    ltm_rollback = db.rollback(ltm_final, 2)

    # check the same object
    assert len(ltm_rollback._snapshots) == 3
    assert len(ltm_rollback._rollbacks) == 2
    assert ltm_rollback._store == init_store

    # check a reloaded object
    ltm_rollback1 = db.load_ltm(ltm.id, snapshots=True, rollbacks=True)
    assert len(ltm_rollback1._snapshots) == 3
    assert len(ltm_rollback1._rollbacks) == 2
    assert ltm_rollback1._store == init_store


def test_recover_rollback(session):
    # create an LTM
    ltm = PayloadLTM()
    ltm.start()
    init_store = deepcopy(ltm._store)

    engine = get_engine()

    # execute "go"
    engine.transition(ltm, "go", payload={"some_kwarg": True})
    middle_store = deepcopy(ltm._store)

    # execute "go" again
    engine.transition(ltm, "go", payload={"other_kwarg": False})


    db = get_db(session)
    ltm_final = db.load_ltm(ltm.id, snapshots=True, rollbacks=True)

    # rollback to after first transition/execution
    db.rollback(ltm_final, 4)

    # rollback to after init
    db.rollback(ltm_final, 2)

    ltm_rollback = db.load_ltm(ltm.id, snapshots=True, rollbacks=True)
    assert len(ltm_rollback._rollbacks) == 2

    db.rollback(ltm_final, rollback_index=0)

    # check a reloaded object
    ltm_rollback = db.load_ltm(ltm.id, snapshots=True, rollbacks=True)
    assert len(ltm_rollback._rollbacks) == 3
    assert ltm_rollback._store == ltm_final._store


def test_replay(session):
    ltm = PayloadLTM()
    ltm.start()

    engine = get_engine()

    engine.transition(ltm, "go", payload={"some_kwarg": True})
    middle_store = deepcopy(ltm._store)


    db = get_db()
    ltm_final = db.load_ltm(ltm.id, snapshots=True, rollbacks=True)

    db.rollback(ltm_final, 3, replay=True)

    ltm_final = db.load_ltm(ltm.id, snapshots=True, rollbacks=True)

    # check the same object
    assert len(ltm_final._snapshots) == 5
    assert len(ltm_final._rollbacks) == 1
    assert ltm_final._store == middle_store

def test_restart(session):


    db = get_db()
    engine = get_engine()

    ltm = PayloadLTM()
    ltm.start()

    ltm_initial = db.load_ltm(ltm.id, snapshots=True, rollbacks=True)
    initial_store = deepcopy(ltm_initial._store)

    engine.transition(ltm, "go", payload={"some_kwarg": True})

    db = get_db()
    ltm_final = db.load_ltm(ltm.id, snapshots=True, rollbacks=True)

    db.rollback(ltm_final, 0, replay=True)

    ltm_restart = db.load_ltm(ltm.id, snapshots=True, rollbacks=True)

    # check the same object
    assert len(ltm_restart._snapshots) == len(ltm_initial._snapshots)
    assert len(ltm_restart._rollbacks) == 1

    assert ltm_restart._store == initial_store


### Test that store with None as value doesn't break transition
class Child1(LTM):
    name = "child1"


class Child2(LTM):
    name = "child2"


class RootWithNone(LTM):
    name = "root_with_none"
    init = [Child1, Child2]

    transitions = [{"from": Child1, "label": "go", "to": Child2}]

    def get_initial_store(self):
        initial_store = super().get_initial_store()
        initial_store["test"] = None
        return initial_store

def test_store_none_transition(session):
    root = RootWithNone()
    root.start()

    engine = get_engine()

    engine.transition(root, "go")

    assert root.store["test"] == None