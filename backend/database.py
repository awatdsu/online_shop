import os

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from dotenv import load_dotenv
from db_models import Base

load_dotenv()

engine = create_async_engine(os.getenv("DB_URL"), echo=True)

session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# async def main():
#     await drop_db()
#     await create_db()
#     # async with session_maker() as session:
#     #     User1 = User(
#     #         username = "aboba",
#     #         first_name = "Ivan",
#     #         last_name = "Abobus",
#     #         hashed_password = "awsdbfiluqwuilefhuiqwhfh827387r428g3rukqbsfkujbkuawe"
#     #     )
#     #     User2 = User(
#     #         username = "aboba2",
#     #         first_name = "Petya",
#     #         last_name = "Abobus",
#     #         hashed_password = "nqwenf;lqwhehuquhwefknjkn2ih23hh2q9h9h"
#     #     )
#     #     session.add(User1)
#     #     await session.commit()
#     #     session.add(User2)
#     #     await session.commit()

# asyncio.run(main())
