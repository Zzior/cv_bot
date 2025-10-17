import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship


from .base import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .record import Record

class Camera(Base):
    __tablename__ = "cameras"

    name: Mapped[str] = mapped_column(sa.Text, unique=True, nullable=False)
    source: Mapped[str] = mapped_column(sa.Text, unique=True, nullable=False)
    roi: Mapped[list[list[int]]] = mapped_column(
        sa.ARRAY(sa.Integer, dimensions=2), default=list, unique=False, nullable=False
    )

    records: Mapped[list["Record"]] = relationship(
        init=False, back_populates="camera", passive_deletes=True, lazy="selectin"
    )