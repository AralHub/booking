from datetime import date

from pydantic import BaseModel, Field

from .field_validation import BOOKING_STATUS_FIELD, BOOKING_STATUS_FIELD_UPDATE


class BookingBase(BaseModel):
    check_in_date: date
    check_out_date: date


class RoomBookingData(BaseModel):
    room_id: int
    guest_quantity: int = Field(ge=1)
    guest_name: str = Field(
        min_length=3,
        max_length=50,
    )


class BookingCreateMultipleRooms(BaseModel):
    check_in_date: date
    check_out_date: date
    rooms_info: list[RoomBookingData]


class BookingCreateMultipleRoomsInternal(BookingCreateMultipleRooms):
    total_price: int
    total_days: int
    user_id: int
    special_requests: str | None = None
    status: BOOKING_STATUS_FIELD_UPDATE


class BookingUpdateInternal(BaseModel):
    status: BOOKING_STATUS_FIELD_UPDATE


class BookingRead(BookingBase):
    id: int
    total_price: int
    total_days: int
    status: BOOKING_STATUS_FIELD
    rooms_info: list[RoomBookingData]


class BookingFilter(BaseModel):
    id: int | None = None
    check_in_date: date | None = None
    check_out_date: date | None = None
    total_price: int | None = None
    room_id: int | None = None
    user_id: int | None = None
