from pydantic import BaseModel, Field

from app.schemas.field_validation import RATING_FIELD, RATING_FIELD_UPDATE

from .mixins import MultilingualNameBase, MultilingualNameBaseUpdate


# region ReviewCategory
class ReviewCategoryBase(MultilingualNameBase):
    pass


class ReviewCategoryRead(BaseModel):
    id: int
    name: dict[str, str]


class ReviewCategoryCreate(BaseModel):
    name: dict[str, str]


class ReviewCategoryUpdate(MultilingualNameBaseUpdate):
    pass


class ReviewCategoryFilter(BaseModel):
    id: int | None = None


# endregion


# region ReviewCategoryRating
class ReviewCategoryRatingBase(BaseModel):
    review_category_id: int
    rating: RATING_FIELD


class ReviewCategoryRatingCreate(ReviewCategoryRatingBase):
    pass


class ReviewCategoryRatingUpdate(BaseModel):
    review_category_id: int
    rating: RATING_FIELD_UPDATE


class ReviewCategoryRatingCreateInternal(ReviewCategoryRatingCreate):
    review_id: int


class ReviewCategoryRatingUpdateInternal(ReviewCategoryRatingUpdate):
    review_id: int


class ReviewCategoryRatingFilter(BaseModel):
    id: int | None = None
    review_id: int | None = None
    review_category_id: int | None = None
    rating: int | None = None


# endregion


# region Review
class ReviewBase(BaseModel):
    rating: float = Field(ge=1, le=10)
    comment: str


class ReviewRead(ReviewBase):
    id: int
    hotel_id: int
    user_id: int

    class Config:
        from_attributes = True


class ReviewCreate(ReviewBase):
    category_ratings: list[ReviewCategoryRatingCreate] | None = None


class ReviewCreateInternal(ReviewCreate):
    hotel_id: int
    user_id: int


class ReviewUpdate(BaseModel):
    rating: float | None = None
    comment: str | None = None
    category_ratings: list[ReviewCategoryRatingUpdate] | None = None


class ReviewUpdateInternal(ReviewUpdate):
    pass


class ReviewFilter(BaseModel):
    id: int | None = None
    name: str | None = None
    rating: float | None = None
    comment: str | None = None
    hotel_id: int | None = None
    user_id: int | None = None


class HotelReviewSummary(BaseModel):
    average_rating: float
    review_count: int
    category_ratings: dict[str, float]


# endregion
