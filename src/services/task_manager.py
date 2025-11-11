import asyncio
from dataclasses import dataclass
from typing import Annotated, Union
from datetime import datetime, timezone

from pydantic import Field, TypeAdapter

from .base.abc.task import Task
from .record.node import Record
from .inference.node import Inference
from .record.conf import RecordConf
from .inference.conf import InferenceConf

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.database import DatabaseProvider

TaskConf = Annotated[
    Union[RecordConf, InferenceConf],
    Field(discriminator="kind"),
]
_TASK_CONF_ADAPTER = TypeAdapter(TaskConf)


@dataclass
class TaskInfo:
    task: Task
    task_id: int
    task_type: str

    conf: TaskConf

    start_time: datetime
    end_time: datetime

    delayed: asyncio.Task | None = None


class TaskManager:
    def __init__(self, db: "DatabaseProvider"):
        self.db = db
        self.tasks: dict[int, TaskInfo] = {}

    @staticmethod
    def _build_task(conf: TaskConf) -> Task:
        if isinstance(conf, RecordConf):
            return Record(conf)

        elif isinstance(conf, InferenceConf):
            return Inference(conf)

        raise ValueError(f"unknown kind: {conf.kind}")

    async def _delayed_run(self, task_id: int) -> None:
        try:
            if task_id not in self.tasks:
                return

            now = datetime.now(timezone.utc)
            delay = max(0.0, (self.tasks[task_id].start_time - now).total_seconds())
            await asyncio.sleep(delay)

            task = self.tasks.get(task_id)
            if task:
                task.task.start()

        except asyncio.CancelledError:
            return

        except Exception as e:
            _ = e  # TO DO: loging
            return

    async def add_task(self, start: datetime, end: datetime, conf: TaskConf, task_id: int | None = None) -> int:
        if task_id is not None and task_id in self.tasks:
            return task_id

        now = datetime.now(timezone.utc)
        start = start.astimezone(timezone.utc)
        end = end.astimezone(timezone.utc)

        if end <= start:
            raise ValueError("end must be greater than start")
        if end <= now:
            raise ValueError("cannot create task that already ended")

        if task_id is None:
            async with self.db.session() as db:
                db_task = await db.task.new(start, end, conf.model_dump(mode="json"))
                task_id = db_task.id

        task = self._build_task(conf)
        self.tasks[task_id] = TaskInfo(task, task_id, conf.kind, conf, start, end)
        if now >= start:
            task.start()
        else:
            self.tasks[task_id].delayed = asyncio.create_task(self._delayed_run(task_id))

        return task_id

    async def stop_task(self, task_id: int) -> None:
        task = self.tasks.pop(task_id, None)
        if task is None:
            return

        if task.delayed:
            task.delayed.cancel()

        async with self.db.session() as db:
            await db.task.delete(task_id)

        task.task.stop()

    def get_tasks(self, task_type: str | None = None) -> list[TaskInfo]:
        results = []
        if task_type:
            for task_id, task_info in self.tasks.items():
                if task_type == task_info.task_type:
                    results.append(task_info)
        else:
            for task_id, task_info in self.tasks.items():
                results.append(task_info)

        return results

    async def load_tasks(self):
        now = datetime.now(timezone.utc)
        async with self.db.session() as db:
            for task in await db.task.all():
                if task.end_time > now:
                    cfg = _TASK_CONF_ADAPTER.validate_python(task.params)
                    await self.add_task(task.start_time, task.end_time, cfg, task_id=task.id)
                else:
                    await db.task.delete(task.id)

    async def watchdog(self):
        while True:
            now = datetime.now(timezone.utc)
            for task_id, task_info in list(self.tasks.items()):
                try:
                    if now >= task_info.end_time:
                        await self.stop_task(task_id)
                except Exception as e:
                    _ = e  # TO DO: logging

            await asyncio.sleep(1)
