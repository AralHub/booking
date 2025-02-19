from pydantic import BaseModel


class ReviewBase(BaseModel):
    name: str
    rating: float
    comment: str
    hotel_id: int
    user_id: int


class ReviewRead(ReviewBase):
    id: int


class ReviewCreate(ReviewBase):
    pass


class ReviewCreateInternal(ReviewCreate):
    pass


class ReviewUpdate(BaseModel):
    rating: float | None = None
    comment: str | None = None


class ReviewFilter(BaseModel):
    id: int | None = None
    name: str | None = None
    rating: float | None = None
    comment: str | None = None
    hotel_id: int | None = None
    user_id: int | None = None
