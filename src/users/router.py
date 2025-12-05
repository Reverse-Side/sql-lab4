from fastapi import APIRouter, Depends, HTTPException

from src.auth.dependencies import AuthAdmin, AuthUser
from src.mixin_schemas import Collection, Pagination
from src.users.dependencies import UserServiceDep
from src.users.schemas import UserResponce, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

user_not_found = HTTPException(status_code=404, detail="User not found")


@router.get("/me", response_model=UserResponce)
async def get_me(service: UserServiceDep, payload: AuthUser):
    user = await service.get(payload.sub)
    if user:
        return user
    raise user_not_found


@router.patch("/me", response_model=UserResponce)
async def update_me(
    user_update: UserUpdate, service: UserServiceDep, payload: AuthUser
):
    responce = await service.update(_id=payload.sub, data=user_update)
    if responce:
        return responce
    raise user_not_found


@router.get("/{user_id}", response_model=UserResponce)
async def get_users(user_id: int, service: UserServiceDep):
    user = await service.get(_id=user_id)
    if user:
        return user
    raise user_not_found


@router.patch("/{user_id}", response_model=UserResponce)
async def update_users(
    user_id: int, user_update: UserUpdate, service: UserServiceDep, payload: AuthAdmin
):
    responce = await service.update(_id=user_id, data=user_update)
    if responce:
        return responce
    raise user_not_found


@router.get("", response_model=Collection[UserResponce])
async def get_list(service: UserServiceDep, pagin=Depends(Pagination)):
    responce = await service.get_list(pagin)
    if responce:
        return responce
    raise user_not_found
