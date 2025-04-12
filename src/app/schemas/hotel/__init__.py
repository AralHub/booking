from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.hotel.location import LocationRead

from ..field_validation import (
    EMAIL_FIELD,
    EMAIL_FIELD_UPDATE,
    PHONE_NUMBER_FIELD,
    PHONE_NUMBER_FIELD_UPDATE,
    SITE_URL_FIELD_UPDATE,
    TIME_FIELD,
    TIME_FIELD_UPDATE,
)
from ..mixins import (
    MultilingualDescriptionBase,
    MultilingualNameBase,
)


class BookingInformation(BaseModel):
    check_in: TIME_FIELD
    check_out: TIME_FIELD
    star_rating: int | None = None


class GuestInformation(BaseModel):
    email_for_guests: EMAIL_FIELD
    first_phone_for_guests: PHONE_NUMBER_FIELD
    second_phone_for_guests: PHONE_NUMBER_FIELD_UPDATE
    site_url: SITE_URL_FIELD_UPDATE


class HotelFullCreate(
    MultilingualNameBase,
    MultilingualDescriptionBase,
    BaseModel,
):
    hotel_category_id: int = 1
    address: str
    city_id: int
    latitude: float
    longitude: float
    amenities: list[int]
    information_for_booking: BookingInformation
    information_for_guests: GuestInformation


class HotelFullCreateInternal(HotelFullCreate):
    hotel_admin_id: int
    created_at: datetime
    slug: str


class BookingInformationUpdate(BaseModel):
    check_in: TIME_FIELD_UPDATE
    check_out: TIME_FIELD_UPDATE
    star_rating: int | None = None


class GuestInformationUpdate(BaseModel):
    email_for_guests: EMAIL_FIELD_UPDATE
    first_phone_for_guests: PHONE_NUMBER_FIELD_UPDATE
    second_phone_for_guests: PHONE_NUMBER_FIELD_UPDATE
    site_url: SITE_URL_FIELD_UPDATE


class HotelFullUpdate(
    MultilingualNameBase,
    MultilingualDescriptionBase,
    BaseModel,
):
    hotel_category_id: int | None = None
    address: str | None = None
    city_id: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    amenities: list[int] | None = None
    information_for_booking: BookingInformationUpdate
    information_for_guests: GuestInformationUpdate


class HotelFullUpdateInternal(HotelFullUpdate):
    hotel_id: int


class BookingInformationRead(BaseModel):
    check_in: TIME_FIELD
    check_out: TIME_FIELD
    star_rating: int | None = None


class GuestInformationRead(BaseModel):
    email_for_guests: EMAIL_FIELD_UPDATE
    first_phone_for_guests: PHONE_NUMBER_FIELD
    second_phone_for_guests: PHONE_NUMBER_FIELD_UPDATE
    site_url: str | None = None


class HotelFullRead(BaseModel):
    id: int
    name: dict[str, str]
    hotel_category_id: int
    description: dict[str, str] | None = None
    location: LocationRead
    city: str | None = None
    amenities: list[int]
    information_for_booking: BookingInformationRead
    information_for_guests: GuestInformationRead
    created_at: datetime
    updated_at: datetime | None = None
    slug: str | None = None
    model_config = ConfigDict(from_attributes=True)


class HotelSearch(BaseModel):
    city: str = "tashkent"
    check_in: date
    check_out: date
    guests: list[int]
    price_min: int | None = None
    price_max: int | None = None
    max_distance_to_center: int = None
    amenities: list[int] = []


class HotelSearchResult(BaseModel):
    id: int
    name: dict
    description: dict
    slug: str
    category: Optional[dict] = None
    location: Optional[dict] = None
    reviews_count: int = 0
    rating: float | None = None
    images: list[str] | None = []
    available_rooms: list[dict] = []
    min_price: float | None = None
    guests: int | None = None


class HotelFilter(BaseModel):
    id: int | None = None
    hotel_admin_id: int | None = None
