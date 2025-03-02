from datetime import datetime

from pydantic import BaseModel


class BookingBase(BaseModel):
    check_in_date: datetime
    check_in_out: datetime
    room_id: int
    user_id: int


class BookingCreate(BookingBase):
    pass


class BookingCreateInternal(BookingCreate):
    total_price: int


class BookingUpdate(BookingBase):
    pass


class BookingUpdateInternal(BookingUpdate):
    pass


class BookingFilter(BaseModel):
    id: int | None = None
    check_in_date: datetime | None = None
    check_in_out: datetime | None = None
    total_price: int | None = None
    room_id: int | None = None
    user_id: int | None = None
