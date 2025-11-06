import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Weight(Base):
    __tablename__ = "weights"

    name: Mapped[str] = mapped_column(sa.String(64), unique=True, nullable=False)
    path: Mapped[str] = mapped_column(sa.String(512), unique=True, nullable=False)
    classes: Mapped[dict] = mapped_column(sa.JSON, default=dict, nullable=False, unique=False)
