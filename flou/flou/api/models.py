from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Transition(BaseModel):
    label: str
    # payload? / parameters? / keys?