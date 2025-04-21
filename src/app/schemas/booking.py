from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models.booking import BookingType, BookingStatus

from .field_validation import BOOKING_STATUS_FIELD, BOOKING_STATUS_FIELD_UPDATE


# region Booking Room
class BookedRoomBase(BaseModel):
    room_id: int
    guest_quantity: int = Field(ge=1)


class BookedRoomCreate(BookedRoomBase):
    guest_name: str | None = Field(
        min_length=2,
        max_length=50,
        default=None,
    )


class BookedRoomCreateInternal(BookedRoomCreate):
    booking_id: int
    room_price: float


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
    time: str | None = None
    booking_type: BookingType


class BookingCreateMultipleRoomsInternal(BaseModel):
    check_in_date: date
    check_out_date: date
    special_requests: str | None = None
    total_price: int
    total_days: int
    total_guests: int
    user_id: int
    special_requests: str | None = None
    status: BOOKING_STATUS_FIELD_UPDATE = BookingStatus.BOOKED
    hotel_id: int
    booking_type: BookingType
    payment_method_id: int
    time: str | None = None


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


# region Booking Initial
class RoomInfoBase(BaseModel):
    room_id: int
    guest_quantity: int = Field(ge=1)


class RoomInfoRead(RoomInfoBase):
    uuid: str
    price: float | None = None
    type: str | None = None


class RoomInfoCreate(RoomInfoBase):
    pass


class RoomInfoCreateInternal(RoomInfoRead):
    pass


class BookingInitialBase(BaseModel):
    check_in_date: date
    check_out_date: date
    booking_type: BookingType = BookingType.PERSONAL


class BookingInitialRead(BookingInitialBase):
    uuid: str
    hotel_id: int
    user_id: int
    total_price: float
    total_days: int
    booking_type: BookingType
    rooms_info: list[RoomInfoRead]


class BookingInitialCreate(BookingInitialBase):
    rooms_info: list[RoomInfoCreate]


class BookingInitialCreateInternal(BookingInitialCreate):
    uuid: str
    hotel_id: int
    user_id: int
    total_price: float
    total_days: int
    rooms_info: list[RoomInfoCreateInternal]


# endregion
