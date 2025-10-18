import asyncio
from logging import INFO

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from src.logger import LogInfo, LogWriter

from src.bot.dispatcher import get_dispatcher
from src.database.database import DatabaseProvider

from src.i18n.i18n import I18n
from src.i18n.languages import en

from src.config import config
from src.app import App, set_app


async def main():
    logger = LogWriter(config.project_dir / "logs" / "bot.log")
    db = DatabaseProvider(config.db.build_connection_str())
    i18n = I18n(
        {"en": en.TEXTS},
        config.language.default_language
    )

    bot = Bot(token=config.bot.token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = get_dispatcher(logger, i18n)

    app = App(
        config=config,
        logger=logger,
        i18n=i18n,
        bot=bot,
        db=db
    )
    set_app(app)

    try:
        await dp.start_polling(app.bot)
    finally:
        logger.write_log(LogInfo("Shutting down", log_level=INFO))


if __name__ == "__main__":
    asyncio.run(main())
