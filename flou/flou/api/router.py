from datetime import datetime
import asyncio
import json
from typing import List

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query, Path
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import select, update


from flou.conf import settings
from flou.database import get_db, get_session
from flou.database.models import Error
from flou.engine import get_engine
from flou.api.dependencies import get_redis
from flou.registry import registry

router = APIRouter()


@router.get("/example")
def read_example():
    return {
        "message": "Hello, World!",
        "engine": settings.old_database.engine,
    }




class LTM(BaseModel):
    id: int
    name: str
    fqn: str
    snapshots_count: int
    created_at: datetime
    updated_at: datetime


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


class LTMCreation(BaseModel):
    fqn: str = Field(..., description="Fully qualified name of the LTM class")
    payload: dict = Field({}, description="Initial payload as a json object")
    playground: bool = Field(
        False, description="If true, the LTM will be created in the playground"
    )


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
    with get_session() as session:
        data["errors"] = session.scalars(
            select(Error).where(Error.ltm_id == ltm_id)
        ).all()
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


class Transition(BaseModel):
    transition: str = Field(..., description="The label of the transition to perform")
    namespace: str = Field(..., description="The namespace of the transition")
    params: list[dict] | None = Field(
        None, description="If a parameterized transition, it's parameters"
    )
    payload: dict | None = Field(
        None, description="Optional payload for the transition"
    )
    wait_until_transition: str | None = Field(
        None,
        description="Await return until this transition `namespace:label` executes",
    )


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
    if transition.wait_until_transition:
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


class SnapshotIndex(BaseModel):
    index: int = Field(..., description="The index of the desired snapshot")


@router.post("/ltm/{ltm_id}/rollback")
async def rollback(
    snapshot: SnapshotIndex, ltm_id: int = Path(..., description="The LTM instance id")
):
    """
    Rollback to a previous snapshot
    """
    db = get_db()
    ltm = db.load_ltm(ltm_id, snapshots=True)
    db.rollback(ltm, snapshot.index, reason="manual")
    return True


@router.post("/ltm/{ltm_id}/replay")
async def replay(
    snapshot: SnapshotIndex, ltm_id: int = Path(..., description="The LTM instance id")
):
    """
    Rollback to a previous transition snapshot and replay the transition
    """
    db = get_db()
    ltm = db.load_ltm(ltm_id, snapshots=True)
    db.replay(ltm, snapshot.index)
    return True


class RollbackIndex(BaseModel):
    index: int = Field(..., description="The index of the desired rollback")


@router.post("/ltm/{ltm_id}/recover-rollback")
async def rollback(
    rollback: RollbackIndex, ltm_id: int = Path(..., description="The LTM instance id")
):
    """
    Undo a rollback
    """
    db = get_db()
    ltm = db.load_ltm(ltm_id, snapshots=True)
    db.rollback(ltm, rollback_index=rollback.index, reason="recover rollback")
    return True


class ErrorList(BaseModel):
    ids: List[str] = Field(..., description="The errors UUIDs to retry")


@router.post("/ltm/{ltm_id}/retry")
async def retry(
     error_list: ErrorList, ltm_id: int = Path(..., description="The LTM instance id")
):
    """
    Retries a failed execution/transition
    """
    for id in error_list.ids:
        with get_session() as session:
            error = session.get(Error, id)

        engine = get_engine()

        item = error.item
        item.pop("item_id", None)

        with get_session() as session:
            session.execute(update(Error).where(Error.id == id).values(retrying=True))
            session.commit()

        if error.reason == "execute":
            engine.execute(error.ltm_id, item_id=error.id, **error.item)
        elif error.reason == "transition":
            engine.transition(error.ltm_id, item_id=error.id, **error.item)
        else:
            raise ValueError

    return True
