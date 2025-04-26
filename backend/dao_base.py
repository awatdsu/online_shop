from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class BaseDao:

    model = None
    
    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, **filter_by):
        query = select(cls.model).filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalar_one_or_none()

        