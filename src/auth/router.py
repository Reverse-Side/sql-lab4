from functools import wraps

from fastapi import APIRouter, HTTPException

from src.auth.dependencies import AuthServiceDep
from src.auth.exceptions import InvalidRefreshToken, LoginError, RegistrationError
from src.auth.schemas import LoginResponce, TokenSchemas, UserLogin, UserRegister

router = APIRouter(prefix="/auth", tags=["Auth"])


def check_invalid_refresh_token(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
        except InvalidRefreshToken:
            raise HTTPException(status_code=403, detail="Invalid refresh token.")
        return result

    return wrapper


@router.post("/register")
async def register_user(data: UserRegister, service: AuthServiceDep) -> LoginResponce:
    try:
        user = await service.register(data)
    except RegistrationError:
        raise HTTPException(
            status_code=400, detail="A user with this email address exists."
        )
    return user


@router.post("/login")
async def login(user: UserLogin, service: AuthServiceDep) -> LoginResponce:
    try:
        token = await service.login(user)
    except LoginError:
        raise HTTPException(status_code=400, detail="Invalid email or password.")
    return token


@router.post("/refresh")
@check_invalid_refresh_token
async def refresh_token(refresh_token: str, service: AuthServiceDep) -> TokenSchemas:
    token = await service.refresh(refresh_token)
    return token


@router.post("/logout")
@check_invalid_refresh_token
async def logout(refresh_token: str, service: AuthServiceDep):
    return await service.logout(refresh_token)
