from uuid import UUID

from sqlalchemy import select
# from sqlalchemy.orm import selectinload

from fastapi import HTTPException

from backend.dao_base import BaseDao
from backend.db_models import User
from backend.db import session_maker

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
            
    @classmethod
    async def delete_user_by_id(cls, user_id: UUID):
        async with session_maker() as session:
            async with session.begin():
                query = select(cls.model).filter_by(id=user_id)
                result = await session.execute(query)
                user_to_delete = result.scalar_one_or_none()
                if not user_to_delete:
                    raise HTTPException(status_code=404, detail="User not found")
                await session.delete(user_to_delete)
                return
            
    # @classmethod
    # async def get_user_with_token(cls, **filter_by):
    #     async with session_maker() as session:
    #         query = select(cls.model).filter_by(**filter_by).options(selectinload(User.token))
    #         result = await session.execute(query)
    #         return result.scalar_one_or_none()