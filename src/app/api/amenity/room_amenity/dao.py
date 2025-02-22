# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dao import BaseDAO

from .models import (
    RoomAmenity,
    RoomAmenityCategory,
)


class RoomAmenityCategoryDAO(BaseDAO):
    model = RoomAmenityCategory


class RoomAmenityDAO(BaseDAO):
    model = RoomAmenity
