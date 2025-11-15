from aiogram import Dispatcher
from aiogram.types import ErrorEvent

from app import App
from i18n.i18n import I18n
from logger import LogWriter, LogInfo

from .routers import routers
from .middlewares import AccessMiddleware, AppMiddleware, LanguageMiddleware

def get_dispatcher(logger: LogWriter, app: App, i18n: I18n, include: Dispatcher = None) -> Dispatcher:
    dp = include if include else Dispatcher()
    for router in routers:
        dp.include_router(router)

    # Register middlewares
    dp.update.middleware(AccessMiddleware(app.config.bot.user_ids))
    dp.update.middleware(AppMiddleware(app))
    dp.update.middleware(LanguageMiddleware(i18n))

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
