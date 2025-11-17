import asyncio
from logging import INFO

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from logger import LogInfo, LogWriter

from bot.dispatcher import get_dispatcher
from services.task_manager import TaskManager
from database.database import DatabaseProvider

from i18n.i18n import I18n
from i18n.languages import en

from config import config
from app import App, set_app


background_tasks = []
config.paths.create_folders()


async def main():
    bot = Bot(token=config.bot.token, default=DefaultBotProperties(parse_mode="HTML"))
    logger = LogWriter(config.paths.logs / "bot.log")
    db = DatabaseProvider(config.db.build_connection_str())
    task_manager = TaskManager(db)
    i18n = I18n(
        {"en": en.TEXTS},
        config.system.default_language
    )

    app = App(
        task_manager=task_manager,
        config=config,
        logger=logger,
        i18n=i18n,
        bot=bot,
        db=db
    )
    set_app(app)
    dp = get_dispatcher(logger, app, i18n)

    await task_manager.load_tasks()
    background_tasks.append(
        asyncio.create_task(task_manager.watchdog())
    )

    try:
        await dp.start_polling(app.bot)
    finally:
        logger.write_log(LogInfo("Shutting down", log_level=INFO))


if __name__ == "__main__":
    asyncio.run(main())
