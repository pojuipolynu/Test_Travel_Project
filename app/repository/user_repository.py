from repository.base_repository import BaseRepository
from db.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class UserRepository(BaseRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db, model=User)

    async def get_user_by_email(self, user_value: str):
        result = await self.db.execute(select(User).filter(User.email == user_value))
        user = result.scalars().first()
        if user is None:
            return
        return user
    