from functools import lru_cache
from typing import AsyncGenerator, Callable

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .config import get_db_config

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
