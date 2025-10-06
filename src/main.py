from logging import INFO
import asyncio

from src.bot.dispatcher import get_dispatcher
from src.logger import LogInfo

from src.config import config

async def main():
    dp = get_dispatcher(config.logger, config.i18n, config.dp)

    await config.start()
    try:
        await dp.start_polling(config.bot)

    finally:
        config.logger.write_log(LogInfo("Shutting down", log_level=INFO))
        await config.stop()


if __name__ == "__main__":
    asyncio.run(main())
