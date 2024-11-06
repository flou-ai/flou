from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, func
import uuid

from flou.database import get_session, get_db
from .models import Experiment, Trial
from .schemas import (
    ExperimentList,
    ExperimentCreate,
    ExperimentDetail,
    TrialList,
    TrialCreate,
    TrialId,
    ExperimentId,
)

router = APIRouter()


@router.get("/", response_model=List[ExperimentList])
async def list_experiments(session = Depends(get_session)):
    """
    Lists all Experiments.
    """
    experiments = session.scalars(select(Experiment)).all()
    return experiments

@router.post("/", response_model=TrialId)
async def create_experiment(experiment: ExperimentCreate, session = Depends(get_session)):
    experiment_kwargs = experiment.model_dump()
    trial_kwargs = experiment_kwargs.pop("trial")

    # for now we are just creating a new LTM based on fqn
    fqn = trial_kwargs.pop("fqn")
    db = get_db(session)
    ltm = db.get_ltm_class(fqn)()

    # create the LTM and assign it to the trial
    trial_kwargs["ltm_id"] = ltm.start(payload={}, playground=True)

    trial = Trial(**trial_kwargs)
    experiment_kwargs["trials"] = [trial]

    new_experiment = Experiment(**experiment_kwargs)

    session.add(new_experiment)
    session.commit()
    session.refresh(new_experiment)

    return {"id": new_experiment.trials[0].id}

@router.get("/{experiment_id}", response_model=ExperimentDetail)
async def get_experiment(experiment_id: uuid.UUID, session = Depends(get_session)):
    experiment = session.get(Experiment, experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    # Fetch trials
    trials = session.scalars(
        select(Trial).where(Trial.experiment_id == experiment_id)
    ).all()
    experiment.trials = trials
    experiment.trials_count = len(trials)
    return experiment

@router.put("/{experiment_id}", response_model=ExperimentDetail)
async def update_experiment(experiment_id: uuid.UUID, experiment: ExperimentCreate, session = Depends(get_session)):
    existing_experiment = session.get(Experiment, experiment_id)
    if not existing_experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    for key, value in experiment.model_dump().items():
        setattr(existing_experiment, key, value)
    session.commit()
    session.refresh(existing_experiment)
    return existing_experiment

@router.delete("/{experiment_id}")
async def delete_experiment(experiment_id: uuid.UUID, session = Depends(get_session)):
    existing_experiment = session.get(Experiment, experiment_id)
    if not existing_experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    session.delete(existing_experiment)
    session.commit()
    return {"message": "Experiment deleted successfully"}

# Trials routes
@router.get("/{experiment_id}/trials/", response_model=List[TrialList])
async def list_trials(experiment_id: uuid.UUID, session = Depends(get_session)):
    trials = session.scalars(
        select(Trial).where(Trial.experiment_id == experiment_id)
    ).all()
    return trials

@router.post("/{experiment_id}/trials/", response_model=TrialList)
async def create_trial(experiment_id: uuid.UUID, trial: TrialCreate, session = Depends(get_session)):
    if not session.get(Experiment, experiment_id):
        raise HTTPException(status_code=404, detail="Experiment not found")
    new_trial = Trial(experiment_id=experiment_id, **trial.model_dump())
    session.add(new_trial)
    session.commit()
    session.refresh(new_trial)
    return new_trial

@router.get("/{experiment_id}/trials/{trial_id}", response_model=TrialList)
async def get_trial(experiment_id: uuid.UUID, trial_id: uuid.UUID, session = Depends(get_session)):
    trial = session.get(Trial, trial_id)
    if not trial or trial.experiment_id != experiment_id:
        raise HTTPException(status_code=404, detail="Trial not found")
    return trial

@router.put("/{experiment_id}/trials/{trial_id}", response_model=TrialList)
async def update_trial(experiment_id: uuid.UUID, trial_id: uuid.UUID, trial: TrialCreate, session = Depends(get_session)):
    existing_trial = session.get(Trial, trial_id)
    if not existing_trial or existing_trial.experiment_id != experiment_id:
        raise HTTPException(status_code=404, detail="Trial not found")
    for key, value in trial.model_dump().items():
        setattr(existing_trial, key, value)
    session.commit()
    session.refresh(existing_trial)
    return existing_trial

@router.delete("/{experiment_id}/trials/{trial_id}")
async def delete_trial(experiment_id: uuid.UUID, trial_id: uuid.UUID, session = Depends(get_session)):
    trial = session.get(Trial, trial_id)
    if not trial or trial.experiment_id != experiment_id:
        raise HTTPException(status_code=404, detail="Trial not found")
    session.delete(trial)
    session.commit()
    return {"message": "Trial deleted successfully"}
