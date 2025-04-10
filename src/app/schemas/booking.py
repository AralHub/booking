from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from .field_validation import BOOKING_STATUS_FIELD, BOOKING_STATUS_FIELD_UPDATE
from app.models.booking import BookingType


# region Booking Room
class BookedRoomBase(BaseModel):
    room_id: int
    guest_quantity: int = Field(ge=1)
    guest_name: str = Field(
        min_length=2,
        max_length=50,
    )


class BookedRoomCreate(BookedRoomBase):
    pass


class BookedRoomCreateInternal(BookedRoomCreate):
    booking_id: int


class BookedRoomgRead(BookedRoomBase):
    id: int
    price: float

    model_config = ConfigDict(from_attributes=True)


# endregion


# region Base
class BookingBase(BaseModel):
    check_in_date: date
    check_out_date: date


class BookingCreateMultipleRooms(BaseModel):
    check_in_date: date
    check_out_date: date
    rooms_info: list[BookedRoomCreate]
    special_requests: str | None = None
    payment_method_id: int


class BookingCreateMultipleRoomsInternal(BaseModel):
    check_in_date: date
    check_out_date: date
    special_requests: str | None = None
    total_price: int
    total_days: int
    user_id: int
    special_requests: str | None = None
    status: BOOKING_STATUS_FIELD_UPDATE
    hotel_id: int
    booking_type: BookingType
    payment_method_id: int


class BookingUpdateInternal(BaseModel):
    status: BOOKING_STATUS_FIELD_UPDATE


class BookingRead(BookingBase):
    id: int
    hotel_id: int
    total_price: int
    total_days: int
    status: BOOKING_STATUS_FIELD
    rooms_info: list[BookedRoomgRead]
    special_requests: str | None = None


class BookingFilter(BaseModel):
    id: int | None = None
    check_in_date: date | None = None
    check_out_date: date | None = None
    total_price: int | None = None
    user_id: int | None = None
    hotel_id: int | None = None


# endregion
