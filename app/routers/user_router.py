from fastapi import APIRouter, Depends, status
from schemas.user_schema import UserCreate, UserResponse, SignInRequest, Token

from services.authorization_service import AuthorizationService

from utils.depends import get_authorization_service

router = APIRouter(prefix="/users")

@router.post("/login", response_model=Token, status_code=status.HTTP_201_CREATED)
async def login_user(user_login: SignInRequest, user_service: AuthorizationService = Depends(get_authorization_service)):
    return await user_service.login(user_login)


@router.post("/sign_up", response_model=Token, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate, user_service: AuthorizationService = Depends(get_authorization_service)):
    return await user_service.sign_up(user_create)
