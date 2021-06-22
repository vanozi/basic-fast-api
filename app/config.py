import sys
from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    def __init__(self):
        # check if the program is run in debug mode
        if sys.gettrace() is None:
            parent_path = Path.cwd()
        else:
            parent_path = Path.cwd().parent
        super(Settings, self).__init__(
            _env_file=f'{parent_path}/.env',
            _env_file_encoding='utf-8')

    sqlalchemy_database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    registration_token_lifetime: int = 7

    # to be put in dotenv for production
    base_url: str = 'http://localhost:8000'
    api_prefix: str = "/api"
    smtp_server: str
    app_name: str
    mail_sender: str = 'henk@henk.com'

    class Config:
        env_file = "../.env"


# configuration
@lru_cache()
def get_settings():
    return Settings()
