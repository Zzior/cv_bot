from typing import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from .repositories import CameraRepo


class Database:
    session: AsyncSession

    camera: CameraRepo

    def __init__(self, session: AsyncSession):
        self.session = session
        self.camera = CameraRepo(session=session)


class DatabaseProvider:
    def __init__(self, url: URL | str, debug=False):
        self.engine = create_async_engine(url=url, echo=debug, pool_pre_ping=True)

    @asynccontextmanager
    async def session(self) -> AsyncIterator[Database]:
        async with AsyncSession(bind=self.engine, autoflush=False) as session:
            db = Database(session=session)
            try:
                yield db
                await session.commit()
            except:
                await session.rollback()
                raise
