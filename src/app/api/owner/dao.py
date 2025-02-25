from sqlalchemy.ext.asyncio import AsyncSession
from .models import HotelOwner, HotelOwnerInfo
from app.core.dao import BaseDAO
from sqlalchemy import select


class HotelOwnerDAO(BaseDAO):
    model = HotelOwner


class HotelOwnerInfoDAO(BaseDAO):
    model = HotelOwnerInfo
