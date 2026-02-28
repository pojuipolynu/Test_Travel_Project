from schemas.user_schema import SignInRequest, UserCreate
from utils.basic_token_handler import user_token
from repository.user_repository import UserRepository
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import postgres_db
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from schemas.user_schema import UserCreate
from db.models import User
from sqlalchemy import select
import bcrypt

security = HTTPBearer()

class AuthorizationService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def hash_password(self, password: str):
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(pwd_bytes, salt)
        return hashed_password.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str):
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )

    async def get_user_by_email(self, user_email: str):
        user = await self.user_repository.get_user_by_email(user_email)
        return user

    async def create_user(self, user_create: UserCreate):
        if user_create is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data wasn`t given")

        user_check = await self.get_user_by_email(user_create.email)

        if user_check:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Email should be unique")
        
        hashed_password = self.hash_password(user_create.password)
        db_user = User(email=user_create.email, hashed_password=hashed_password)
        created_user = await self.user_repository.create(db_user)
        
        return created_user

    async def sign_up(self, user_create: UserCreate):
        user = await self.create_user(user_create=user_create)
        token = user_token.sign_token(user.email)
        if not token:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate token")
        return {"access_token": token}

    async def checking_user(self, user: SignInRequest):
        user_check = await self.get_user_by_email(user.email)
        if user_check:
            if self.verify_password(user.password, user_check.hashed_password):
                return True
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    async def login(self, user_login: SignInRequest):
        await self.checking_user(user_login)
        token = user_token.sign_token(user_login.email)
        if not token:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate token")
        return {"access_token": token}

    @staticmethod
    async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security), session: AsyncSession = Depends(postgres_db)):
        decoded_token = user_token.decode_token(token.credentials)
        user_check = await session.execute(select(User).filter(User.email==decoded_token.get('email')))
        user_check = user_check.scalars().first()
        if user_check:
            return user_check
        