from sqlalchemy.ext.asyncio import AsyncSession
from app.api.booking.models import Booking
from app.core.dao import BaseDAO
from .schemas import BookingCreate


class BookingDAO(BaseDAO):
    model = Booking
