# from sqlalchemy.ext.asyncio import AsyncSession
from app.api.booking.models import Booking
from app.core.dao import BaseDAO


class BookingDAO(BaseDAO):
    model = Booking
