from datetime import UTC, datetime

from fastapi import APIRouter, Depends, UploadFile

from app.api.dependencies.hotel import validate_hotel_by_slug
from app.api.dependencies.partner import valid_hotel_admin_by_slug
from app.core import SessionDep, TransactionSessionDep
from app.core.exceptions.http_exceptions import NotFoundException
from app.core.i18n.responses import (
    RESPONSE_MESSAGES,
    BaseResponse,
    DataResponse,
)
from app.core.i18n.translations import ErrorCode
from app.core.utils import file_utils
from app.dao.room.images import RoomImageDAO
from app.schemas.hotel.info import HotelNameRead
from app.schemas.room.images import RoomImageFilter, RoomImageRead

router = APIRouter(
    prefix="/hotels",
    tags=["Hotel Room Images"],
)


@router.get(
    "/{hotel_slug}/rooms/{room_id}/images",
)
async def get_room_images(
    hotel_slug: str,
    room_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    session=SessionDep,
):
    db_room_images = await RoomImageDAO.get_room_images(
        session=session,
        hotel_id=hotel.id,
        room_id=room_id,
    )
    if not db_room_images:
        return {
            "data": [],
            "total": 0,
        }
    return {
        "data": db_room_images,
        "total": len(db_room_images),
    }


@router.post(
    "/{hotel_slug}/rooms/{room_id}/images",
    response_model=BaseResponse,
)
async def add_room_image(
    hotel_slug: int,
    room_id: int,
    photo: UploadFile,
    hotel: HotelNameRead = Depends(valid_hotel_admin_by_slug),
    session=TransactionSessionDep,
):
    file_path = await file_utils.save_photo(
        file=photo,
        filename=f"room_{datetime.now(UTC).strftime('%Y-%m-%d_%H-%M-%S')}",
        folder=f"hotel_{hotel.id}",
    )
    await RoomImageDAO.add_room_image(
        session=session,
        room_id=room_id,
        file_path=file_path,
    )
    return BaseResponse(
        success=True,
        message=RESPONSE_MESSAGES.get(
            "DATA_CREATED",
            "Room image created successfully",
        ),
    )


@router.delete(
    "/{hotel_slug}/rooms/images/{image_id}",
    response_model=BaseResponse,
)
async def delete_room_image(
    hotel_slug: int,
    room_id: int,
    image_id: int,
    hotel: HotelNameRead = Depends(valid_hotel_admin_by_slug),
    session=TransactionSessionDep,
):
    image = await RoomImageDAO.get_one_or_none_by_id(
        session=session,
        data_id=image_id,
    )
    if not image:
        raise NotFoundException(
            error_code=ErrorCode.NOT_FOUND,
        )
    await file_utils.delete_photo(
        photo_path=image.image,
    )
    await RoomImageDAO.delete(
        session=session,
        filters=RoomImageFilter(
            id=image_id,
        ),
    )
    return BaseResponse(
        success=True,
        message=RESPONSE_MESSAGES.get(
            "DATA_DELETED",
            "Hotel image deleted successfully",
        ),
    )
