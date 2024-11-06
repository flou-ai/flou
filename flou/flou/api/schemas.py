from datetime import datetime

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampedModel(BaseModel):
    created_at: datetime
    updated_at: datetime
