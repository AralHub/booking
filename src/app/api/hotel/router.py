import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, UploadFile
from slugify import slugify as slugify_func

from app.api.images.dao import HotelImageDAO, RoomImageDAO
from app.api.images.schemas import (
    HotelImageFilter,
    RoomImageFilter,
)
from app.api.locations.dao import LocationDAO
from app.api.locations.schemas import (
    LocationCreate,
    LocationCreateInternal,
    LocationFilter,
    LocationUpdate,
    LocationUpdateInternal,
)
from app.api.review.dao import ReviewCategoryRatingDAO, ReviewDAO
from app.api.review.schemas import (
    ReviewCategoryCreateInternal,
    ReviewCreate,
    ReviewCreateInternal,
)
from app.api.room.dao import BedTypeDAO, RoomBedConfDAO, RoomDAO, RoomTypeVariantDAO
from app.api.room.schemas import (
    BedFilter,
    RoomBedConfCreate,
    RoomBedConfCreateInternal,
    RoomBedConfFilter,
    RoomCreate,
    RoomCreateInternal,
    RoomFilter,
    RoomTypeVariantFilter,
    RoomUpdate,
    RoomUpdateInternal,
)
from app.api.rule.dao import RuleDAO
from app.api.rule.schemas import (
    RuleCreate,
    RuleCreateInternal,
    RuleFilter,
    RuleUpdate,
    RuleUpdateInternal,
)
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings
from app.core.exceptions.http_exceptions import (
    NotFoundException,
)
from app.core.utils import file_utils
from app.core.utils.parse_date import parse_time

# from slugify import slugify
# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from .dao import HotelCategoryDAO, HotelDAO, HotelInfoDAO
from .dependencies import validate_hotel_id
from .schemas import (
    HotelCategoryCreate,
    HotelCategoryFilter,
    HotelCategoryUpdate,
    HotelFullCreate,
    HotelFullUpdate,
    HotelInfoCreate,
    HotelInfoCreateInternal,
    HotelInfoFilter,
    HotelInfoRead,
    HotelInfoUpdate,
    HotelInfoUpdateInternal,
    HotelNameBase,
    HotelNameCreateInternal,
    HotelNameFilter,
)

logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["Hotels"],
    prefix=settings.api_v1.hotel_prefix,
)


# region Hotel
@router.get("/search")
async def search_hotels(session=SessionDep):
    pass
    # parsed_check_in = parse_date(check_in)
    # parsed_check_out = parse_date(check_out)

    # return await HotelDAO.find_hotels(
    #     session=session,
    #     city_id=city_id,
    #     check_in_date=parsed_check_in,
    #     check_out_date=parsed_check_out,
    #     rooms=rooms,
    # )


@router.post("/")
async def create_hotel(
    hotel_create_data: HotelFullCreate,
    session=TransactionSessionDep,
):
    # Validate hotel category exists
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
                parse_time(hotel_create_data.information_for_booking.check_in)
                if hotel_create_data.information_for_booking.check_in
                else None
            ),
            check_out_from=(
                parse_time(hotel_create_data.information_for_booking.check_out)
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


@router.put("/{hotel_id}")
async def update_hotel(
    hotel_update_data: HotelFullUpdate,
    hotel_id: int,
    session=TransactionSessionDep,
):
    return await HotelDAO.update(
        session=session,
        values=hotel_update_data,
        filters=HotelNameFilter(
            id=hotel_id,
        ),
    )


@router.delete("/{hotel_id}")
async def delete_hotel(
    hotel_id: int,
    session=TransactionSessionDep,
):
    return await HotelDAO.delete(
        session=session,
        filters=HotelNameFilter(id=hotel_id),
    )


# endregion


# region Hotel Info


@router.get(
    "/{hotel_id}/info",
    response_model=HotelInfoRead,
)
async def get_hotel_admin_info(
    hotel_id: int,
    hotel: HotelNameBase = Depends(validate_hotel_id),
    session=TransactionSessionDep,
):
    return await HotelInfoDAO.get_one_or_none(
        session=session,
        filters=HotelInfoFilter(hotel_id=hotel_id),
    )


@router.post("/{hotel_id}/info")
async def add_hotel_admin_info(
    hotel_id: int,
    hotel_info_create_data: HotelInfoCreate,
    hotel: HotelNameBase = Depends(validate_hotel_id),
    session=TransactionSessionDep,
):

    return await HotelInfoDAO.create(
        session=session,
        values=HotelInfoCreateInternal(
            **hotel_info_create_data.model_dump(),
            hotel_id=hotel_id,
        ),
    )


@router.put("/{hotel_id}/info")
async def update_hotel_info(
    hotel_id: int,
    hotel_info_update_data: HotelInfoUpdate,
    hotel: HotelNameBase = Depends(validate_hotel_id),
    session=TransactionSessionDep,
):
    return await HotelInfoDAO.update(
        session=session,
        values=HotelInfoUpdateInternal(
            **hotel_info_update_data.model_dump(),
            hotel_id=hotel_id,
        ),
        filters=HotelInfoFilter(
            hotel_id=hotel_id,
        ),
    )


# endregion


# region Hotel Location
@router.get("/location/{city_id}")
async def get_hotels_by_city_id(
    city_id: int,
    session=SessionDep,
):
    db_hotels = await HotelDAO.get_all(
        session=session,
        filters=HotelNameFilter(
            city_id=city_id,
        ),
    )
    return db_hotels


@router.get("/{hotel_id}/location")
async def get_hotel_location(
    hotel_id: int,
    session=SessionDep,
):
    db_hotel_location = await LocationDAO.get_one_or_none(
        session=session,
        filters=LocationFilter(
            hotel_id=hotel_id,
        ),
    )
    if not db_hotel_location:
        raise NotFoundException("Hotel location not found")
    return db_hotel_location


@router.post("/{hotel_id}/location")
async def add_hotel_location(
    hotel_id: int,
    location_create_data: LocationCreate,
    session=TransactionSessionDep,
):
    return await LocationDAO.add_hotel_location(
        session=session,
        values=LocationCreateInternal(
            **location_create_data.model_dump(
                exclude_none=True,
                excluce_unset=True,
            ),
            hotel_id=hotel_id,
        ),
    )


@router.put("/{hotel_id}/location")
async def update_hotel_location(
    hotel_id: int,
    location_update_data: LocationUpdate,
    session=TransactionSessionDep,
):
    return await LocationDAO.update(
        session=session,
        values=LocationUpdateInternal(
            **location_update_data.model_dump(),
        ),
        filters=LocationFilter(
            hotel_id=hotel_id,
        ),
    )


# endregion
# region Hotel Amenity
@router.get("/{hotel_id}/amenities")
async def get_hotel_amenities(
    hotel_id: int,
    session=SessionDep,
):
    return await HotelDAO.get_hotel_amenities(
        session=session,
        hotel_id=hotel_id,
    )


@router.post("/{hotel_id}/amenities")
async def add_hotel_amenities(
    hotel_id: int,
    hotel_amenities_data: list[int],
    session=TransactionSessionDep,
):
    await HotelDAO.add_hotel_amenities(
        session=session,
        hotel_id=hotel_id,
        hotel_amenities_data=hotel_amenities_data,
    )
    return {
        "message": "Amenities added successfully",
    }


# endregion


# region Hotel Rooms
@router.get("/{hotel_id}/rooms")
async def get_all_rooms(
    hotel_id: int,
    session=SessionDep,
):
    return await RoomDAO.get_all(
        session=session,
        filters=RoomFilter(
            hotel_id=hotel_id,
        ),
    )


@router.get("/{hotel_id}/rooms/types")
async def get_room_categories(
    hotel_id: int,
    session=SessionDep,
):
    return await RoomDAO.get_hotel_room_types(
        session=session,
        hotel_id=hotel_id,
    )


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_room(
    hotel_id: int,
    room_id: int,
    session=SessionDep,
):
    return await RoomDAO.get_one_or_none(
        session=session,
        filters=RoomFilter(
            hotel_id=hotel_id,
            id=room_id,
        ),
    )


@router.post("/{hotel_id}/rooms")
async def add_room(
    hotel_id: int,
    hotel_room_data: RoomCreate,
    session=TransactionSessionDep,
):
    db_room_type_varinat = await RoomTypeVariantDAO.get_one_or_none(
        session=session,
        filters=RoomTypeVariantFilter(
            id=hotel_room_data.room_type_variant_id,
        ),
    )
    if not db_room_type_varinat:
        raise NotFoundException("Room type variant not found")
    hotel_room_create_data = RoomCreateInternal(
        **hotel_room_data.model_dump(),
        hotel_id=hotel_id,
    )
    await RoomDAO.create(
        session=session,
        values=hotel_room_create_data,
    )


@router.put("/{hotel_id}/rooms/{room_id}")
async def update_room(
    hotel_id: int,
    room_id: int,
    room_update_data: RoomUpdate,
    hotel: HotelNameBase = Depends(validate_hotel_id),
    session=TransactionSessionDep,
):
    updated_row_count = await RoomDAO.update(
        session=session,
        values=RoomUpdateInternal(
            **room_update_data.model_dump(
                exclude_none=True,
            )
        ),
        filters=RoomFilter(
            id=room_id,
            hotel_id=hotel_id,
        ),
    )
    if updated_row_count == 0:
        raise NotFoundException("Room not found")
    return {
        "message": "Room updated successfully",
    }


# region Room Beds
@router.get("/{hotel_id}/rooms/{room_id}/beds")
async def get_room_beds(
    hotel_id: int,
    room_id: int,
    session=SessionDep,
):
    return await RoomBedConfDAO.get_all(
        session=session,
        filters=RoomBedConfFilter(
            room_id=room_id,
        ),
    )


@router.post("/{hotel_id}/rooms/{room_id}/beds")
async def add_room_beds(
    hotel_id: int,
    room_id: int,
    room_bed_conf: RoomBedConfCreate,
    session=TransactionSessionDep,
):

    for bed_conf in room_bed_conf.bed_configurations:
        bed_type = await BedTypeDAO.get_one_or_none(
            session=session,
            filters=BedFilter(id=bed_conf.bed_type_id),
        )
        if not bed_type:
            raise NotFoundException(f"Bed type {bed_conf.bed_type_id} not found")
        bed_conf_create_data = RoomBedConfCreateInternal(
            room_id=room_id,
            **bed_conf.model_dump(),
        )
        print(bed_conf_create_data)
        await RoomBedConfDAO.create(
            session=session,
            values=bed_conf_create_data,
        )
    return {
        "message": "Beds added successfully",
    }


# endregion


# region Room Amenities
@router.post("/{hotel_id}/rooms/{room_id}/amenities")
async def add_room_amenities(
    hotel_id: int,
    room_id: int,
    room_amenities_list: list[int],
    session=TransactionSessionDep,
):
    pass
    # await RoomDAO.add_hotel_amenities(
    #     session=session,
    #     hotel_id=hotel_id,
    #     room_id=room_id,
    #     room_amenities_list=room_amenities_list,
    # )
    return {
        "message": "Amenities added successfully",
    }


# endregion

# endregion


# region Hotel Images
@router.get("/{hotel_id}/images")
async def get_all_hotel_images(
    hotel_id: int,
    session=SessionDep,
):
    db_hotel_images = await HotelImageDAO.get_all(
        session=session,
        filters=HotelImageFilter(
            hotel_id=hotel_id,
        ),
    )
    if not db_hotel_images:
        raise NotFoundException("Hotel doesn't have any images")
    return db_hotel_images


@router.post("/{hotel_id}/images")
async def add_hotel_image(
    hotel_id: int,
    photo: UploadFile,
    session=TransactionSessionDep,
):
    file_path = await file_utils.save_png(
        file=photo,
        filename=f"hotel_{datetime.now(UTC).strftime('%Y-%m-%d_%H-%M-%S')}",
        folder=f"hotel_{hotel_id}",
    )
    return await HotelImageDAO.create(
        session=session,
        values=HotelImageFilter(
            hotel_id=hotel_id,
            image=file_path,
        ),
    )


@router.delete("/{hotel_id}/images/{image_id}")
async def delete_hotel_image(
    hotel_id: int,
    image_id: int,
    session=TransactionSessionDep,
):
    image = await HotelImageDAO.get_one(
        session=session,
        filters=HotelImageFilter(
            hotel_id=hotel_id,
            id=image_id,
        ),
    )
    await file_utils.delete_photo(
        photo_path=image.image,
    )
    await HotelImageDAO.delete(
        session=session,
        filters=HotelImageFilter(
            hotel_id=hotel_id,
            id=image_id,
        ),
    )
    return {
        "message": "Image deleted successfully",
    }


@router.get("/{hotel_id}/rooms/{room_id}/images")
async def get_all_room_images(
    hotel_id: int,
    room_id: int,
    session=SessionDep,
):
    return await RoomImageDAO.get_all(
        session=session,
        filters=RoomImageFilter(
            hotel_id=hotel_id,
            room_id=room_id,
        ),
    )


@router.post("/{hotel_id}/rooms/{room_id}/images")
async def add_room_image(
    hotel_id: int,
    room_id: int,
    photo: UploadFile,
    session=TransactionSessionDep,
):
    file_path = await file_utils.save_png(
        file=photo,
        filename=f"room_{datetime.now(UTC).strftime('%Y-%m-%d_%H-%M-%S')}",
        folder=f"room_{room_id}",
    )
    return await RoomImageDAO.create(
        session=session,
        values=RoomImageFilter(
            hotel_id=hotel_id,
            room_id=room_id,
            image=file_path,
        ),
    )


@router.delete("/{hotel_id}/rooms/{room_id}/images/{image_id}")
async def delete_room_image(
    hotel_id: int,
    room_id: int,
    image_id: int,
    session=TransactionSessionDep,
):
    # image = await RoomImageDAO.get_one(
    #     session=session,
    #     filters=RoomImageFilter(
    #         hotel_id=hotel_id,
    #         room_id=room_id,
    #         id=image_id,
    #     ),
    # )
    pass


# endregion

# region Hotel Rules


@router.get("/{hotel_id}/rules")
async def get_hotel_rule(
    hotel_id: int,
    session=SessionDep,
):
    return await RuleDAO.get_one_or_none(
        session=session,
        filters=RuleFilter(hotel_id=hotel_id),
    )


@router.post("/{hotel_id}/rules")
async def add_hotel_rule(
    hotel_id: int,
    rule_create_data: RuleCreate,
    session=TransactionSessionDep,
):
    return await RuleDAO.create(
        session=session,
        values=RuleCreateInternal(
            **rule_create_data.model_dump(),
            hotel_id=hotel_id,
        ),
    )


@router.put("/{hotel_id}/rules")
async def update_hotel_rule(
    hotel_id: int,
    rule_update_data: RuleUpdate,
    session=TransactionSessionDep,
):
    return await RuleDAO.update(
        session=session,
        values=RuleUpdateInternal(
            **rule_update_data.model_dump(),
        ),
        filters=RuleFilter(
            hotel_id=hotel_id,
        ),
    )


# endregion


# region Hotel Reviews
@router.get("/{hotel_id}/reviews")
async def get_hotel_reviews(
    hotel_id: int,
    hotel: HotelNameBase = Depends(validate_hotel_id),
    session=SessionDep,
):
    return await ReviewDAO.get_all_hotel_reviews(
        session=session,
        hotel_id=hotel_id,
    )


@router.post("/{hotel_id}/reviews")
async def create_hotel_reviews(
    hotel_id: int,
    review_create_data: ReviewCreate,
    hotel: HotelNameBase = Depends(validate_hotel_id),
    session=TransactionSessionDep,
):

    craeted_review = await ReviewDAO.create(
        session=session,
        values=ReviewCreateInternal(
            **review_create_data.model_dump(
                exclude={
                    "category_ratings",
                }
            ),
            hotel_id=hotel_id,
            user_id=5,
        ),
    )
    if len(review_create_data.category_ratings) > 0:
        for review_category_rating in review_create_data.category_ratings:
            review_category_rating_create_data = ReviewCategoryCreateInternal(
                review_category_id=review_category_rating.review_category_id,
                rating=review_category_rating.rating,
                review_id=craeted_review.id,
            )

        await ReviewCategoryRatingDAO.create(
            session=session,
            values=review_category_rating_create_data,
        )
    return craeted_review


# endregion


# region Hotel Category
@router.get("/categories")
async def get_hotel_categories(
    session=SessionDep,
):
    return await HotelCategoryDAO.get_all(
        session=session,
        filters=None,
    )


@router.post("/categories")
async def create_hotel_category(
    hotel_category_create_data: HotelCategoryCreate,
    session=TransactionSessionDep,
):
    return await HotelCategoryDAO.create(
        session=session,
        values=hotel_category_create_data,
    )


@router.put("/categories/{category_id}")
async def update_hotel_category(
    category_update_data: HotelCategoryUpdate,
    category_id: int,
    session=TransactionSessionDep,
):
    return await HotelCategoryDAO.update(
        session=session,
        values=category_update_data,
        filters=HotelCategoryFilter(id=category_id),
    )


@router.delete("/categories/{category_id}")
async def delete_hotel_category(
    category_id: int,
    session=TransactionSessionDep,
):
    return await HotelCategoryDAO.delete(
        session=session,
        filters=HotelCategoryFilter(id=category_id),
    )


# endregion
