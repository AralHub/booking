from datetime import UTC, datetime

# from app.core.config import settings
from fastapi import APIRouter, UploadFile

# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from app.core import SessionDep, TransactionSessionDep
from app.core.exceptions.http_exceptions import NotFoundException
from app.core.utils import file_utils
from app.api.hotel.dao import HotelDAO
from .dao import HotelImageDAO, RoomImageDAO
from .schemas import HotelImageFilter, RoomImageFilter

router = APIRouter(
    tags=["Images"],
)


# region Hotel Images
@router.get("/hotels/{hotel_id}/images")
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


@router.post("/hotels/{hotel_id}/images")
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


@router.delete("/hotels/{hotel_id}/images/{image_id}")
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


# endregion
# region Room Images
@router.get("/hotels/{hotel_id}/rooms/{room_id}/images")
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


@router.post("/hotels/{hotel_id}/rooms/{room_id}/images")
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


@router.delete("/hotels/{hotel_id}/rooms/{room_id}/images/{image_id}")
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
