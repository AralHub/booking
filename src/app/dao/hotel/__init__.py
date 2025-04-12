from datetime import UTC, date, datetime

from fastapi import Depends
from sqlalchemy import delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.exceptions.http_exceptions import (
    NotFoundException,
    DuplicateValueException,
)
from app.core.i18n.translations import ErrorCode
from app.core.utils.slug_utils import generate_slug_for_hotel
from app.api.dependencies.hotel import validate_hotel

from app.dao import BaseDAO
from app.dao.hotel.amenities import HotelAmenityDAO
from app.dao.hotel.location import HotelLocationDAO
from app.dao.location import CityDAO
from app.dao.hotel.rating import HotelRatingDAO
from app.dao.hotel.review import ReviewDAO
from app.dao.hotel.category import HotelCategoryDAO
from app.dao.hotel.info import HotelInfoDAO
from app.dao.room import RoomDAO
from app.dao.booking import BookingDAO
from app.dao.hotel.rules import HotelRuleDAO
from app.dao.partner import PartnerDAO
from app.models.hotel.amenities import HotelAmenityAssociation
from app.models.booking import Booking
from app.schemas.hotel.location import (
    LocationCreate,
    LocationFilter,
    LocationUpdate,
)
from app.models.hotel import Hotel
from app.models.room.price import RoomPrice
from app.models.room.types import RoomType
from app.models.hotel.category import HotelCategory
from app.models.hotel.location import HotelLocation
from app.models.booking import BookingStatus
from app.models.room import Room
from app.models.hotel.location import HotelLocation
from app.models.hotel.rating import HotelRating
from app.models.hotel.rating import HotelRating
from app.schemas.location import CityFilter
from app.schemas.hotel import HotelFilter
from app.schemas.hotel.category import HotelCategoryFilter
from app.schemas.hotel.info import HotelInfoFilter, HotelInfoUpdate
from app.schemas.hotel.info import (
    HotelInfoCreateInternal,
    HotelInfoFilter,
    HotelInfoUpdate,
    HotelNameRead,
    HotelNameCreateInternal,
    HotelNameFilter,
    HotelNameUpdate,
)
from app.schemas.hotel.rules import (
    RuleCreateInternal,
    RuleFilter,
    RuleUpdate,
)
from app.schemas.hotel import HotelFullCreate, HotelFullUpdate
from app.schemas.partner import PartnerFilter, PartnerUpdateInternal


class HotelDAO(BaseDAO):
    model = Hotel

    # region Populars
    @classmethod
    async def get_popular_hotels(
        cls,
        session: AsyncSession,
        limit: int,
    ):
        min_price_subquery = (
            select(
                Room.hotel_id,
                func.min(Room.base_price).label("min_price"),
                func.first_value(Room.id)
                .over(partition_by=Room.hotel_id, order_by=Room.base_price)
                .label("cheapest_room_id"),
            )
            .group_by(Room.hotel_id, Room.id)
            .subquery()
        )

        query = (
            select(cls.model)
            .join(HotelRating, cls.model.id == HotelRating.hotel_id)
            .join(min_price_subquery, cls.model.id == min_price_subquery.c.hotel_id)
            .join(Room, Room.id == min_price_subquery.c.cheapest_room_id)
            .options(
                selectinload(cls.model.hotel_rating),
                selectinload(cls.model.location),
                selectinload(
                    cls.model.rooms.and_(
                        Room.id == min_price_subquery.c.cheapest_room_id
                    )
                ).selectinload(Room.room_prices),
            )
            .order_by(HotelRating.average_rating.desc())
            .limit(limit)
        )

        result = await session.execute(query)
        return result.scalars().all()

    # endregion
    # region Full hotel
    @classmethod
    async def get_full_hotel_by_id(
        cls,
        hotel_id: int,
        session: AsyncSession,
    ):
        query = (
            select(cls.model)
            .options(
                selectinload(cls.model.hotel_info),
                selectinload(cls.model.rule),
                selectinload(cls.model.hotel_category),
                selectinload(cls.model.hotel_rating),
            )
            .where(cls.model.id == hotel_id)
        )
        result = await session.execute(query)
        hotel = result.scalar_one_or_none()
        return hotel or None

    # endregion
    # region Create hotel
    @classmethod
    async def create_new_hotel(
        cls,
        hotel_create_data: HotelFullCreate,
        session: AsyncSession,
        hotel_admin_id: int,
    ):
        partner_hotel = await HotelDAO.get_one_or_none(
            session=session,
            filters=HotelFilter(
                hotel_admin_id=hotel_admin_id,
            ),
        )
        if partner_hotel:
            raise DuplicateValueException(
                error_code=ErrorCode.DUPLICATE_VALUE,
            )
        db_hotel_category = await HotelCategoryDAO.get_one_or_none(
            session=session,
            filters=HotelCategoryFilter(id=hotel_create_data.hotel_category_id),
        )

        if not db_hotel_category:
            raise NotFoundException("Hotel category not found")
        db_city = await CityDAO.get_one_or_none(
            session=session,
            filters=CityFilter(
                id=hotel_create_data.city_id,
            ),
        )
        if not db_city:
            raise NotFoundException("City not found")
        generated_slug = await generate_slug_for_hotel(
            session=session,
            name=hotel_create_data.name_en,
        )
        hotel_create_internal = HotelNameCreateInternal(
            name=hotel_create_data.to_dict_name(),
            description=hotel_create_data.to_dict_description(),
            slug=generated_slug,
            hotel_category_id=hotel_create_data.hotel_category_id,
            hotel_admin_id=hotel_admin_id,
            is_active=False,
            created_at=datetime.now(UTC),
        )
        # Create main hotel record
        db_hotel = await HotelDAO.create(
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
        await HotelLocationDAO.add_hotel_location(
            session=session,
            location_create_data=LocationCreate(
                address=hotel_create_data.address,
                city_id=hotel_create_data.city_id,
                longitude=hotel_create_data.longitude,
                latitude=hotel_create_data.latitude,
            ),
            hotel_id=db_hotel.id,
        )
        # Create hotel rules
        await HotelRuleDAO.create(
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
        if hotel_create_data.amenities:
            await HotelAmenityDAO.add_hotel_amenities(
                session=session,
                hotel_id=db_hotel.id,
                amenities=hotel_create_data.amenities,
            )
        await PartnerDAO.update(
            session=session,
            values=PartnerUpdateInternal(
                has_hotel=True,
            ),
            filters=PartnerFilter(
                id=hotel_admin_id,
            ),
        )
        return db_hotel

    # endregion
    # region Update hotel
    @classmethod
    async def update_hotel(
        cls,
        hotel_update_data: HotelFullUpdate,
        session: AsyncSession,
        hotel_id: int,
        hotel: HotelNameRead = Depends(validate_hotel),
    ):
        # Validate hotel category exists
        db_hotel_category = await HotelCategoryDAO.get_one_or_none(
            session=session,
            filters=HotelCategoryFilter(id=hotel_update_data.hotel_category_id),
        )
        if not db_hotel_category:
            raise NotFoundException("Hotel category not found")
        generated_slug = await generate_slug_for_hotel(
            name=hotel_update_data.name,
        )
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
        await HotelLocationDAO.update_hotel_location(
            session=session,
            location_update_data=LocationUpdate(
                address=hotel_update_data.address,
                latitude=hotel_update_data.latitude,
                longitude=hotel_update_data.longitude,
                city_id=hotel_update_data.city_id,
            ),
            hotel_id=hotel_id,
        )
        # Create hotel rules
        await HotelRuleDAO.update(
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
        if hotel_update_data.amenities:
            await HotelAmenityDAO.add_hotel_amenities(
                session=session,
                hotel_id=hotel_id,
                hotel_amenities_data=hotel_update_data.amenities,
            )

        return hotel

    # endregion
