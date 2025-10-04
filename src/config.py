import asyncio
from os import getenv
from pathlib import Path

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from src.logger import LogWriter

class Config:
    def __init__(self):
        self.tasks = []
        self.app_dir = Path(__file__).parent.parent
        self.storage_dir = self.app_dir / "storage"

        load_dotenv(self.app_dir / ".env")

        self.logger = LogWriter(self.storage_dir / "logs/app.log")

        # env
        self.token = getenv("BOT_TOKEN")
        self.log_chat_id = getenv("LOG_CHAT_ID")

        self.dp = Dispatcher()
        self.bot = Bot(token=self.token, default=DefaultBotProperties(parse_mode="HTML"))

        self.logger.setup_bot(self.bot, self.log_chat_id)

    async def start(self):
        log_listen = asyncio.create_task(self.logger.listen_queue())

        self.tasks.append(log_listen)

    async def stop(self):
        self.logger.stop()

config = Config()
