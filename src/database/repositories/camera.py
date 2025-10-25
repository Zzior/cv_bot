from typing import Sequence

from sqlalchemy import select, exists, or_
from sqlalchemy.ext.asyncio import AsyncSession

from errors.database import NotFoundError

from ..models import Camera



class CameraRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def new(self, name: str, source: str, roi: list | None = None) -> Camera:
        camera = Camera(
            name=name,
            source=source,
            roi=roi or []
        )
        self.session.add(camera)
        await self.session.flush()
        return camera

    async def check_to_add(self, name: str, source: str):
        query = select(
            exists().where(
                or_(Camera.name == name, Camera.source == source)
            )
        )
        result = await self.session.execute(query)
        return not result.scalar()

    async def get(self, id_: int) -> Camera | None:
        return await self.session.get(Camera, id_)

    async def get_or_raise(self, id_: int) -> Camera:
        camera: Camera | None = await self.session.get(Camera, id_)
        if camera is None:
            raise NotFoundError(f"Camera id: {id_} not found")

        return camera

    async def all(self) -> Sequence[Camera]:
        query = select(Camera).order_by(Camera.name)
        cameras = await self.session.execute(query)
        return cameras.scalars().all()

    async def get_by_name(self, name: str) -> Camera | None:
        query = select(Camera).where(
            Camera.name == name
        )
        camera = await self.session.execute(query)
        return camera.scalar_one_or_none()

    async def get_by_source(self, source: str) -> Camera | None:
        query = select(Camera).where(
            Camera.source == source
        )
        camera = await self.session.execute(query)
        return camera.scalar_one_or_none()

    async def update_roi(self, id_: int, roi: list[list[int]]) -> Camera:
        camera = await self.get_or_raise(id_)
        camera.roi = roi
        await self.session.flush()
        return camera

    async def delete(self, id_: int) -> bool:
        camera = await self.get(id_)
        if camera:
            await self.session.delete(camera)
            return True
        return False