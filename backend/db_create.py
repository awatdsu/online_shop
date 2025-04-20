import os
import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from dotenv import load_dotenv
from db_models import Base

load_dotenv()

engine = create_async_engine(os.getenv("DB_URL"), echo=True)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def main():
    await drop_db()
    await create_db()

asyncio.run(main())
