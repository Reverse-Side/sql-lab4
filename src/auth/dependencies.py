from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth.exceptions import AuthenticationError
from src.auth.interface import IAuthService
from src.auth.schemas import TokenInfo
from src.auth.service import get_user_servise

AuthServiceDep = Annotated[IAuthService, Depends(get_user_servise)]

bearer = HTTPBearer()


# Базова функція: отримує токен і повертає TokenInfo або викликає 401
def get_token_info(
    service: AuthServiceDep, creds: HTTPAuthorizationCredentials = Depends(bearer)
) -> TokenInfo:
    """Перевіряє дійсність токена і повертає payload (TokenInfo)."""
    try:
        token = creds.credentials
        token_info = service.auth(token)

        # Якщо токен не пройшов перевірку (TokenInfo = None), це 401
        if token_info is None:
            raise HTTPException(
                status_code=401, detail="Invalid credentials or token expired"
            )

        return token_info

    except AuthenticationError:
        # Якщо виникла помилка під час обробки токена, це також 401
        raise HTTPException(status_code=401, detail="Invalid authentication token")


# AuthAny: Будь-який аутентифікований користувач (Адмін чи Звичайний)
AuthUser = Annotated[TokenInfo, Depends(get_token_info)]


# AuthAdmin: Користувач повинен бути адміністратором
def get_admin(token_info: AuthUser) -> TokenInfo:
    if not token_info.is_admin:
        raise HTTPException(status_code=403, detail="Only admin access allowed")

    return token_info


# AuthAdmin: Залежність для адміністратора
AuthAdmin = Annotated[TokenInfo, Depends(get_admin)]
