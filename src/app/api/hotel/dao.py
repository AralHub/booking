from datetime import UTC, datetime

from fastapi import Depends
from slugify import slugify as slugify_func
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.amenity.hotel_amenity.dao import HotelAmenityDAO
from app.api.amenity.hotel_amenity.models import HotelAmenityAssociation
from app.api.locations.dao import LocationDAO
from app.api.locations.schemas import (
    LocationCreateInternal,
    LocationFilter,
    LocationUpdate,
)
from app.api.rule.dao import RuleDAO
from app.api.rule.schemas import (
    RuleCreateInternal,
    RuleFilter,
    RuleUpdate,
)
from app.core.dao import BaseDAO
from app.core.exceptions.http_exceptions import NotFoundException

from .dependencies import validate_hotel_id

# from slugify import slugify
# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from .models import Hotel, HotelCategory, HotelInfo
from .schemas import (
    HotelCategoryFilter,
    HotelFullCreate,
    HotelFullUpdate,
    HotelInfoCreateInternal,
    HotelInfoFilter,
    HotelInfoUpdate,
    HotelNameBase,
    HotelNameCreateInternal,
    HotelNameFilter,
    HotelNameUpdate,
)


class HotelCategoryDAO(BaseDAO):
    model = HotelCategory


class HotelInfoDAO(BaseDAO):
    model = HotelInfo


class HotelDAO(BaseDAO):
    model = Hotel

    @classmethod
    async def delete_hotel_all_amenities(
        cls,
        hotel_id: int,
        session: AsyncSession,
    ):
        db_hotel = await session.scalar(
            select(cls.model)
            .where(cls.model.id == hotel_id)
            .options(selectinload(cls.model.hotel_amenities))
        )

        if not db_hotel:
            raise NotFoundException("Hotel not found")

        await session.execute(
            delete(HotelAmenityAssociation).where(
                HotelAmenityAssociation.hotel_id == hotel_id
            )
        )
        await session.commit()

    @classmethod
    async def add_hotel_amenities(
        cls,
        hotel_id: int,
        hotel_amenities_data: list[int],
        session: AsyncSession,
    ):
        query = (
            select(cls.model)
            .options(selectinload(cls.model.hotel_amenities))
            .where(cls.model.id == hotel_id)
        )
        result = await session.execute(query)
        db_hotel = result.scalar_one_or_none()
        if not db_hotel:
            raise NotFoundException("Hotel not found")
        for hotel_amenity_id in hotel_amenities_data:
            hotel_amenity = await HotelAmenityDAO.get_one_or_none_by_id(
                session=session,
                data_id=hotel_amenity_id,
            )
            if hotel_amenity:
                db_hotel.hotel_amenities.append(hotel_amenity)
        await session.commit()

    @classmethod
    async def get_hotel_amenities(cls, hotel_id: int, session: AsyncSession):
        query = (
            select(cls.model)
            .options(selectinload(cls.model.hotel_amenities))
            .where(cls.model.id == hotel_id)
        )
        result = await session.execute(query)
        db_hotel = result.scalar_one_or_none()

        if not db_hotel:
            raise NotFoundException("Hotel not found")
        return db_hotel.hotel_amenities

    @classmethod
    async def create_new_hotel(
        cls,
        hotel_create_data: HotelFullCreate,
        session: AsyncSession,
    ):
        db_hotel_category = await HotelCategoryDAO.get_one_or_none(
            session=session,
            filters=HotelCategoryFilter(id=hotel_create_data.hotel_category_id),
        )

        if not db_hotel_category:
            raise NotFoundException("Hotel category not found")
        generated_slug = slugify_func(hotel_create_data.name)
        hotel_create_internal = HotelNameCreateInternal(
            name=hotel_create_data.name,
            description=hotel_create_data.description,
            slug=generated_slug,
            hotel_category_id=hotel_create_data.hotel_category_id,
            hotel_admin_id=1,  # TODO: Get from current user
            is_active=False,
            created_at=datetime.now(UTC),
        )
        # Create main hotel record
        db_hotel = await cls.create(
            session=session,
            values=hotel_create_internal,
        )
        # Create hotel info
        await HotelInfoDAO.create(
            session=session,
            values=HotelInfoCreateInternal(
                hotel_id=db_hotel.id,
                first_phone_number=hotel_create_data.information_for_guests.first_phone_for_guests,
                second_phone_number=hotel_create_data.information_for_guests.second_phone_for_guests,
                email=hotel_create_data.information_for_guests.email_for_guests,
                site_url=hotel_create_data.information_for_guests.site_url,
            ),
        )
        # Create location record
        await LocationDAO.create(
            session=session,
            values=LocationCreateInternal(
                hotel_id=db_hotel.id,
                address=hotel_create_data.address,
                latitude=hotel_create_data.latitude,
                longitude=hotel_create_data.longitude,
                city_id=hotel_create_data.city_id,
            ),
        )
        # Create hotel rules
        await RuleDAO.create(
            session=session,
            values=RuleCreateInternal(
                hotel_id=db_hotel.id,
                check_in_from=(
                    hotel_create_data.information_for_booking.check_in
                    if hotel_create_data.information_for_booking.check_in
                    else None
                ),
                check_out_from=(
                    hotel_create_data.information_for_booking.check_out
                    if hotel_create_data.information_for_booking.check_out
                    else None
                ),
            ),
        )
        # Add hotel amenities
        if hotel_create_data.facilities:
            await HotelDAO.add_hotel_amenities(
                session=session,
                hotel_id=db_hotel.id,
                hotel_amenities_data=hotel_create_data.facilities,
            )

        return db_hotel

    @classmethod
    async def update_hotel(
        cls,
        hotel_update_data: HotelFullUpdate,
        session: AsyncSession,
        hotel_id: int,
        hotel: HotelNameBase = Depends(validate_hotel_id),
    ):
        # Validate hotel category exists
        db_hotel_category = await HotelCategoryDAO.get_one_or_none(
            session=session,
            filters=HotelCategoryFilter(id=hotel_update_data.hotel_category_id),
        )
        if not db_hotel_category:
            raise NotFoundException("Hotel category not found")
        generated_slug = slugify_func(hotel_update_data.name)
        hotel_update = HotelNameUpdate(
            name=hotel_update_data.name,
            description=hotel_update_data.description,
            slug=generated_slug,
            hotel_category_id=hotel_update_data.hotel_category_id,
        )
        # Create main hotel record
        await cls.update(
            session=session,
            values=hotel_update,
            filters=HotelNameFilter(
                id=hotel_id,
            ),
        )
        # Create hotel info
        await HotelInfoDAO.update(
            session=session,
            values=HotelInfoUpdate(
                first_phone_number=hotel_update_data.information_for_guests.first_phone_for_guests,
                second_phone_number=hotel_update_data.information_for_guests.second_phone_for_guests,
                email=hotel_update_data.information_for_guests.email_for_guests,
                site_url=hotel_update_data.information_for_guests.site_url,
            ),
            filters=HotelInfoFilter(
                hotel_id=hotel_id,
            ),
        )
        # Create location record
        await LocationDAO.update(
            session=session,
            values=LocationUpdate(
                address=hotel_update_data.address,
                latitude=hotel_update_data.latitude,
                longitude=hotel_update_data.longitude,
                city_id=hotel_update_data.city_id,
            ),
            filters=LocationFilter(
                hotel_id=hotel_id,
            ),
        )
        # Create hotel rules
        await RuleDAO.update(
            session=session,
            values=RuleUpdate(
                check_in_from=(
                    hotel_update_data.information_for_booking.check_in
                    if hotel_update_data.information_for_booking.check_in
                    else None
                ),
                check_out_from=(
                    hotel_update_data.information_for_booking.check_out
                    if hotel_update_data.information_for_booking.check_out
                    else None
                ),
            ),
            filters=RuleFilter(hotel_id=hotel_id),
        )
        # Add hotel amenities
        if hotel_update_data.facilities:
            await HotelDAO.add_hotel_amenities(
                session=session,
                hotel_id=hotel_id,
                hotel_amenities_data=hotel_update_data.facilities,
            )

        return hotel
