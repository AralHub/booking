from datetime import datetime

from pydantic import BaseModel


class BookingBase(BaseModel):
    start_date: datetime
    end_date: datetime
    total_price: int
    room_id: int
    user_id: int


class BookingCreate(BookingBase):
    pass


class BookingCreateInternal(BookingCreate):
    pass


class BookingUpdate(BookingBase):
    pass


class BookingUpdateInternal(BookingUpdate):
    pass


class BookingFilter(BaseModel):
    id: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    total_price: int | None = None
    room_id: int | None = None
    user_id: int | None = None
