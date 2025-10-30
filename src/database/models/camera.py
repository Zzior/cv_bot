import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Camera(Base):
    __tablename__ = "cameras"

    name: Mapped[str] = mapped_column(sa.String(64), unique=True, nullable=False, )
    source: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=False)
    fps: Mapped[int] = mapped_column(sa.Integer, unique=False, nullable=False)
    roi: Mapped[list[list[int]]] = mapped_column(
        sa.ARRAY(sa.Integer, dimensions=2), default=list, unique=False, nullable=False
    )
