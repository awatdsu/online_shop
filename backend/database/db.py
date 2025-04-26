import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncEngine

from backend.settings import settings
from backend.models import Base

class DatabaseSessionManager:
    def __init__(self) -> None:
        self._engine: AsyncEngine = create_async_engine(
            url = settings.postgres_settings.postgres_url,
            echo = True
        )
        self.sessionmaker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind = self._engine,
            expire_on_commit = False,
            class_= AsyncSession
        )
    
    async def init_models(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    


db_manager = DatabaseSessionManager()

async def get_session():
    async with db_manager.sessionmaker() as session:
        yield session


if __name__ == "__main__":
    asyncio.run(db_manager.init_models())


__all__ = ("get_session",)
