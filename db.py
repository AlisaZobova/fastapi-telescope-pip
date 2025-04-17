from functools import lru_cache
from typing import AsyncGenerator, Callable

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    user: str = Field(description='database user', alias='DB_USER')
    password: str = Field(description='database password', alias='DB_PASS')
    host: str = Field(description='database host', alias='DB_HOST')
    port: int = Field(description='database port', alias='DB_PORT')
    name: str = Field(description='database name', alias='DB_NAME')

    @property
    def async_url(self) -> str:
        return f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}'


def get_db_config() -> DatabaseConfig:
    return DatabaseConfig() 


@lru_cache
def get_async_engine(
) -> AsyncEngine:
    config = get_db_config()

    return create_async_engine(
        config.async_url,
        echo=True,
    )


@lru_cache
def get_async_sessionmaker(
        engine: AsyncEngine = Depends(get_async_engine),
) -> Callable[..., AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
    )


async def get_async_session(
        sessionmaker: Callable[..., AsyncSession] = Depends(get_async_sessionmaker),
) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        yield session
