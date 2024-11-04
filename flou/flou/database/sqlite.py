from datetime import datetime
import json

from sqlalchemy import func, update, cast
from sqlalchemy.dialects.sqlite import JSON, insert
from redis import Redis

from flou.conf import settings
from .base import BaseDatabase
from .models import LTM, Error
from .utils import json_dumps


redis = Redis(host=settings.redis.host, port=settings.redis.port, db=settings.redis.db)


class SQLiteDatabase(BaseDatabase):
    def list_ltms(self, playground=False):

        with self.get_session() as session:
            ltms = (
                session.query(
                    LTM.id,
                    LTM.name,
                    LTM.fqn,
                    func.json_array_length(LTM.snapshots).label("snapshots_count"),
                    LTM.created_at,
                    LTM.updated_at,
                )
                .filter(LTM.playground == playground)
                .all()
            )

        return ltms

    def _update_state(self, ltm_id, updates, snapshot):

        # jsonb_set needs nested calls to apply several values
        update_pairs = []
        for path, value in updates:
            key = path.split(".")
            update_pairs.extend([f"$.{'.'.join(key)}", func.JSON(json_dumps(value))])

        with self.get_session() as session:
            session.execute(
                update(LTM)
                .where(LTM.id == ltm_id)
                .values(
                    state=func.json_set(LTM.state, *update_pairs),
                    snapshots=func.json_insert(
                        LTM.snapshots, "$[#]", func.JSON(json_dumps(snapshot))
                    ),
                )
            )
            session.commit()

    def _rollback(self, ltm_id, new_state, new_snapshots, new_rollback):
        with self.get_session() as session:
            session.execute(
                update(LTM)
                .where(LTM.id == ltm_id)
                .values(
                    state=new_state,
                    snapshots=new_snapshots,
                    rollbacks=func.json_insert(
                        LTM.rollbacks, "$[#]", func.JSON(json_dumps(new_rollback))
                    ),
                )
            )
            session.commit()

    def _atomic_append(self, ltm_id, path, value):
        key = f"$.{'.'.join(path)}"

        with self.get_session() as session:
            result = session.execute(
                update(LTM)
                .where(LTM.id == ltm_id)
                .values(
                    state=func.json_insert(
                        LTM.state, f"{key}[#]", func.JSON(json_dumps(value))
                    )
                )
                .returning(func.json_extract(LTM.state, key))
            )
            result = json.loads(result.scalar_one())
            session.commit()
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
                    set_={
                        "retries": func.json_insert(
                            Error.retries, "$[#]", func.JSON(json_dumps(retry))
                        )
                    },
                )
                .returning(Error.id)
            )
            result = result.scalar_one()
            session.commit()
        return result
