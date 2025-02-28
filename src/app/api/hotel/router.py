from datetime import UTC, datetime

from fastapi import APIRouter

from app.api.locations.dao import LocationDAO
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
from app.api.room.dao import RoomDAO, RoomTypeVariantDAO
from app.api.room.schemas import (
    RoomCreate,
    RoomCreateInternal,
    RoomTypeVariantFilter,
    RoomUpdate,
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
    session=SessionDep,
):
    pass
    # return await RoomDAO.get_all(
    #     session=session,
    #     filters=None,
    # )


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_room(
    hotel_id: int,
    room_id: int,
    session=SessionDep,
):
    pass
    # return await RoomDAO.get_one_or_none_by_id(
    #     session=session,
    #     data_id=room_id,
    # )


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
            room_type_id=hotel_room_data.room_type_id,
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
    room_update_data: RoomUpdate,
    room_id: int,
    session=TransactionSessionDep,
):
    pass
    # return await RoomDAO.update(
    #     session=session,
    #     values=room_update_data,
    #     filters=RoomFilter(
    #         id=room_id,
    #     ),
    # )


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
