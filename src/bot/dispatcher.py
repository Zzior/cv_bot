from aiogram import Dispatcher
from aiogram.types import ErrorEvent

from src.logger import LogWriter, LogInfo

from bot.routers import routers


def get_dispatcher(logger: LogWriter, include: Dispatcher = None) -> Dispatcher:
    """This function set up dispatcher with routers, filters and middlewares."""
    dp = include if include else Dispatcher()
    for router in routers:
        dp.include_router(router)

    @dp.error()
    async def errors_handler(error_update: ErrorEvent):
        await logger.send_log(
            LogInfo(
                "Telegram handler error",
                send_bot=True,
                exception=error_update.exception,
                message=f"Event type {error_update.update.event_type}"
            )
        )
        return True

    return dp
