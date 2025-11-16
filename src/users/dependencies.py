from typing import Annotated

from fastapi import Depends

from src.users.interface import IUserService
from src.users.service import get_service

UserServiceDep = Annotated[IUserService, Depends(get_service)]
