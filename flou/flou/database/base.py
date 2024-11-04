from copy import deepcopy
from datetime import datetime
import importlib
import sys
import traceback

import json
import jsonpatch
from redis import Redis
from sqlalchemy import update, func, ARRAY, String, cast, text, literal_column
from sqlalchemy.dialects.postgresql import insert, JSONB

from . import get_session
from .models import Error, LTM
from .utils import json_dumps
from flou.conf import settings


redis = Redis(host=settings.redis.host, port=settings.redis.port, db=settings.redis.db)


class BaseDatabase:

    def __init__(self, session=None, *args, **kwargs):
        self.session = session

    def get_session(self):
        if self.session:
            return self.session
        return get_session()

    def list_ltms(self, playground=False):

        with self.get_session() as session:
            ltms = (
                session.query(
                    LTM.id,
                    LTM.name,
                    LTM.fqn,
                    func.jsonb_array_length(LTM.snapshots).label("snapshots_count"),
                    LTM.created_at,
                    LTM.updated_at,
                )
                .filter(LTM.playground == playground)
                .all()
            )

        return ltms

    def create_ltm(self, ltm, payload=None, params=None, playground=False):
        from flou.engine import get_engine

        # get the fqn from an instance
        fqn = ltm.get_class_fqn()

        ltm.execute(ltm.root, payload)
        # update the snapshot arg
        snapshot = self.calculate_snapshot(
            ltm.root,
            "start",
            item={"payload": payload, "params": params, "playground": playground},
        )

        with self.get_session() as session:
            if not ltm.id:
                new_ltm = LTM(
                    name=ltm.name,
                    fqn=fqn,
                    kwargs=ltm.params,
                    state=ltm.state,
                    snapshots=[snapshot],
                    playground=playground,
                )
                session.add(new_ltm)
                session.commit()
                ltm.id = new_ltm.id
            else:
                existing_ltm = session.get(LTM, ltm.id)
                existing_ltm.name = ltm.name
                existing_ltm.fqn = fqn
                existing_ltm.kwargs = ltm.params
                existing_ltm.state = ltm.state
                existing_ltm.snapshots = [snapshot]
                existing_ltm.playground = playground
                session.commit()

        ltm._snapshots = [snapshot]

        # immediate cause we need this to finish before a sub state can execute
        get_engine().consume_queues(ltm)

        # publish to redis
        redis.publish(
            f"ltm:{ltm.id}:start",
            json_dumps(
                {
                    "id": ltm.id,
                    "snapshot": snapshot,
                }
            ),
        )

        return ltm.id

    def get_ltm_class(self, fqn):
        module, _, class_name = fqn.rpartition(".")
        return getattr(importlib.import_module(module), class_name)

    def load_ltm(self, pk, snapshots=False, rollbacks=False, playground=False):
        with self.get_session() as session:
            columns = [
                LTM.id,
                LTM.fqn,
                LTM.kwargs,
                LTM.state,
                LTM.created_at,
                LTM.updated_at,
            ]

            if snapshots:
                columns.append(LTM.snapshots)
            if rollbacks:
                columns.append(LTM.rollbacks)
            if playground:
                columns.extend([LTM.playground, LTM.source_id])

            ltm_data = session.query(*columns).filter_by(id=pk).one()

            args = {
                "id": pk,
                "state": ltm_data.state,
                "created_at": ltm_data.created_at,
                "updated_at": ltm_data.updated_at,
                "params": ltm_data.kwargs,
            }
            if snapshots:
                args["snapshots"] = ltm_data.snapshots
            if rollbacks:
                args["rollbacks"] = ltm_data.rollbacks
            if playground:
                args["playground"] = ltm_data.playground
                args["source_id"] = ltm_data.source_id

            ltm = self.get_ltm_class(ltm_data.fqn)(**args)
        return ltm

    def copy_ltm(self, pk):
        with self.get_session() as session:
            ltm = session.get(LTM, pk)
            new_ltm = LTM(
                name=ltm.name,
                fqn=ltm.fqn,
                structure=ltm.structure,
                kwargs=ltm.kwargs,
                state=ltm.state,
                snapshots=ltm.snapshots,
                playground=True,
                source_id=pk,
                rollbacks=ltm.rollbacks,
                created_at=ltm.created_at,
                updated_at=ltm.updated_at,
            )
            session.add(new_ltm)
            session.commit()
            last_id = new_ltm.id
        return last_id

    def _update_state(self, ltm_id, updates, snapshot):

        # FIXME: we were previously using nested `jsonb_set` but on large inputs
        # we surpassed python's recursion limit. The way to go is using postgres
        # jsonb subscription, but sqlalchemy doesn't support it yet.
        # see: https://github.com/sqlalchemy/sqlalchemy/issues/10927# 

        # raw sql implementation: works but it's insecure
        def to_brackets(path):
            path = path.split(".")
            path = "']['".join(path)
            path = f"['{path}']"
            return path

        sql_updates = {
            f"state{to_brackets(path)}": json_dumps(value)
            for path, value in updates
        }
        update_query = text(
            f"""
                            UPDATE ltms SET
                            snapshots = snapshots || :snapshot,
                            {', '.join([f"{key} = CAST('{value}' AS JSONB) " for i, (key, value) in enumerate(sql_updates.items())])}
                            WHERE id=:ltm_id
                            """
        )

        values = {
            "snapshot": json_dumps(snapshot),
            "ltm_id": ltm_id,
        }

        with self.get_session() as session:
            session.execute(
                update_query, values
            )
            session.commit()

        return

        def to_brackets(path):
            path = path.split(".")
            path = "']['".join(path)
            path = f"['{path}']"
            return path

        sql_updates = {
            literal_column(f"state{to_brackets(path)}") : cast(value, JSONB)
            for path, value in updates
        }

        values = {
            "snapshot": json_dumps(snapshot),
            "ltm_id": ltm_id,
        }
        # values.update({f"value{i}": value for i, (key, value) in enumerate(updates)})
        sql_updates.update(snapshots=LTM.snapshots + [snapshot])

        with self.get_session() as session:
            session.execute(
                update(LTM)
                .where(LTM.id == ltm_id)
                .values(sql_updates)
            )

        return

        # nested jsonb_set implementation: works for small amounts of updates
        state_value = LTM.state
        for path, value in updates:
            key = path.split(".")
            # key = ARRAY([path_element for path_element in key], String)
            state_value = func.jsonb_set(state_value, key, cast(value, JSONB))

        with self.get_session() as session:
            session.execute(
                update(LTM)
                .where(LTM.id == ltm_id)
                .values(
                    state=state_value,
                    snapshots=LTM.snapshots + [snapshot],
                    # snapshots=func.jsonb_insert(
                    #     LTM.snapshots, "{-1}", json_dumps(snapshot), True
                    # ),
                )
            )
            session.commit()

    def update_state(self, ltm, reason, item=None):

        updates = ltm.root._updates_queue

        prepared_updates = []
        for ltm_fqn, update_list in updates:
            path = ltm_fqn.partition(".")[2]  # get base path (without root)
            if path:
                path += "."
            else:
                path = ""

            for key, value in update_list.items():
                prepared_updates.append((f"{path}{key}", value))

        snapshot = self.calculate_snapshot(ltm.root, reason, item)

        self._update_state(ltm.root.id, prepared_updates, snapshot)

        # add snapshot to ltm if we have them
        if ltm.root._snapshots:
            ltm.root._snapshots.append(snapshot)

        ltm.root._updates_queue = None

        # publish to redis
        redis.publish(
            f"ltm:{ltm.root.id}:{reason}",
            json_dumps(
                {
                    "id": ltm.root.id,
                    "snapshot": snapshot,
                }
            ),
        )

    def calculate_snapshot(self, ltm, reason, item):
        patch = jsonpatch.make_patch(ltm._initial_state, ltm._state).patch
        ltm._initial_state = deepcopy(ltm._state)
        snapshot = {
            "time": f"{datetime.now()}",
            "reason": reason,
            "item": item,
            "patch": patch,
            "execute_queue": deepcopy(ltm._execute_queue) or [],
            "transitions_queue": deepcopy(ltm._transitions_queue) or [],
        }
        return snapshot

    def recreate_state_from_snapshot(self, ltm, snapshot_index):
        """
        Recreate a previous state from the list of snapshots up to (including) `snapshot_index`
        """
        recreated_state = {}

        for snapshot in ltm._snapshots[: snapshot_index + 1]:
            recreated_state = jsonpatch.apply_patch(recreated_state, snapshot["patch"])

        return recreated_state

    def _rollback(self, ltm_id, new_state, new_snapshots, new_rollback):
        with self.get_session() as session:
            session.execute(
                update(LTM)
                .where(LTM.id == ltm_id)
                .values(
                    state=new_state,
                    snapshots=new_snapshots,
                    rollbacks=LTM.rollbacks + [new_rollback],
                )
            )
            session.commit()

    def rollback(self, ltm, snapshot_index=None, rollback_index=None, reason="manual"):
        """
        Rollback the LTM to a previous snapshot.

        The snapshot_index is zero indexed and is included.
        Adds the current state & snapshots to the rollbacks.
        """

        if snapshot_index is None and rollback_index is None:
            raise ValueError("Either snapshot_index or rollback_index must be provided")

        # we need the snapshots to rollback
        ltm = ltm.root
        ltm = self.load_ltm(ltm.id, snapshots=True, rollbacks=True)

        new_rollback = {
            "time": f"{datetime.now()}",
            "state": ltm._state,
            "snapshots": ltm._snapshots,
            "reason": reason,
        }

        if snapshot_index is not None:
            new_snapshots = ltm._snapshots[: snapshot_index + 1]
            # calculate snapshot until that point
            if snapshot_index == -1:  # if restart
                ltm._state = None
                ltm._init_ltms()
                new_state = ltm._state
            else:
                new_state = self.recreate_state_from_snapshot(ltm, snapshot_index)
        else:
            new_snapshots = ltm._rollbacks[rollback_index]["snapshots"]
            new_state = ltm._rollbacks[rollback_index]["state"]
            if not reason:
                reason = "recover rollback"

        self._rollback(ltm.id, new_state, new_snapshots, new_rollback)

        ltm._snapshots = new_snapshots
        ltm._state = new_state
        if not ltm._rollbacks:
            ltm._rollbacks = []
        ltm._rollbacks.append(new_rollback)

        # publish to redis
        redis.publish(
            f"ltm:{ltm.root.id}:rollback",
            json_dumps(
                {
                    "id": ltm.root.id,
                    "snapshot_index": snapshot_index,
                }
            ),
        )

        # set _initial_state to be used in snapshot calculation
        ltm._initial_state = {}
        return ltm

    def replay(self, ltm, snapshot_index):
        snapshot = ltm._snapshots[snapshot_index]
        ltm = self.rollback(ltm, snapshot_index - 1, reason="replay")
        from flou.engine import get_engine

        engine = get_engine()
        # special case for restart
        if snapshot_index == 0:
            engine.start(ltm, **snapshot["item"])
        else:
            engine.transition(ltm, **snapshot["item"])

    def _atomic_append(self, ltm_id, path, value):
        path_last_element = path + ["-1"]

        with self.get_session() as session:
            result = session.execute(
                update(LTM)
                .where(LTM.id == ltm_id)
                .values(
                    state=func.jsonb_insert(
                        LTM.state, path_last_element, cast(value, JSONB), True
                    )
                )
                .returning(func.jsonb_extract_path(LTM.state, *path))
            )
            result = result.scalar_one()
            session.commit()
        return result

    def atomic_append(self, ltm, key, value):

        root = ltm.root

        fqn = ltm.fqn.partition(".")[2]
        if fqn:
            fqn += "."

        path = f"{fqn}{key}".split(".")

        result = self._atomic_append(root.id, path, value)

        # from ipdb import set_trace; set_trace()
        return result

    def _log_retry(self, item_id, ltm_id, reason, item, retry, retrying=True):
        with self.get_session() as session:
            result = session.execute(
                insert(Error)
                .values(
                    id=item_id,
                    ltm_id=ltm_id,
                    reason=reason,
                    item=item,
                    retries=[retry],
                    retrying=retrying,
                )
                .on_conflict_do_update(
                    index_elements=["id"],
                    set_={"retries": Error.retries + [retry], "retrying": retrying},
                )
                .returning(Error.id)
            )
            result = result.scalar_one()
            session.commit()
        return result

    def log_retry(self, item_id, ltm_id, reason, item, exception, retrying=True):
        """
        Creates or appends a retry log
        """
        exc_info = sys.exc_info()
        formatted_traceback = "".join(traceback.format_exception(*exc_info))
        exc_type, exc_value, exc_context = sys.exc_info()

        retry = {
            "time": f"{datetime.now()}",
            "type": exc_type.__name__,
            "description": str(exc_value),
            "details": formatted_traceback,
        }

        result = self._log_retry(item_id, ltm_id, reason, item, retry, retrying)

        self._broadcast_error(result)

    def set_stop_retrying(self, item_id):
        """
        Updates an `Error` that has stopped retrying
        """
        with self.get_session() as session:
            result = session.execute(
                update(Error).where(Error.id == item_id).values(retrying=False)
            )
            session.commit()
            if result.rowcount > 0:
                session.commit()
                self._broadcast_error(item_id)

    def set_success(self, item_id):
        """
        If there was a previous error for this item_id set it as success
        """
        with self.get_session() as session:
            result = session.execute(
                update(Error)
                .where(Error.id == item_id)
                .values(retrying=False, success=True)
            )
            if result.rowcount > 0:
                session.commit()
                self._broadcast_error(item_id)

    def set_retrying(self, item_id):
        """
        Updates an `Error` that is starting to retry again
        """
        with self.get_session() as session:
            session.execute(
                update(Error).where(Error.id == item_id).values(retrying=True)
            )
            session.commit()
        self._broadcast_error(item_id)

    def _broadcast_error(self, item_id):
        with self.get_session() as session:
            error = session.get(Error, item_id)
        redis.publish(
            f"ltm:{error.ltm_id}:error",
            json_dumps(
                {
                    "id": error.ltm_id,
                    "error": error.as_dict(),
                }
            ),
        )
