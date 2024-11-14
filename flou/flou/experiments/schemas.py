from uuid import UUID

from flou.api.schemas import BaseModel, TimestampedModel


class TrialId(BaseModel):
    id: UUID


class TrialBase(BaseModel):
    name: str | None = None
    inputs: dict = {}
    outputs: dict = {}


class TrialList(TrialId, TrialBase, TimestampedModel):
    index: int


class TrialCreateBase(TrialBase):
    fqn: str
    rollback_index: int = 0
    snapshot_index: int = 0


class TrialCreate(TrialCreateBase):
    experiment_id: UUID
    name: str


class AddTrial(BaseModel):
    name: str | None = None
    previous_trial_outputs: dict = {}
    inputs: dict = {}


class TrialDetail(TrialList):
    ltm_id: int
    rollback_index: int


class ExperimentBase(BaseModel):
    name: str
    description: str | None = None
    inputs: dict = {}
    outputs: dict = {}


class ExperimentId(BaseModel):
    id: UUID


class ExperimentList(ExperimentId, ExperimentBase, TimestampedModel):
    index: int
    trials_count: int


class ExperimentCreate(ExperimentBase):
    trial: TrialCreateBase


class ExperimentDetail(ExperimentId, ExperimentBase, TimestampedModel):
    index: int
    trials: list[TrialDetail] = []
