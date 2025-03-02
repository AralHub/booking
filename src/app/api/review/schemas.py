from pydantic import BaseModel


# region Review
class ReviewBase(BaseModel):
    name: str
    rating: float
    comment: str
    hotel_id: int
    user_id: int
    category_ratings: dict[int, float]


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


# endregion


# region ReviewCategory
class ReviewCategoryBase(BaseModel):
    name: str


# endregion


# region ReviewCategoryRating
class ReviewCategoryRatingBase(BaseModel):
    review_id: int
    review_category_id: int
    rating: float


# endregion
