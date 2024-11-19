from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from flou.conf import settings
from .utils import json_dumps


engine = create_engine(settings.database.url, json_serializer=json_dumps)  #, echo=True )


def get_db(session=None):
    if settings.database.driver.startswith("sqlite"):
        from .sqlite import SQLiteDatabase
        return SQLiteDatabase(session=session)
    elif settings.database.driver.startswith("postgresql"):
        from .base import BaseDatabase
        return BaseDatabase(session=session)


SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


def get_session():
    with SessionLocal() as session:
        yield session
