from pydantic import BaseModel


# region ReviewCategory
class ReviewCategoryBase(BaseModel):
    name: str


class ReviewCategoryRead(ReviewCategoryBase):
    id: int


class ReviewCategoryCreate(ReviewCategoryBase):
    pass


class ReviewCategoryFilter(BaseModel):
    id: int | None = None
    name: str | None = None


# endregion


# region ReviewCategoryRating
class ReviewCategoryRatingBase(BaseModel):
    review_category_id: int
    rating: int


class ReviewCategoryRatingCreate(ReviewCategoryRatingBase):
    pass


class ReviewCategoryCreateInternal(ReviewCategoryRatingCreate):
    review_id: int


# endregion


# region Review
class ReviewBase(BaseModel):
    rating: float
    comment: str


class ReviewRead(ReviewBase):
    id: int


class ReviewCreate(ReviewBase):
    category_ratings: list[ReviewCategoryRatingCreate] | None = None


class ReviewCreateInternal(ReviewCreate):
    hotel_id: int
    user_id: int


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
