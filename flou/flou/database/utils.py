from datetime import datetime
import uuid
from typing import Any
import json

from sqlalchemy import types
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import row


class JSONType(types.TypeDecorator):
    """Platform-independent JSON type that uses JSONB on PostgreSQL."""

    impl = types.JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(types.JSON())


class JSONSerializer(json.JSONEncoder):
    def default(self, value: Any) -> str:
        if isinstance(value, uuid.UUID):
            return str(value)
        if isinstance(value, datetime):
            return str(value)
        if isinstance(value, row.Row):
            return value._asdict()

        return super().default(value)


def json_dumps(value):
    return json.dumps(value, cls=JSONSerializer)