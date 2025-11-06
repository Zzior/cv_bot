from typing import Sequence

from sqlalchemy import select, exists, or_
from sqlalchemy.ext.asyncio import AsyncSession

from errors.database import NotFoundError

from ..models import Weight


class WeightRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def new(self, name: str, path: str, classes: dict) -> Weight:
        weight = Weight(
            name=name,
            path=path,
            classes=classes
        )
        self.session.add(weight)
        await self.session.flush()
        return weight

    async def check_to_add(self, name: str, path: str) -> bool:
        query = select(
            exists().where(
                or_(Weight.name == name, Weight.path == path)
            )
        )
        result = await self.session.execute(query)
        return not result.scalar()

    async def get(self, id_: int) -> Weight | None:
        return await self.session.get(Weight, id_)

    async def get_or_raise(self, id_: int) -> Weight:
        weight: Weight | None = await self.session.get(Weight, id_)
        if weight is None:
            raise NotFoundError(f"Weight id: {id_} not found")

        return weight

    async def all(self) -> Sequence[Weight]:
        query = select(Weight).order_by(Weight.name)
        weights = await self.session.execute(query)
        return weights.scalars().all()

    async def get_by_name(self, name: str) -> Weight | None:
        query = select(Weight).where(
            Weight.name == name
        )
        weight = await self.session.execute(query)
        return weight.scalar_one_or_none()

    async def get_by_path(self, path: str) -> Weight | None:
        query = select(Weight).where(
            Weight.path == path
        )
        weight = await self.session.execute(query)
        return weight.scalar_one_or_none()

    async def delete(self, id_: int) -> bool:
        weight = await self.get(id_)
        if weight:
            await self.session.delete(weight)
            return True
        return False