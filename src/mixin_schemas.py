from datetime import datetime
from typing import Generic, TypeVar
from pydantic import BaseModel, Field


class CreatedAtMixin(BaseModel):
    created_at: datetime


class Pagination(BaseModel):
    offset: int = Field(gte=0)
    limit: int = Field(ge=0, le=200)


T = TypeVar("T")


class Collection(Pagination, Generic[T]):
    collection: list[T]
    size: int

    def model_post_init(self, __context__=None) -> None:
        self.size = len(self.collection)
