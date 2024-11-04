import pytest

from flou.database import get_db
from flou.ltm import LTM


class MyLTM(LTM):

    name = "root"

    def get_initial_state(self):
        initial_state = super().get_initial_state()
        initial_state["my_list"] = []
        return initial_state


def test_atomic_update(session):

    root = MyLTM()
    id = root.start()
    root.atomic_state_append("my_list", "first")
    root.atomic_state_append("my_list", "second")

    assert root.state["my_list"] == ["first", "second"]


def test_copy(session):

    root = MyLTM()
    id = root.start()

    db = get_db(session)

    copy_id = db.copy_ltm(id)

    root = db.load_ltm(id, snapshots=True, rollbacks=True, playground=True)
    copy = db.load_ltm(copy_id, snapshots=True, rollbacks=True, playground=True)

    assert copy.id != root.id
    assert copy._playground == True
    assert copy._source_id == root.id
    assert copy.name == root.name
    assert copy.fqn == root.fqn
    assert copy.params == root.params
    assert copy._state == root._state
    assert copy._snapshots == root._snapshots
    assert copy._rollbacks == root._rollbacks
    assert copy.created_at == root.created_at
    assert copy.updated_at == root.updated_at