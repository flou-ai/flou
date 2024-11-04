from functools import lru_cache
import importlib

from flou.conf import settings


def get_engine():
    # create an instance from a fqn
    module, _, class_name = settings.engine.engine.rpartition(".")
    database = getattr(importlib.import_module(module), class_name)(settings.old_database)
    return database