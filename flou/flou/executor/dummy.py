import logging
import uuid

from flou.database import get_db, get_db
from .base import BaseExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DummyExecutor(BaseExecutor):
    # TODO: change execution and transition to be in a FIFO queue

    def execute(self, ltm, fqn, payload=None, item_id=None):
        logger.info(f">>> execute: {ltm.root.id} {fqn}, payload: {payload}")
        try:
            if not item_id:
                item_id = uuid.uuid4()

            from flou.executor import get_executor

            db = get_db()
            executor = get_executor()

            ltm = ltm.root._get_ltm(fqn)
            ltm.run(payload)

            ltm.update_state({"_status": "active"})
            db.update_state(
                ltm,
                "execute",
                item={"item_id": item_id, "fqn": ltm.fqn, "payload": payload},
            )

            executor.consume_queues(ltm)
        except Exception as e:
            get_db().log_retry(
                item_id,
                ltm.root.id,
                "execute",
                {"fqn": fqn, "payload": payload},
                e,
                retrying=False,
            )
            raise e

    def transition(
        self, ltm, label, params=None, namespace=None, payload=None, item_id=None
    ):
        logger.info(
            f">>> transition: {ltm.root.id}, label: {label},  params: {params}, namespace: {namespace}, payload: {payload}"
        )
        try:
            if not item_id:
                item_id = uuid.uuid4()

            from flou.executor import get_executor

            executor = get_executor()
            db = get_db()

            if not namespace:
                namespace = ltm.root.name

            ltm.root.perform_transition(label, params, namespace, payload)

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

            executor.consume_queues(ltm)
        except Exception as e:
            get_db().log_retry(
                item_id,
                ltm.root.id,
                "execute",
                {
                    "label": label,
                    "params": params,
                    "namespace": namespace,
                    "payload": payload,
                },
                e,
                retrying=False,
            )
            raise e

    def start(self, ltm, payload=None, params=None, playground=False):
        id = get_db().create_ltm(ltm, payload, params=params, playground=playground)
        return id
