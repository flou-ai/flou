from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String

from flou.database.models import Base
from flou.database.utils import JSONType


class LTM(Base):
    __tablename__ = "ltm_ltms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    fqn: Mapped[str] = mapped_column(String(255), nullable=False)
    structure: Mapped[dict] = mapped_column(JSONType(), default=dict, nullable=False)
    kwargs: Mapped[dict] = mapped_column(JSONType(), default=dict, nullable=False)
    state: Mapped[dict] = mapped_column(JSONType(), default=dict, nullable=False)
    snapshots: Mapped[list] = mapped_column(JSONType(), default=list, nullable=False)
    playground: Mapped[bool] = mapped_column(default=False, nullable=False)
    source_id: Mapped[int] = mapped_column(ForeignKey("ltm_ltms.id"), nullable=True)
    rollbacks: Mapped[list] = mapped_column(JSONType(), default=list, nullable=False)
