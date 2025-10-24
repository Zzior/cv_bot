from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from errors.database import NotFoundError

from ..models import Task


class TaskRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def new(self, start: datetime, end: datetime, params: dict) -> Task:
        task = Task(
            start_time=start,
            end_time=end,
            params=params,
        )

        self.session.add(task)
        await self.session.flush()
        return task

    async def get(self, id_: int) -> Task | None:
        return await self.session.get(Task, id_)

    async def get_or_raise(self, id_: int) -> Task:
        task: Task | None = await self.session.get(Task, id_)
        if task is None:
            raise NotFoundError(f"Record id: {id_} not found")

        return task

    async def all(self) -> Sequence[Task]:
        query = select(Task).order_by(Task.id)
        cameras = await self.session.execute(query)
        return cameras.scalars().all()

    async def delete(self, id_: int) -> bool:
        task = await self.get(id_)
        if task:
            await self.session.delete(task)
            return True
        return False