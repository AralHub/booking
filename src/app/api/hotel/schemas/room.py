from pydantic import BaseModel


class RoomFilter(BaseModel):
    id: int | None = None
    hotel_id: int | None = None
