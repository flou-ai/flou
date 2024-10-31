from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from flou.conf import settings
from .utils import json_dumps


engine = create_engine(settings.database.url, echo=True, json_serializer=json_dumps)


def get_db():
    if settings.database.driver.startswith("sqlite"):
        from .sqlite import SQLiteDatabase
        return SQLiteDatabase()
    elif settings.database.driver.startswith("postgresql"):
        from .base import BaseDatabase
        return BaseDatabase()


def get_session():
    return Session(engine)
