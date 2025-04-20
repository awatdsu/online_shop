from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select

from backend.dao_base import BaseDao
from backend.db_models import UserToken
from backend.db import session_maker

class UserTokenDao(BaseDao):
    model = UserToken

    @classmethod
    async def add_new_user_token_data(cls, **token_data):
        async with session_maker() as session:
            async with session.begin():
                new_token_data = UserToken(**token_data)
                session.add(new_token_data)
                await session.commit()
                return new_token_data
            
    @classmethod
    async def delete_user_token_data_by_id(cls, token_id: UUID):
        async with session_maker() as session:
            async with session.begin():
                query = select(cls.model).filter_by(id=token_id)
                result = await session.execute(query)
                user_token_to_delete = result.scalar_one_or_none()
                if not user_token_to_delete:
                    raise HTTPException(status_code=404, detail="User token not found")
                await session.delete(user_token_to_delete)
                return
    
    @classmethod
    async def refresh_user_token(cls, user_id: UUID, new_token: str):
        async with session_maker() as session:
            query = select(cls.model).filter_by(user_id=user_id)
            result = await session.execute(query)
            token_data = result.scalar_one_or_none()
            if not token_data:
                raise HTTPException(status_code=404, detail="User token not found")
            token_data.refresh_token = new_token
            await session.commit()
            return token_data
        
    @classmethod
    async def add_device_to_user_data(cls, user_id: UUID, new_device: str):
        async with session_maker() as session:
            query = select(cls.model).filter_by(user_id=user_id)
            result = await session.execute(query)
            token_data = result.scalar_one_or_none()
            if not token_data:
                raise HTTPException(status_code=404, detail="User token not found")
            if new_device not in token_data.devices:
                token_data.devices.append(new_device)
            await session.commit()
            return token_data

    @classmethod
    async def set_device_to_user_data(cls, user_id: UUID, new_device: str):
        async with session_maker() as session:
            query = select(cls.model).filter_by(user_id=user_id)
            result = await session.execute(query)
            token_data = result.scalar_one_or_none()
            if not token_data:
                raise HTTPException(status_code=404, detail="User token not found")
            if new_device not in token_data.devices:
                token_data.devices = [new_device]
            await session.commit()
            return token_data

    @classmethod
    async def remove_device_from_user_data(cls, user_id: UUID, device: str):
        async with session_maker() as session:
            query = select(cls.model).filter_by(user_id=user_id)
            result = await session.execute(query)
            token_data = result.scalar_one_or_none()
            if not token_data:
                raise HTTPException(status_code=404, detail="User token not found")
            token_data.devices.remove(device)
            await session.commit()
            return token_data
        
    @classmethod
    async def get_device_from_user_data(cls, user_id: UUID):
        async with session_maker() as session:
            query = select(cls.model).filter_by(user_id=user_id)
            result = await session.execute(query)
            token_data = result.scalar_one_or_none()
            if not token_data:
                raise HTTPException(status_code=404, detail="User token not found")
            await session.commit()
            return token_data.devices