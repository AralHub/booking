from pydantic import BaseModel


class FavoriteBase(BaseModel):
    hotel_id: int


class FavoriteRead(FavoriteBase):
    id: int


class FavoriteCreate(FavoriteBase):
    pass


class FavoriteCreateInternal(FavoriteCreate):
    user_id: int


class FavoriteFilter(BaseModel):
    id: int | None = None
    hotel_id: int | None = None
    user_id: int | None = None
