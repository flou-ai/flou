from ..utils import convert_lists_to_sets
from flou.ltm import LTM


# Test a concurrent sub ltm


class Noop(LTM):
    name = "noop"


class ConcurrentSubLTM(LTM):
    name = "sub_ltm_{num}"

    init = [Noop]


class ConcurrentSubRootLTM(LTM):
    name = "concurrent_sub_root"

    init = [Noop]

    transitions = [{"from": Noop, "label": "start_{num}", "to": ConcurrentSubLTM}]


def test_concurrent_sub_ltm(session):

    root = ConcurrentSubRootLTM()
    root.start()

    from flou.database import get_db

    db = get_db(session)

    from flou.engine import get_engine

    engine = get_engine()
    engine.transition(root, "start_{num}", params=[{"num": "1"}, {"num": "2"}])

    doneLTM = db.load_ltm(root.id, snapshots=True)

    assert len(doneLTM._snapshots) == 8
    assert doneLTM._state["sub_ltm_1"] == {
        "_status": "active",
        "noop": {"_status": "active"},
    }
    assert doneLTM._state["sub_ltm_2"] == {
        "_status": "active",
        "noop": {"_status": "active"},
    }


# test two sub LTMs that are launched concurrently


class ToDoneConcurrentState(LTM):
    name = "to_done"

    def run(self, payload=None):
        self.parent.transition(
            "done_{num}", params=[self.parent.params], payload=self.parent.params
        )


class MultipleConcurrentSubLTM(LTM):
    name = "sub_ltm_{num}"

    init = [ToDoneConcurrentState]


class WaitForAllStates(LTM):
    name = "wait_for_all"

    def get_initial_state(self):
        initial = super().get_initial_state()
        initial["done"] = []
        return initial

    def run(self, payload=None):
        done = self.atomic_state_append("done", payload)
        if convert_lists_to_sets(done) == convert_lists_to_sets(
            self.parent.launch_params
        ):
            self.transition("done_all")


class MultipleConcurrentSubRootLTM(LTM):

    name = "concurrent_sub_root"

    init = [Noop]

    launch_params = [{"num": "1"}, {"num": "2"}]

    transitions = [
        {"from": Noop, "label": "start_{num}", "to": MultipleConcurrentSubLTM},
        {
            "from": MultipleConcurrentSubLTM,
            "label": "done_{num}",
            "to": WaitForAllStates,
        },
        {"from": WaitForAllStates, "label": "done_all", "to": Noop},
    ]


def test_multiple_concurrent_sub_ltm(session):

    root = MultipleConcurrentSubRootLTM()
    root.start()

    from flou.database import get_db

    db = get_db(session)

    from flou.engine import get_engine

    engine = get_engine()
    engine.transition(root, "start_{num}", params=[{"num": "1"}, {"num": "2"}])

    doneLTM = db.load_ltm(root.id, snapshots=True)

    assert convert_lists_to_sets(doneLTM._state) == convert_lists_to_sets(
        {
            "_status": "active",
            "noop": {"_status": "active"},
            "sub_ltm_1": {"_status": "finished", "to_done": {"_status": "active"}},
            "sub_ltm_2": {"_status": "finished", "to_done": {"_status": "active"}},
            "wait_for_all": {
                "_status": "finished",
                "done": [{"num": "2"}, {"num": "1"}],
            },
        }
    )


# Now test nesting, with one extra level


class MultipleConcurrentSubNestedLTM(LTM):

    name = "concurrent_sub_nested_{num}"

    init = [Noop]

    launch_params = [{"num": "1"}, {"num": "2"}]

    transitions = [
        {"from": Noop, "label": "start_{num}", "to": MultipleConcurrentSubLTM},
        {
            "from": MultipleConcurrentSubLTM,
            "label": "done_{num}",
            "to": WaitForAllStates,
        },
        {"from": WaitForAllStates, "label": "done_all", "to": Noop},
    ]


class MultipleConcurrentSubNestedRootLTM(LTM):

    name = "concurrent_sub_nested_root"

    init = [Noop]

    launch_params = [{"num": "1"}, {"num": "2"}]

    transitions = [
        {"from": Noop, "label": "start_{num}", "to": MultipleConcurrentSubNestedLTM},
        {
            "from": MultipleConcurrentSubNestedLTM,
            "label": "done_{num}",
            "to": WaitForAllStates,
        },
        {"from": WaitForAllStates, "label": "done_all", "to": ToDoneConcurrentState},
    ]


def test_multiple_concurrent_sub_nested_ltm(session):

    root = MultipleConcurrentSubNestedRootLTM()
    root.start()

    from flou.database import get_db

    db = get_db(session)

    from flou.engine import get_engine

    engine = get_engine()
    engine.transition(root, "start_{num}", params=[{"num": "1"}, {"num": "2"}])

    doneLTM = db.load_ltm(root.id, snapshots=True)
    engine.transition(
        doneLTM,
        "start_{num}",
        params=[{"num": "1"}, {"num": "2"}],
        namespace="concurrent_sub_nested_root.concurrent_sub_nested_1",
    )

    doneLTM = db.load_ltm(root.id, snapshots=True)
    engine.transition(
        doneLTM,
        "start_{num}",
        params=[{"num": "1"}, {"num": "2"}],
        namespace="concurrent_sub_nested_root.concurrent_sub_nested_2",
    )

    assert len(doneLTM._snapshots) == 30
    assert convert_lists_to_sets(doneLTM._state) == convert_lists_to_sets(
        {
            "_status": "active",
            "concurrent_sub_nested_1": {
                "_status": "active",
                "noop": {"_status": "active"},
                "sub_ltm_1": {"_status": "finished", "to_done": {"_status": "active"}},
                "sub_ltm_2": {"_status": "finished", "to_done": {"_status": "active"}},
                "wait_for_all": {
                    "_status": "finished",
                    "done": [{"num": "2"}, {"num": "1"}],
                },
            },
            "concurrent_sub_nested_2": {
                "_status": "active",
                "noop": {"_status": "active"},
                "sub_ltm_1": {"_status": "finished", "to_done": {"_status": "active"}},
                "sub_ltm_2": {"_status": "finished", "to_done": {"_status": "active"}},
                "wait_for_all": {
                    "_status": "finished",
                    "done": [{"num": "2"}, {"num": "1"}],
                },
            },
            "noop": {"_status": "finished"},
            "to_done": {"_status": "init"},
            "wait_for_all": {"_status": "init", "done": []},
        }
    )


def test_concurrent_instances_as_json(session):

    root = MultipleConcurrentSubNestedRootLTM()
    root.start()

    from flou.database import get_db

    db = get_db(session)
    from flou.engine import get_engine

    engine = get_engine()
    engine.transition(root, "start_{num}", params=[{"num": "1"}, {"num": "2"}])

    engine.transition(
        root,
        "start_{num}",
        params=[{"num": "1"}, {"num": "2"}],
        namespace="concurrent_sub_nested_root.concurrent_sub_nested_1",
    )

    engine.transition(
        root,
        "start_{num}",
        params=[{"num": "1"}, {"num": "2"}],
        namespace="concurrent_sub_nested_root.concurrent_sub_nested_2",
    )

    assert convert_lists_to_sets(
        root.concurrent_instances_as_json()
    ) == convert_lists_to_sets(
        {
            "concurrent_sub_nested_root.concurrent_sub_nested_{num}": [
                {
                    "fname": "concurrent_sub_nested_1",
                    "fqn": "concurrent_sub_nested_root.concurrent_sub_nested_1",
                    "structure_fqn": "concurrent_sub_nested_root.concurrent_sub_nested_{num}",
                    "params": {"num": "1"},
                },
                {
                    "fname": "concurrent_sub_nested_2",
                    "fqn": "concurrent_sub_nested_root.concurrent_sub_nested_2",
                    "structure_fqn": "concurrent_sub_nested_root.concurrent_sub_nested_{num}",
                    "params": {"num": "2"},
                },
            ],
            "concurrent_sub_nested_root.concurrent_sub_nested_{num}.sub_ltm_{num}": [
                {
                    "fname": "sub_ltm_1",
                    "fqn": "concurrent_sub_nested_root.concurrent_sub_nested_1.sub_ltm_1",
                    "structure_fqn": "concurrent_sub_nested_root.concurrent_sub_nested_{num}.sub_ltm_{num}",
                    "params": {"num": "1"},
                },
                {
                    "fname": "sub_ltm_2",
                    "fqn": "concurrent_sub_nested_root.concurrent_sub_nested_1.sub_ltm_2",
                    "structure_fqn": "concurrent_sub_nested_root.concurrent_sub_nested_{num}.sub_ltm_{num}",
                    "params": {"num": "2"},
                },
                {
                    "fname": "sub_ltm_1",
                    "fqn": "concurrent_sub_nested_root.concurrent_sub_nested_2.sub_ltm_1",
                    "structure_fqn": "concurrent_sub_nested_root.concurrent_sub_nested_{num}.sub_ltm_{num}",
                    "params": {"num": "1"},
                },
                {
                    "fname": "sub_ltm_2",
                    "fqn": "concurrent_sub_nested_root.concurrent_sub_nested_2.sub_ltm_2",
                    "structure_fqn": "concurrent_sub_nested_root.concurrent_sub_nested_{num}.sub_ltm_{num}",
                    "params": {"num": "2"},
                },
            ]
        }
    )