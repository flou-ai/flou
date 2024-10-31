from flou.ltm import LTM
from .utils import convert_lists_to_sets


class Noop(LTM):
    name = "noop"


class Noop2(LTM):
    name = "noop2"


class Child1(LTM):
    name = "child1"
    init = [Noop]

    transitions = [{"from": Noop, "label": "start", "to": Noop2, "namespace": "global"}]


class Child2(LTM):
    name = "child2"
    init = [Noop]

    transitions = [{"from": Noop, "label": "start", "to": Noop2, "namespace": "global"}]


class Root(LTM):
    name = "root"
    init = [Child1, Child2]


def test_namespaces():
    root = Root()
    root.start()

    from flou.executor import get_executor

    executor = get_executor()

    executor.transition(root, "start", namespace="global")

    from flou.database import get_db

    db = get_db()
    doneLTM = db.load_ltm(root.id, snapshots=True)

    assert convert_lists_to_sets(doneLTM._state) == convert_lists_to_sets(
        {
            "_status": "active",
            "child1": {
                "_status": "active",
                "noop": {"_status": "finished"},
                "noop2": {"_status": "active"},
            },
            "child2": {
                "_status": "active",
                "noop": {"_status": "finished"},
                "noop2": {"_status": "active"},
            },
        }
    )
