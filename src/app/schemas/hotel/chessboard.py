from datetime import date

from pydantic import BaseModel


class ChessBoardBase(BaseModel):
    room_type_id: int
    check_date: date
    price: float | None = None
    available_rooms: int
    is_closed: bool


class ChessBoardCreate(ChessBoardBase):
    pass


class ChessBoardUpdate(ChessBoardBase):
    pass


class ChessBoardFilter(BaseModel):
    id: int | None = None
    room_type_id: int | None = None
    check_date: date | None = None
    price: float | None = None
    available_rooms: int | None = None
    is_closed: bool | None = None
