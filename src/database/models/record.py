from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship


from .base import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .camera import Camera


class Record(Base):
    __tablename__ = "records"

    start_time: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    segment_size: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    record_dir: Mapped[str] = mapped_column(sa.Text, nullable=False)

    camera_id: Mapped[int] = mapped_column(
        sa.ForeignKey("cameras.id", ondelete="CASCADE"),
        nullable=False,
    )

    camera: Mapped["Camera"] = relationship(init=False, back_populates="records", lazy="joined")