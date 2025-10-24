from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Task(Base):
    __tablename__ = "tasks"

    start_time: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    params: Mapped[dict] = mapped_column(sa.JSON, default=dict, nullable=False, unique=False)
