from datetime import date

from pydantic import BaseModel


class BookingBase(BaseModel):
    check_in_date: date
    check_out_date: date
    room_id: int
    guest_quantity: int


class BookingCreate(BookingBase):
    pass


class BookingCreateInternal(BookingCreate):
    total_price: int
    total_days: int
    user_id: int


class BookingUpdate(BookingBase):
    pass


class BookingUpdateInternal(BookingUpdate):
    pass


class BookingFilter(BaseModel):
    id: int | None = None
    check_in_date: date | None = None
    check_out_date: date | None = None
    total_price: int | None = None
    room_id: int | None = None
    user_id: int | None = None
