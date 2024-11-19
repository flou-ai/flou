import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import now
from sqlalchemy.types import String

from flou.database.models import Base
from flou.database.utils import JSONType


class Error(Base):
    __tablename__ = "engine_error"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    ltm_id: Mapped[int] = mapped_column(ForeignKey("ltm_ltms.id"))
    reason: Mapped[str] = mapped_column(String(30), nullable=False)
    item: Mapped[dict] = mapped_column(JSONType(), nullable=False)
    retries: Mapped[list] = mapped_column(JSONType(), default=list, nullable=False)
    retrying: Mapped[bool] = mapped_column(default=True, nullable=False)
    success: Mapped[bool] = mapped_column(default=False, nullable=False)

    def __repr__(self):
        return f"Error(ltm_id={self.ltm_id!r})"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

