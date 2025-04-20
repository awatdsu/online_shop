import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from dotenv import load_dotenv

load_dotenv()

engine = create_async_engine(os.getenv("DB_URL"), echo=True)

session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

