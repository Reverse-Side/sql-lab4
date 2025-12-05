from datetime import datetime, timedelta, timezone

from typing import Any
import jwt
from src.auth.schemas import TokenCreate, TokenInfo
from src.config import settings


class JWTAuthCodec:
    def __init__(self, public_key, private_key, algorithm: str, expire_minutes: int):
        self.__public_key = public_key
        self.__private_key = private_key
        self.__algorithm = algorithm
        self.__expire_minutes = expire_minutes

    def decode(self, token: str | bytes):
        payload = jwt.decode(
            token,
            self.__public_key,
            algorithms=self.__algorithm,
        )
        payload["sub"] = int(payload["sub"])
        payload = TokenInfo(**payload)
        if payload.exp >= datetime.now(timezone.utc):
            return payload
        raise jwt.InvalidTokenError("exipire token")

    def encode(
        self,
        payload: TokenCreate,
        expire_minutes: int | None = None,
    ):
        to_encodes = payload.model_dump()
        to_encodes["sub"] = str(payload.sub)
        now = datetime.now(timezone.utc)
        if expire_minutes:
            expire = now + timedelta(minutes=expire_minutes)
        else:
            expire = now + timedelta(minutes=self.__expire_minutes)

        to_encodes.update(
            exp=expire,
            iat=now,
        )

        return jwt.encode(to_encodes, self.__private_key, self.__algorithm)


def get_jwt_codec():
    s = settings.auth_jwt

    with open(s.public_key_path, "r") as pub_f:
        public_key = pub_f.read()

    with open(s.private_key_path, "r") as priv_f:
        private_key = priv_f.read()

    return JWTAuthCodec(
        public_key=public_key,
        private_key=private_key,
        algorithm=s.algorithm,
        expire_minutes=s.access_token_expire_minutes,
    )
