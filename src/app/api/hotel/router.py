from datetime import UTC, datetime

from fastapi import APIRouter, UploadFile
from app.core.utils import file_utils
from app.api.images.dao import HotelImageDAO, RoomImageDAO
from app.api.images.schemas import (
    HotelImageFilter,
    RoomImageFilter,
)
from app.api.locations.dao import CityDAO, LocationDAO
from app.api.locations.schemas import (
    LocationCreate,
    LocationCreateInternal,
    LocationFilter,
    LocationUpdate,
    LocationUpdateInternal,
)
from app.api.owner.dao import HotelOwnerDAO, HotelOwnerInfoDAO
from app.api.owner.schemas import (
    HotelOwnerInfoCreate,
    HotelOwnerInfoCreateInternal,
    HotelOwnerInfoFilter,
    HotelOwnerInfoRead,
)
from app.api.room.dao import RoomDAO, RoomTypeVariantDAO, RoomBedConfDAO, BedTypeDAO
from app.api.room.schemas import (
    RoomCreate,
    RoomCreateInternal,
    RoomFilter,
    RoomTypeVariantFilter,
    RoomUpdate,
    RoomBedConfCreate,
    RoomBedConfCreateInternal,
    RoomBedConfFilter,
    BedFilter,
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

# from slugify import slugify
# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from app.core.exceptions.http_exceptions import (
    DuplicateValueException,
    NotFoundException,
)

from .dao import HotelCategoryDAO, HotelDAO
from .schemas import (
    HotelCategoryCreate,
    HotelCategoryFilter,
    HotelCategoryUpdate,
    HotelCreate,
    HotelCreateInternal,
    HotelFilter,
    HotelUpdate,
)

router = APIRouter(
    tags=["Hotels"],
    prefix=settings.api_v1.hotel_prefix,
)


# region Hotel
@router.get("/count")
async def get_hotels_count(
    session=SessionDep,
):
    return await HotelDAO.count(
        session=session,
        filters=None,
    )


@router.post("")
async def create_hotel(
    hotel_create_data: HotelCreate,
    session=TransactionSessionDep,
):
    db_hotel = await HotelDAO.get_one_or_none(
        session=session,
        filters=HotelFilter(
            slug=hotel_create_data.slug,
        ),
    )
    if db_hotel:
        raise DuplicateValueException("Hotel with this slug already exists")
    hotel_data = HotelCreateInternal(
        **hotel_create_data.model_dump(),
        hotel_owner_id=1,
        created_at=datetime.now(UTC),
    )
    return await HotelDAO.create(
        session=session,
        values=hotel_data,
    )


@router.get("/{hotel_id}")
async def get_hotel(
    hotel_id: int,
    session=SessionDep,
):
    return await HotelDAO.get_one_or_none_by_id(
        session=session,
        data_id=hotel_id,
    )


@router.put("/{hotel_id}")
async def update_hotel(
    hotel_update_data: HotelUpdate,
    hotel_id: int,
    session=TransactionSessionDep,
):
    return await HotelDAO.update(
        session=session,
        values=hotel_update_data,
        filters=HotelFilter(
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
        filters=HotelFilter(id=hotel_id),
    )


# endregion


# region Hotel Owner
@router.get("/{hotel_id}/owner")
async def get_hotel_owner(
    hotel_id: int,
    session=SessionDep,
):
    db_hotel_owner = await HotelOwnerDAO.get_one_or_none_by_id(
        session=session,
        data_id=hotel_id,
    )
    if not db_hotel_owner:
        raise NotFoundException("Hotel owner not found")
    return db_hotel_owner


@router.get(
    "/{hotel_id}/owner/info",
    response_model=HotelOwnerInfoRead,
)
async def get_hotel_owner_info(
    hotel_id: int,
    session=TransactionSessionDep,
):
    db_hotel = await HotelDAO.get_one_or_none_by_id(
        session=session,
        data_id=hotel_id,
    )
    if not db_hotel:
        raise NotFoundException("Hotel not found")
    return await HotelOwnerInfoDAO.get_one_or_none(
        session=session,
        filters=HotelOwnerInfoFilter(hotel_id=hotel_id),
    )


@router.post("/{hotel_id}/owner/info")
async def add_hotel_owner_info(
    hotel_id: int,
    hotel_owner_info_create_data: HotelOwnerInfoCreate,
    session=TransactionSessionDep,
):
    db_hotel = await HotelDAO.get_one_or_none_by_id(
        session=session,
        data_id=hotel_id,
    )
    if not db_hotel:
        raise NotFoundException("Hotel not found")

    return await HotelOwnerInfoDAO.create(
        session=session,
        values=HotelOwnerInfoCreateInternal(
            **hotel_owner_info_create_data.model_dump(),
            hotel_id=hotel_id,
        ),
    )


# endregion


# region Hotel Location
@router.get("/hotels/{hotel_id}/location")
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


@router.post("/hotels/{hotel_id}/location")
async def add_hotel_location(
    hotel_id: int,
    location_create_data: LocationCreate,
    session=TransactionSessionDep,
):
    db_city = await CityDAO.get_one_or_none_by_id(
        session=session,
        data_id=location_create_data.city_id,
    )
    if not db_city:
        raise NotFoundException("City not found")
    return await LocationDAO.create(
        session=session,
        values=LocationCreateInternal(
            **location_create_data.model_dump(),
            hotel_id=hotel_id,
        ),
    )


@router.put("/hotels/{hotel_id}/location")
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
    session=TransactionSessionDep,
):
    return await RoomDAO.update(
        session=session,
        values=room_update_data,
        filters=RoomFilter(
            id=room_id,
            hotel_id=hotel_id,
        ),
    )


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
