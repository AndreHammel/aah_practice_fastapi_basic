# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fastapi_zero.settings import Settings

engine = create_async_engine(Settings().DATABASE)


async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
