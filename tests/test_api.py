import pytest
from flou.database import get_db
from flou.conf import Executor
from fastapi.testclient import TestClient
from flou.api.main import app
from flou.conf import Database
from flou.registry import registry

client = TestClient(app)


def test_list(session):
    from .test_ltm import PayloadLTM
    ltm = PayloadLTM()
    id = ltm.start()

    response = client.get("/api/v0/ltm")

    db = get_db()
    copy_id = db.copy_ltm(id)
    copy = db.load_ltm(copy_id)

    # check that we have the original one but not the copy
    assert response.status_code == 200
    assert id in [ltm['id'] for ltm in response.json()]
    assert copy_id not in [ltm['id'] for ltm in response.json()]

    response = client.get("/api/v0/ltm?playground=true")

    # check that we have the copy but not the original one
    assert response.status_code == 200
    assert id not in [ltm['id'] for ltm in response.json()]
    assert copy_id in [ltm['id'] for ltm in response.json()]

def test_register(session):

    from tests.test_ltm import Root
    registry._registry = []
    registry.register(Root)

    response = client.get("/api/v0/ltm/registry")

    assert response.status_code == 200
    assert response.json() == [{"fqn": "tests.test_ltm.Root", "name": "root"}]


def test_create_ltm(session):
    ltm_creation_data = {
        "fqn": "tests.test_ltm.Root",
        # "kwargs": {"some": "data"}
    }
    response = client.post("/api/v0/ltm", json=ltm_creation_data)
    assert response.status_code == 200

    id = response.json()['id']
    from flou.database import get_db
    db = get_db(session)
    assert db.load_ltm(id).id == id


def test_copy_ltm(session):
    from .test_ltm import PayloadLTM
    ltm = PayloadLTM()
    id = ltm.start()

    response = client.post(f"/api/v0/ltm/{id}/copy")
    assert response.status_code == 200

    copy_id = response.json()['copy_id']
    from flou.database import get_db
    db = get_db(session)
    copy = db.load_ltm(copy_id, playground=True)
    assert copy._source_id == id


def test_transition(session):
    from .test_ltm import PayloadLTM
    ltm = PayloadLTM()
    id = ltm.start()

    transition_data = {
        "transition": "go",
        "namespace": "payload",
        "payload": {"some": "data"}
    }
    response = client.post(f"/api/v0/ltm/{ltm.id}/transition", json=transition_data)
    assert response.status_code == 200

    assert response.json() == True
    from flou.database import get_db
    db = get_db(session)
    loaded_ltm = db.load_ltm(id)
    assert loaded_ltm._get_ltm("payload.payload_state").state["some"] == "data"


def test_rollback(session):
    from .test_ltm import PayloadLTM
    ltm = PayloadLTM()
    id = ltm.start()

    from flou.executor import get_executor
    executor = get_executor()
    executor.transition(ltm, "go", payload={"some_kwarg": True})

    rollback_data = {
        "index": 2,
    }
    response = client.post(f"/api/v0/ltm/{ltm.id}/rollback", json=rollback_data)
    assert response.status_code == 200
    assert response.json() == True

    from flou.database import get_db
    db = get_db(session)
    loaded_ltm = db.load_ltm(id, snapshots=True, rollbacks=True)
    assert len(loaded_ltm._snapshots) == 3
    assert len(loaded_ltm._rollbacks) == 1


def test_replay(session):
    from .test_ltm import PayloadLTM
    ltm = PayloadLTM()
    id = ltm.start()

    from flou.executor import get_executor
    executor = get_executor()
    executor.transition(ltm, "go", payload={"some_kwarg": True})

    replay_data = {
        "index": 3,
    }
    response = client.post(f"/api/v0/ltm/{ltm.id}/replay", json=replay_data)
    assert response.status_code == 200
    assert response.json() == True

    from flou.database import get_db
    db = get_db(session)
    loaded_ltm = db.load_ltm(id, snapshots=True, rollbacks=True)
    assert len(loaded_ltm._snapshots) == 5
    assert len(loaded_ltm._rollbacks) == 1