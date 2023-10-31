import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_host: str = '127.0.0.1'
    redis_port: int = 6379
    redis_db: int = 0

    class Config:
        env_file = "config.env"

    @property
    def redis_celery_url(self):
        return f'redis://{self.redis_host}:{self.redis_port}/{self.redis_db}'

    @property
    def redis_url(self):
        return f'redis://{self.redis_host}:{self.redis_port}/{self.redis_db}'


@lru_cache()
def get_config() -> Settings:
    return Settings()
