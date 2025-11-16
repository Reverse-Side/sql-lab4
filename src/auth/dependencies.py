from typing import Annotated
from fastapi import Depends, HTTPException
from src.auth.exceptions import AuthenticationError
from src.auth.interface import IAuthService
from src.auth.schemas import TokenInfo
from src.auth.service import get_user_servise
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

AuthServiceDep = Annotated[IAuthService, Depends(get_user_servise)]

bearer = HTTPBearer()


def get_auth(
    service: AuthServiceDep, creds: HTTPAuthorizationCredentials = Depends(bearer)
):
    try:
        token = creds.credentials
        token_info = service.auth(token)
        if token_info is None:
            raise HTTPException(403, detail="Auth not user")
        return token_info
    except AuthenticationError:
        raise HTTPException(403, detail="Auth not user")


AuthUser = Annotated[TokenInfo, Depends(get_auth)]


def get_admin(user: AuthUser) -> TokenInfo:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Only admin")

    return user


AuthAdmin = Annotated[TokenInfo, Depends(get_admin)]
