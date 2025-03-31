from pydantic import BaseModel


class HotelRatingBase(BaseModel):
    average_rating: float
    reviews_count: int
    hotel_id: int


class HotelRatingCreateInternal(HotelRatingBase):
    hotel_id: int


class HotelCategoryRatingBase(BaseModel):
    rating: float


class HotelCategoryRatingCreateInternal(HotelCategoryRatingBase):
    hotel_rating_id: int
    review_category_id: int
