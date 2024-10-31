from datetime import datetime
import uuid

from sqlalchemy import func, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql.functions import now
from sqlalchemy.types import String

from .utils import JSONType


class Base(DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=now(),
        onupdate=func.now(),
        nullable=False
    )


class LTM(Base):
    __tablename__ = "ltms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    fqn: Mapped[str] = mapped_column(String(255), nullable=False)
    structure: Mapped[dict] = mapped_column(JSONType(), default=dict, nullable=False)
    kwargs: Mapped[dict] = mapped_column(JSONType(), default=dict, nullable=False)
    state: Mapped[dict] = mapped_column(JSONType(), default=dict, nullable=False)
    snapshots: Mapped[list] = mapped_column(JSONType(), default=list, nullable=False)
    playground: Mapped[bool] = mapped_column(default=False, nullable=False)
    source_id: Mapped[int] = mapped_column(ForeignKey("ltms.id"), nullable=True)
    rollbacks: Mapped[list] = mapped_column(JSONType(), default=list, nullable=False)


class Error(Base):
    __tablename__ = "error"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    ltm_id: Mapped[int] = mapped_column(ForeignKey("ltms.id"))
    reason: Mapped[str] = mapped_column(String(30), nullable=False)
    item: Mapped[dict] = mapped_column(JSONType(), nullable=False)
    retries: Mapped[list] = mapped_column(JSONType(), default=list, nullable=False)
    retrying: Mapped[bool] = mapped_column(default=True, nullable=False)
    success: Mapped[bool] = mapped_column(default=False, nullable=False)

    def __repr__(self):
        return f"Error(ltm_id={self.ltm_id!r})"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
