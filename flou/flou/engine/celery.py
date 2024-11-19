import json
import logging
import os
import sys
import uuid

from celery import Celery

from flou.database import get_db, get_db
from flou.conf import settings, Engine
from flou.ltm import LTM
from .base import BaseEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# add your path to the sys path so we can `import_module` from the path celery is being called
sys.path.append(os.getcwd())

app = Celery("flou")

# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object(settings.engine)

# Load task modules from celery
app.autodiscover_tasks(["flou.engine.celery"], force=True)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    logger.info(f"Request: {self.request!r}")


@app.task(
    name="execute",
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": settings.engine.max_retries},
    retry_backoff=True,
)
def execute(ltm_id, item_id, fqn, payload=None):
    logger.info(f">>> execute: {ltm_id} {fqn}, payload: {payload}")

    try:
        from flou.engine import get_engine

        engine = get_engine()
        db = get_db()
        root = db.load_ltm(ltm_id)
        ltm = root._get_ltm(fqn)

        # run the state directly with no celery override
        ltm.run(payload)

        # update the state to executed
        ltm.update_state({"_status": "active"})

        # update the db state with all updates at once
        db.update_state(
            ltm,
            "execute",
            item={"item_id": item_id, "fqn": ltm.fqn, "payload": payload},
        )

        engine.consume_queues(ltm)
    except Exception as e:
        get_db().log_retry(
            item_id, ltm_id, "execute", {"fqn": fqn, "payload": payload}, e
        )
        raise e
    else:
        get_db().set_success(item_id)


@app.task(
    name="transition",
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": settings.engine.max_retries},
    retry_backoff=True,
)
def transition(ltm_id, item_id, label, params=None, namespace=None, payload=None):
    logger.info(
        f">>> transition: {ltm_id}, label: {label},  params: {params}, namespace: {namespace}, payload: {payload}"
    )
    try:
        from flou.engine import get_engine

        engine = get_engine()
        db = get_db()
        ltm = db.load_ltm(ltm_id)

        if not namespace:
            namespace = ltm.root.name

        ltm.perform_transition(label, params, namespace, payload)

        # update the db state with all updates at once
        db.update_state(
            ltm,
            "transition",
            item={
                "item_id": item_id,
                "label": label,
                "params": params,
                "namespace": namespace,
                "payload": payload,
            },
        )

        engine.consume_queues(ltm)
    except Exception as e:
        get_db().log_retry(
            item_id,
            ltm_id,
            "transition",
            {
                "label": label,
                "params": params,
                "namespace": namespace,
                "payload": payload,
            },
            e,
        )
        raise e
    else:
        get_db().set_success(item_id)


@app.task
def error_handler(request, exc, traceback):
    """
    Set the Error to not retrying anymore

    This function get's called after the last retry failed
    """
    get_db().set_stop_retrying(request.kwargs["item_id"])


class CeleryEngine(BaseEngine):
    def execute(self, ltm, fqn, payload=None, item_id=None):
        if isinstance(ltm, LTM):
            ltm_id = ltm.root.id
        else:
            ltm_id = ltm
        if not item_id:
            item_id = uuid.uuid4()
        return execute.apply_async(
            args=[ltm_id],
            kwargs={"item_id": item_id, "fqn": fqn, "payload": payload},
            link_error=error_handler.s(),
        )

    def transition(
        self, ltm, label, params=None, namespace=None, payload=None, item_id=None
    ):
        if isinstance(ltm, LTM):
            ltm_id = ltm.root.id
        else:
            ltm_id = ltm
        if not item_id:
            item_id = uuid.uuid4()
        return transition.apply_async(
            args=[ltm_id],
            kwargs={
                "item_id": item_id,
                "label": label,
                "params": params,
                "namespace": namespace,
                "payload": payload,
            },
            link_error=error_handler.s(),
        )

    def start(self, ltm_id, payload=None, params=False, playground=False):
        id = get_db().create_ltm(
            ltm_id, payload, params=params, playground=playground
        )
        return id
