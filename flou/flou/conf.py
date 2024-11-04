import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, HttpUrl
from typing import List, Literal


class Redis(BaseModel):
    host: str = "localhost"
    port: int = 6379
    password: str = None
    db: int = 0


class Database(BaseModel):
    # driver: str = "sqlite"
    # name: str = "flou.sqlite3"
    # user: str = None
    # password: str = None
    # host: str = None
    # port: int = None
    driver: str = "postgresql+psycopg"
    name: str = "postgres"
    user: str = "postgres"
    password: str = "postgres"
    host: str = "localhost"
    port: int = "54320"

    @property
    def url(self):
        # Build the credentials part
        credentials = ''
        if self.user and self.password:
            credentials = f"{self.user}:{self.password}@"
        elif self.user:
            credentials = f"{self.user}@"

        # Build the host and port part
        host_port = ''
        if self.host and self.port:
            host_port = f"{self.host}:{self.port}"
        elif self.host:
            host_port = self.host

        # Construct the final URL
        if host_port:
            url = f"{self.driver}://{credentials}{host_port}/{self.name}"
        else:
            # For databases like SQLite that may not require host or credentials
            url = f"{self.driver}:///{self.name}"

        return url


class OldDatabase(BaseModel):
    engine: str = "flou.database.sqlite.SQLiteDatabase"
    name: str = "flou.sqlite3"
    user: str = None
    password: str = None
    host: str = None
    port: int = None


class Engine(BaseModel):
    engine: str = "flou.engine.celery.CeleryEngine"
    broker_url: str = "redis://localhost:6379/0"
    max_retries: int = 1
    broker_connection_retry_on_startup: bool = True


env_file = ".env"
if os.getenv("ENV", None):
    env_file = f".env.{os.getenv('ENV')}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file, env_nested_delimiter="__", extra="ignore"
    )
    APP_NAME: str = "flou"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_HOSTS: List[HttpUrl | Literal["*"]] = ["*"]
    database: Database = Database()
    old_database: OldDatabase = OldDatabase()
    engine: Engine = Engine()
    redis: Redis = Redis()


settings = Settings()
