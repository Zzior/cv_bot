from dataclasses import dataclass

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from aiogram import Bot

    from config import Config
    from i18n.i18n import I18n
    from logger import LogWriter
    from database.database import DatabaseProvider

@dataclass(slots=True)
class App:
    config: "Config"

    logger: "LogWriter"

    db: "DatabaseProvider"

    bot: "Bot"

    i18n: "I18n"

    # TaskManager
    # CameraManager
    # WeightManager


_app: App | None = None

def set_app(app: App) -> None:
    global _app
    _app = app

def get_app() -> App:
    if _app is None:
        raise RuntimeError("App not initialized")
    return _app