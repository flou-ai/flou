import pytest
from flou.database import get_db
from fastapi.testclient import TestClient
from flou.api.main import app
from flou.registry import registry
from .test_ltm import PayloadLTM
from flou.experiments.models import Experiment, Trial

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
    assert id in [ltm["id"] for ltm in response.json()]
    assert copy_id not in [ltm["id"] for ltm in response.json()]

    response = client.get("/api/v0/ltm?playground=true")

    # check that we have the copy but not the original one
    assert response.status_code == 200
    assert id not in [ltm["id"] for ltm in response.json()]
    assert copy_id in [ltm["id"] for ltm in response.json()]


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

    id = response.json()["id"]
    from flou.database import get_db

    db = get_db(session)
    assert db.load_ltm(id).id == id


def test_copy_ltm(session):
    from .test_ltm import PayloadLTM

    ltm = PayloadLTM()
    id = ltm.start()

    response = client.post(f"/api/v0/ltm/{id}/copy")
    assert response.status_code == 200

    copy_id = response.json()["copy_id"]
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
        "payload": {"some": "data"},
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

    from flou.engine import get_engine

    engine = get_engine()
    engine.transition(ltm, "go", payload={"some_kwarg": True})

    rollback_data = {
        "snapshot": {
            "index": 2,
        },
    }
    response = client.post(f"/api/v0/ltm/{ltm.id}/rollback", json=rollback_data)
    assert response.status_code == 200
    assert response.json() == {"success": True}

    from flou.database import get_db

    db = get_db(session)
    loaded_ltm = db.load_ltm(id, snapshots=True, rollbacks=True)
    assert len(loaded_ltm._snapshots) == 3
    assert len(loaded_ltm._rollbacks) == 1


def test_replay(session):
    from .test_ltm import PayloadLTM

    ltm = PayloadLTM()
    id = ltm.start()

    from flou.engine import get_engine

    engine = get_engine()
    engine.transition(ltm, "go", payload={"some_kwarg": True})

    replay_data = {
        "snapshot": {
            "index": 3,
            "replay": True,
        },
    }
    response = client.post(f"/api/v0/ltm/{ltm.id}/rollback", json=replay_data)
    assert response.status_code == 200
    assert response.json() == {"success": True}

    from flou.database import get_db

    db = get_db(session)
    loaded_ltm = db.load_ltm(id, snapshots=True, rollbacks=True)
    assert len(loaded_ltm._snapshots) == 5
    assert len(loaded_ltm._rollbacks) == 1


def test_list_experiments(session):
    experiment1 = Experiment(name="Experiment 1", description="First experiment")
    experiment2 = Experiment(name="Experiment 2", description="Second experiment")
    session.add(experiment1)
    session.add(experiment2)
    session.commit()

    response = client.get("/api/v0/experiments")
    assert response.status_code == 200
    experiments = response.json()
    assert isinstance(experiments, list)
    assert len(experiments) >= 2
    assert any(exp["name"] == "Experiment 1" for exp in experiments)
    assert any(exp["name"] == "Experiment 2" for exp in experiments)


def test_create_experiment(session):
    experiment_creation_data = {
        "name": "New Experiment",
        "description": "A test experiment",
        "trial": {
            "name": "Initial Trial",
            "fqn": "tests.test_ltm.Root",
        },
    }

    response = client.post("/api/v0/experiments", json=experiment_creation_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"]


def test_rollback_trial(session):
    # Create experiment and get initial trial
    from .test_ltm import PayloadLTM

    ltm = PayloadLTM()
    ltm.start()
    trial = Trial(name="Initial Trial", ltm_id=ltm.id, rollback_index=0, snapshot_index=0)
    experiment = Experiment(
        name="Test Experiment", description="Test experiment for rollback"
    )
    experiment.trials.append(trial)
    session.add(experiment)
    session.flush()

    from flou.engine import get_engine

    engine = get_engine()
    engine.transition(ltm, "go", payload={"some": "data"})

    # Perform rollback
    rollback_data = {
        "snapshot": {
            "index": 2,
        },
        "new_trial": {
            "name": "New Trial 2",
            "previous_trial_outputs": {},
            "inputs": {},
        },
    }
    response = client.post(f"/api/v0/ltm/{ltm.id}/rollback", json=rollback_data)
    print(response.json())
    assert response.status_code == 200

    # Verify trials state
    trials = (
        session.query(Trial)
        .filter(Trial.experiment_id == experiment.id)
        .order_by(Trial.created_at)
        .all()
    )
    assert len(trials) == 2

    assert trials[0].outputs == rollback_data["new_trial"]["previous_trial_outputs"]
    assert trials[0].rollback_index == 0

    # Check new trial properties
    assert trials[1].ltm_id == ltm.id
    assert trials[1].experiment_id == trial.experiment_id
    assert trials[1].name == rollback_data["new_trial"]["name"]
    assert trials[1].rollback_index == 1
    assert trials[1].snapshot_index == 2


def test_create_trial(session):
    # First create an experiment
    experiment = Experiment(name="Test Experiment", description="Test experiment")
    session.add(experiment)
    session.commit()

    # Create trial data
    trial_creation_data = {
        "name": "New Trial",
        "fqn": "tests.test_ltm.Root",
    }

    response = client.post(f"/api/v0/experiments/{experiment.id}/trials", json=trial_creation_data)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data

    # Verify trial was created correctly
    trials = session.query(Trial).filter(Trial.experiment_id == experiment.id).all()
    assert len(trials) == 1
    assert trials[0].name == "New Trial"
    assert trials[0].ltm_id == data["id"]
