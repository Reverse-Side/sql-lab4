from pydantic import BaseModel, EmailStr, Field, FileUrl


class User(BaseModel):
    nickname: str = Field(min_length=3, max_length=20)


class UserResponce(User):
    id: int = Field(ge=0)
    email: EmailStr

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    nickmame: str | None = Field(default=None, min_length=3, max_length=20)
    email: EmailStr | None = Field(default=None)
