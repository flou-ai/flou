from uuid import UUID

from pydantic import BaseModel


class Experiment(BaseModel):
    name: str | None = None
    description: str | None = None
    ltm_id: int
    rollback_index: int
    inputs: dict
    outputs: dict


class TrialBase(BaseModel):
    experiment_id: UUID
    name: str | None = None
    rollback_index: id | None
    inputs: dict
    outputs: dict