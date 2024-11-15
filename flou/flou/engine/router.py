from datetime import datetime
import asyncio
import json
from typing import List

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query, Path
from sqlalchemy import select, update


from flou.conf import settings
from flou.database import get_db, get_session
from flou.engine import get_engine
from flou.api.dependencies import get_redis
from flou.engine.schemas import (
    LTM,
    LTMCreation,
    Transition,
    Rollback,
    RollbackIndex,
    ErrorList,
)
from flou.experiments.models import Trial
from flou.experiments.schemas import AddTrial

from flou.engine.models import Error
from flou.registry import registry

router = APIRouter()


@router.get("/ltm", response_model=List[LTM])
async def list_ltms(
    playground: bool = Query(
        False, description="Switches between production and playground LTMs"
    )
):
    """
    Lists all LTM instances.

    Returns the id, name, fqn, snapshots count and creation and updated dates of
    each LTM.
    """
    db = get_db()
    return db.list_ltms(playground=playground)


@router.get("/ltm/registry")
async def list_registered_ltms():
    """
    Lists all registered LTMs

    Returns the fqn and name of each LTM.
    """
    return [
        {
            "fqn": ltm.get_class_fqn(),
            "name": ltm.name,
        }
        for ltm in registry.get_ltms()
    ]


@router.post("/ltm")
async def create_ltm(ltm_creation: LTMCreation):
    """
    Creates a new LTM instance
    """
    db = get_db()
    ltm = db.get_ltm_class(ltm_creation.fqn)()
    id = ltm.start(payload=ltm_creation.payload, playground=ltm_creation.playground)
    return {"id": id}


@router.get("/ltm/{ltm_id}")
async def get_ltm(
    ltm_id: int = Path(..., description="The LTM instance id"),
    rollbacks: bool = Query(False, description="Include rollbacks"),
    session=Depends(get_session),
):
    """
    Get an LTM instance's data
    """
    db = get_db()
    ltm = db.load_ltm(ltm_id, snapshots=True, rollbacks=rollbacks)
    data = {
        "name": ltm.name,
        "state": ltm._state,
        "snapshots": ltm._snapshots,
        "fqn": ltm.get_class_fqn(),
        "params": ltm.params,
        "structure": ltm.as_json(structure=True),
        "concurrent_instances": ltm.concurrent_instances_as_json(),
        "created_at": ltm.created_at,
        "updated_at": ltm.updated_at,
    }
    if rollbacks:
        data["rollbacks"] = ltm._rollbacks

    # gather the errors
    data["errors"] = session.scalars(select(Error).where(Error.ltm_id == ltm_id)).all()

    # Check if any trials reference this LTM and get experiment ID
    current_trial = session.scalar(select(Trial).where(Trial.ltm_id == ltm_id).order_by(Trial.created_at.desc()).limit(1))
    if current_trial:
        data["experiment_id"] = current_trial.experiment_id
        data["current_trial"] = current_trial

    return data


@router.post("/ltm/{ltm_id}/copy")
async def copy_ltm(ltm_id: int = Path(..., description="The LTM instance id")):
    """
    Copy an LTM instance to use in the playground
    """
    db = get_db()
    copy_id = db.copy_ltm(ltm_id)
    return {
        "copy_id": copy_id,
    }


@router.post("/ltm/{ltm_id}/transition")
async def transition(
    transition: Transition,
    ltm_id: int = Path(..., description="The LTM instance id"),
    redis=Depends(get_redis),
):
    """
    Perform a transition
    """
    engine = get_engine()
    db = get_db()
    ltm = db.load_ltm(ltm_id)
    engine.transition(
        ltm,
        transition.transition,
        params=transition.params,
        namespace=transition.namespace,
        payload=transition.payload,
    )

    # wait until another transition is completed
    .storieiif transition.wait_until_transition:
        wait_namespace, wait_label = transition.wait_until_transition.split(":")
        try:
            async with redis.pubsub() as pubsub:
                await pubsub.subscribe(f"ltm:{ltm.id}:transition")

                async for message in pubsub.listen():
                    if message["type"] == "message":
                        data = json.loads(message["data"])
                        item = data["snapshot"]["item"]

                        # check for matching namespace
                        if wait_namespace != item["namespace"]:
                            continue

                        if wait_label != item["label"]:
                            continue

                        # check for matching label (with params)
                        label_match = False
                        if item["params"]:
                            for param in item["params"]:
                                if wait_label == item["label"].format(**param):
                                    label_match = True
                        else:
                            label_match = True

                        if label_match:
                            return True
        except asyncio.CancelledError:
            return False

    return True


@router.websocket("/ws/{ltm_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    ltm_id: int = Path(..., description="The LTM instance id"),
    redis=Depends(get_redis),
):
    """
    Websocket endpoint to listen to LTM updates

    Subscribes to the LTM transitions and execution sending each corresponding
    snapshot.
    """
    await websocket.accept()
    try:
        async with redis.pubsub() as pubsub:
            await pubsub.psubscribe(f"ltm:{ltm_id}:*")
            async for message in pubsub.listen():
                if message["type"] == "pmessage":
                    await websocket.send_json(json.loads(message["data"]))
    except WebSocketDisconnect:
        print("websocket disconnect")
        pass
    except asyncio.CancelledError:
        print("cancelled")
        pass
    finally:
        print("finally")


@router.post("/ltm/{ltm_id}/rollback")
async def rollback(
    snapshot: Rollback | None = None,
    rollback: RollbackIndex | None = None,
    new_trial: AddTrial | None = None,
    ltm_id: int = Path(..., description="The LTM instance id"),
    session=Depends(get_session),
):
    """
    Rollback to a previous snapshot.

    If the LTM is part of a trial, a new trial is created
    """
    db = get_db()
    ltm = db.load_ltm(ltm_id, snapshots=True)
    rollback_args = {
       "ltm": ltm,
    }
    if snapshot:
        rollback_args["snapshot_index"] = snapshot.index
        rollback_args["replay"] = snapshot.replay
        rollback_args["reason"] = "replay" if snapshot.replay else "manual"
    elif rollback:
        rollback_args["rollback_index"] = rollback.index
        rollback_args["reason"] = "recover rollback"

    ltm = db.rollback(**rollback_args)

    trial = (
        session.query(Trial)
        .filter(Trial.ltm_id == ltm_id)
        .order_by(Trial.created_at.desc())
        .first()
    )

    result = {"success": True}

    if trial:
        if new_trial and new_trial.previous_trial_outputs:
            trial.outputs = new_trial.previous_trial_outputs
            session.add(trial)

        # Create new trial with same name and experiment
        new_trial = Trial(
            experiment_id=trial.experiment_id,
            ltm_id=trial.ltm_id,
            **new_trial.model_dump(include={"inputs"}),
            name=new_trial.name or trial.name,
            rollback_index=len(ltm._rollbacks or []),  # this rollback doesn't exist yet
            snapshot_index=snapshot.index if snapshot else 0,
        )
        session.add(new_trial)
        session.commit()

        result["trial"] = new_trial

    return result


@router.post("/ltm/{ltm_id}/retry")
async def retry(
    error_list: ErrorList,
    ltm_id: int = Path(..., description="The LTM instance id"),
    session=Depends(get_session),
):
    """
    Retries a failed execution/transition
    """
    for id in error_list.ids:
        error = session.get(Error, id)

        engine = get_engine()

        item = error.item
        item.pop("item_id", None)

        session.execute(update(Error).where(Error.id == id).values(retrying=True))
        session.commit()

        if error.reason == "execute":
            engine.execute(error.ltm_id, item_id=error.id, **error.item)
        elif error.reason == "transition":
            engine.transition(error.ltm_id, item_id=error.id, **error.item)
        else:
            raise ValueError

    return True
