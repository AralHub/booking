from pydantic import BaseModel


class UserFavoriteBase(BaseModel):
    hotel_id: int


class UserFavoriteRead(UserFavoriteBase):
    id: int


class UserFavoriteCreate(UserFavoriteBase):
    pass


class UserFavoriteCreateInternal(UserFavoriteCreate):
    user_id: int


class UserFavoriteFilter(BaseModel):
    id: int | None = None
    hotel_id: int | None = None
    user_id: int | None = None
