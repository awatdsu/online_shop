from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException

from backend.models import User

class UserDao:

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_one_or_none(self, **user_data) -> User:
        query = select(User).filter_by(**user_data)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def add_user(self, **user_data) -> User:
        new_user = User(**user_data)
        self.session.add(new_user)
        return new_user
    
    async def delete_user_by_id(self, user_id: UUID):
        query = select(User).filter_by(id=user_id)
        result = await self.session.execute(query)
        user_to_delete = result.scalar_one_or_none()
        if user_to_delete is None:
            raise HTTPException(status_code=404, detail="User not found")
        await self.session.delete(user_to_delete)
    
    async def update_verification(self, email:str):
        query = update(User).filter_by(email=email).values(is_verificated=True)
        await self.session.execute(query)
    
    async def update_password(self, email: str, new_passw: str):
        query = update(User).filter_by(email=email).values(password=new_passw)
        await self.session.execute(query)


