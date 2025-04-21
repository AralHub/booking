from fastapi import APIRouter, Depends

from app.api.dependencies.amenities import validate_room_amenity
from app.api.dependencies.user import get_current_superuser
from app.core import SessionDep, TransactionSessionDep
from app.core.i18n.responses import (
    RESPONSE_MESSAGES,
    BaseResponse,
    DataResponse,
    ListResponse,
)
from app.dao.room.amenities import (
    RoomAmenityCategoryDAO,
    RoomAmenityDAO,
)
from app.schemas.room.amenities import (
    RoomAmenityCategoryRead,
    RoomAmenityCreate,
    RoomAmenityCreateInternal,
    RoomAmenityFilter,
    RoomAmenityRead,
    RoomAmenityUpdate,
    RoomAmenityUpdateInternal,
)

router = APIRouter(
    tags=["Superuser Room Amenities"],
    prefix="/room-amenities",
)


@router.get(
    "",
    response_model=ListResponse[RoomAmenityCategoryRead],
)
async def get_all_room_amenities(
    session=SessionDep,
):
    """
    Удобства по категории-удобств комнат
    """
    room_amenities = await RoomAmenityCategoryDAO.get_all_amenities(
        session=session,
    )
    return ListResponse(
        data=room_amenities,
        total=len(room_amenities),
    )


@router.post(
    "/categories/{category_id}/amenities",
    dependencies=[Depends(get_current_superuser)],
    response_model=DataResponse[RoomAmenityRead],
)
async def create_room_amenity(
    category_id: int,
    amenity_create_data: RoomAmenityCreate,
    session=TransactionSessionDep,
):
    created_amenity = await RoomAmenityDAO.create(
        session=session,
        values=RoomAmenityCreateInternal(
            name=amenity_create_data.to_dict_name(),
            room_amenity_category_id=category_id,
        ),
    )
    return DataResponse(
        data=created_amenity,
    )


@router.put(
    "/amenities/{amenity_id}",
    dependencies=[Depends(get_current_superuser)],
    response_model=DataResponse[RoomAmenityRead],
)
async def update_room_amenity(
    category_id: int,
    amenity_id: int,
    amenity_update_data: RoomAmenityUpdate,
    room_amenity: RoomAmenityRead = Depends(validate_room_amenity),
    session=TransactionSessionDep,
):
    """
    Обновить удобство в категории
    """
    updated_amenity = await RoomAmenityDAO.update(
        session=session,
        filters=RoomAmenityFilter(
            id=amenity_id,
            room_amenity_category_id=category_id,
        ),
        values=amenity_update_data,
    )
    return DataResponse(
        data=updated_amenity,
    )


@router.delete(
    "/amenities/{amenity_id}",
    dependencies=[Depends(get_current_superuser)],
    response_model=BaseResponse,
)
async def delete_room_amenity(
    amenity_id: int,
    room_amenity: RoomAmenityRead = Depends(validate_room_amenity),
    session=TransactionSessionDep,
):
    await RoomAmenityDAO.delete(session=session, filters=amenity_id)
    return BaseResponse(
        success=True,
        message=RESPONSE_MESSAGES.DELETE_SUCCESS,
    )
