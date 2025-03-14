from datetime import date

from pydantic import BaseModel

from .field_validation import BOOKING_STATUS_FIELD, BOOKING_STATUS_FIELD_UPDATE


class BookingBase(BaseModel):
    check_in_date: date
    check_out_date: date
    room_id: int
    guest_quantity: int


class BookingRead(BookingBase):
    id: int
    status: BOOKING_STATUS_FIELD


class BookingCreate(BookingBase):
    pass


class BookingCreateInternal(BookingCreate):
    total_price: int
    total_days: int
    user_id: int


class BookingUpdateInternal(BaseModel):
    status: BOOKING_STATUS_FIELD_UPDATE


class BookingFilter(BaseModel):
    id: int | None = None
    check_in_date: date | None = None
    check_out_date: date | None = None
    total_price: int | None = None
    room_id: int | None = None
    user_id: int | None = None
