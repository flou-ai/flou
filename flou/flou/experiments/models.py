from datetime import datetime
from flou.database.models import Base
import uuid

from sqlalchemy import func, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql.functions import now
from sqlalchemy.types import String

from flou.database.utils import JSONType


class Experiment(Base):
    __tablename__ = "experiments_experiments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    index: Mapped[str] = mapped_column(default=0, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(), nullable=False)
    ltm_id: Mapped[int] = mapped_column(ForeignKey("ltm_ltms.id"), nullable=False)
    rollback_index: Mapped[int] = mapped_column(nullable=False)
    snapshot_index: Mapped[int] = mapped_column(nullable=False)
    inputs: Mapped[dict] = mapped_column(JSONType(), default=dict, nullable=False)
    outputs: Mapped[dict] = mapped_column(JSONType(), default=dict, nullable=False)


class Trial(Base):
    __tablename__ = "experiments_trials"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    index: Mapped[str] = mapped_column(default=0, nullable=False)
    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiments_experiments.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    rollback_index: Mapped[int] = mapped_column(nullable=False)
    snapshot_index: Mapped[int] = mapped_column(nullable=False)
    inputs: Mapped[dict] = mapped_column(JSONType(), default=dict, nullable=False)
    outputs: Mapped[dict] = mapped_column(JSONType(), default=dict, nullable=False)