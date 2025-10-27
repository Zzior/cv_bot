from os import getenv
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from dataclasses import dataclass

from sqlalchemy.engine import URL

project_dir = Path(__file__).parent.parent
load_dotenv(project_dir / ".env")

@dataclass
class DatabaseConfig:
    name: str | None = getenv("POSTGRES_DATABASE")
    user: str | None = getenv("POSTGRES_USER")
    passwd: str | None = getenv("POSTGRES_PASSWORD", None)
    port: int = int(getenv("POSTGRES_PORT", 5432))
    host: str = getenv("POSTGRES_HOST", "db")

    driver: str = "asyncpg"
    database_system: str = "postgresql"

    def build_connection_str(self) -> str:
        return URL.create(
            drivername=f"{self.database_system}+{self.driver}",
            username=self.user,
            database=self.name,
            password=self.passwd,
            port=self.port,
            host=self.host,
        ).render_as_string(hide_password=False)


@dataclass
class BotConfig:
    token: str = getenv("BOT_TOKEN")


@dataclass
class SystemConfig:
    time_zone: str = getenv("TIME_ZONE")
    default_language: str = getenv("DEFAULT_LANGUAGE")

    @property
    def tzinfo(self) -> ZoneInfo:
        return ZoneInfo(self.time_zone)


@dataclass
class Config:
    project_dir = project_dir
    storage_dir = project_dir / "storage"
    system = SystemConfig()
    db = DatabaseConfig()
    bot = BotConfig()

config = Config()
