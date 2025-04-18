from datetime import date

from pydantic import BaseModel


class ChessBoardBase(BaseModel):
    check_date: date
    available_rooms_count: int


class ChessBoardRead(ChessBoardBase):
    id: int
    room_id: int
    hotel_id: int


class ChessBoardCreate(ChessBoardBase):
    pass


class ChessBoardCreateInternal(ChessBoardCreate):
    room_id: int
    hotel_id: int


class ChessBoardUpdate(BaseModel):
    check_date: date | None = None
    available_rooms_count: int | None = None


class ChessBoardUpdateInternal(ChessBoardUpdate):
    pass


class ChessBoardFilter(BaseModel):
    id: int | None = None
    room_id: int | None = None
    hotel_id: int | None = None
    check_date: date | None = None
    available_rooms_count: int | None = None
