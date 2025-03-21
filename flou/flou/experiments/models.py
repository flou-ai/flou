from typing import List
import uuid

from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String
from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger

from flou.database.models import Base
from flou.database.utils import JSONType


class Experiment(Base):
    __tablename__ = "experiments_experiments"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    index: Mapped[int] = mapped_column(default=1, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(), nullable=False)
    inputs: Mapped[dict] = mapped_column(JSONType(), default=dict, nullable=False)
    outputs: Mapped[dict] = mapped_column(JSONType(), default=dict, nullable=False)

    trials: Mapped[List["Trial"]] = relationship(back_populates="experiment")


# Define the trigger function using alembic_utils
experiments_set_index = PGFunction(
    schema="public",
    signature="experiments_set_index()",
    definition="""
        RETURNS trigger AS $$
        BEGIN
            NEW.index := COALESCE(
                (SELECT MAX(index) FROM experiments_experiments), 0
            ) + 1;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """,
)


# Define the trigger using alembic_utils
experiments_set_index_trigger = PGTrigger(
    schema="public",
    signature="experiments_set_index_trigger",
    on_entity="public.experiments_experiments",
    is_constraint=False,
    definition="""
    BEFORE INSERT ON public.experiments_experiments
    FOR EACH ROW EXECUTE FUNCTION public.experiments_set_index();
    """,
)


class Trial(Base):
    __tablename__ = "experiments_trials"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    index: Mapped[int] = mapped_column(default=1, nullable=False)
    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiments_experiments.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    ltm_id: Mapped[int] = mapped_column(ForeignKey("ltm_ltms.id"), nullable=False)
    rollback_index: Mapped[int] = mapped_column(nullable=False)
    snapshot_index: Mapped[int] = mapped_column(nullable=False)
    inputs: Mapped[dict] = mapped_column(JSONType(), default=dict, nullable=False)
    outputs: Mapped[dict] = mapped_column(JSONType(), default=dict, nullable=False)

    experiment: Mapped[Experiment] = relationship("Experiment", back_populates="trials")


# Define the trigger function using alembic_utils
trials_set_index = PGFunction(
    schema="public",
    signature="trials_set_index()",
    definition="""
        RETURNS trigger AS $$
        BEGIN
            NEW.index := COALESCE(
                (SELECT MAX(index) FROM experiments_trials WHERE experiment_id = NEW.experiment_id AND name = NEW.name), 0
            ) + 1;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """,
)


# Define the trigger using alembic_utils
trials_set_index_trigger = PGTrigger(
    schema="public",
    signature="trials_set_index_trigger",
    on_entity="public.experiments_trials",
    is_constraint=False,
    definition="""
    BEFORE INSERT ON public.experiments_trials
    FOR EACH ROW EXECUTE FUNCTION public.trials_set_index();
    """,
)
