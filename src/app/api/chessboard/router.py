from fastapi import APIRouter
from app.api.hotel.models import Hotel, Room
from app.api.booking.models import Booking, BookingStatus
from app.api.room.models import RoomTypeVariant

router = APIRouter()
