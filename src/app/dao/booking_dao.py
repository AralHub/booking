from sqlalchemy.ext.asyncio import AsyncSession
from app.api.hotel.models.hotel import Hotel
from app.api.booking.models import Booking
from app.core.exceptions.http_exceptions import NotFoundException
from app.api.user.functions.utils import decode_jwt
from datetime import UTC, datetime
from .base_dao import BaseDAO


class BookingDAO(BaseDAO):
    model = Booking
