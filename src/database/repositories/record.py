from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.errors.database import NotFoundError

from ..models import Record


class RecordRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def new(self, start: datetime, end: datetime, segment: int, rec_dir: str, camera_id: int) -> Record:
        record = Record(
            start_time=start,
            end_time=end,
            segment_size=segment,
            record_dir=rec_dir,
            camera_id=camera_id,
        )

        self.session.add(record)
        await self.session.flush()
        return record

    async def get(self, id_: int) -> Record | None:
        return await self.session.get(Record, id_)

    async def get_or_raise(self, id_: int) -> Record:
        record: Record | None = await self.session.get(Record, id_)
        if record is None:
            raise NotFoundError(f"Record id: {id_} not found")

        return record

    async def delete(self, id_: int) -> bool:
        record = await self.get(id_)
        if record:
            await self.session.delete(record)
            return True
        return False