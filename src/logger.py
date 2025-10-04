import asyncio
import multiprocessing
from queue import Empty
from pathlib import Path
from logging import ERROR, INFO
from dataclasses import dataclass

import logging
from logging.handlers import RotatingFileHandler


from aiogram import Bot


@dataclass()
class LogInfo:
    name: str

    send_bot: bool = True
    log_level: int = ERROR
    exception: BaseException = None
    message: str = "No message"

class LogWriter:
    def __init__(
            self,  log_path: Path, console_level: int = INFO,
            file_level: int = ERROR, max_bytes: int = 10*1024*1024, backup_count: int = 5,
    ):
        self.log_queue = multiprocessing.Queue()

        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        formatter = logging.Formatter(
            "—————————————————————————————————————————————\n"
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            "\n—————————————————————————————————————————————\n"
        )

        # logger
        self.logger = logging.getLogger("cv_bot")
        self.logger.setLevel(level=min(console_level, file_level))
        self.logger.propagate = False
        self.logger.handlers.clear()

        # console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)


        # File logs
        file_handler = RotatingFileHandler(self.log_path, maxBytes=max_bytes, backupCount=backup_count,encoding="utf-8")
        file_handler.setLevel(level=file_level)
        file_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

        self.bot: Bot | None = None
        self.chat_id: int | str | None = None

        self._stop = asyncio.Event()

    def setup_bot(self, bot: Bot, chat_id: int | str) -> None:
        self.bot = bot
        self.chat_id = chat_id

    @staticmethod
    def format_message(log_info: LogInfo) -> str:
        return (
            f"Exception: {type(log_info.exception).__name__}\n"
            f"Message: {log_info.exception}\n"
            f"Args: {getattr(log_info.exception, 'args', None)}\n\n"
            f"Name: {log_info.name}\n"
            f"Msg: {log_info.message}"
        )

    async def send_log(self, log_info: LogInfo) -> None:
        if self.bot and self.chat_id:
            try:
                await self.bot.send_message(chat_id=self.chat_id, text=self.format_message(log_info), parse_mode=None)
            except Exception as send_e:
                self.write_log(LogInfo("class Logger -> async send log", exception=send_e))

        self.write_log(log_info)

    def write_log(self, log_info: LogInfo) -> None:
        self.logger.log(log_info.log_level, self.format_message(log_info))

    def put_log(self, log_info: LogInfo) -> None:
        self.log_queue.put_nowait(log_info)

    async def listen_queue(self, timeout: float = 1.0) -> None:
        while not self._stop.is_set():
            try:
                item = await asyncio.to_thread(self.log_queue.get, True, timeout)
            except Empty:
                continue

            if item is None:
                break

            log: LogInfo = item
            if log.send_bot:
                await self.send_log(log)
            else:
                self.write_log(log)

    def stop(self) -> None:
        self._stop.set()
        try:
            self.log_queue.put_nowait(None)
        except Exception:
            pass
        self.log_queue.close()
        self.log_queue.join_thread()