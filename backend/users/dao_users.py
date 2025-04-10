from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.dao_base import BaseDao
from backend.db_models import User
from backend.database import session_maker

class UsersDao(BaseDao):
    model = User

    @classmethod
    async def add_new_user(cls, **user_data):
        async with session_maker() as session:
            async with session.begin():
                new_user = User(**user_data)
                session.add(new_user)
                await session.flush()
                new_user_id = new_user.id
                await session.commit()
                return new_user_id