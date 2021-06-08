from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    def __init__(self):
        parent_path = Path.cwd()
        super(Settings, self).__init__(
            _env_file=f'{parent_path}/.env',
            _env_file_encoding='utf-8')

    sqlalchemy_database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = "../.env"


# configuration
@lru_cache()
def get_settings():
    return Settings()
