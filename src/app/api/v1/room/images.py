from datetime import UTC, datetime

from fastapi import APIRouter, UploadFile

from app.core import SessionDep, TransactionSessionDep
from app.core.exceptions.http_exceptions import NotFoundException
from app.core.utils import file_utils
from app.dao.room.images import RoomImageDAO
from app.schemas.room.images import RoomImageFilter

router = APIRouter(
    tags=["Room Images"],
)


@router.get("/{hotel_id}/rooms/{room_id}/images")
async def get_room_images(
    hotel_id: int,
    room_id: int,
    session=SessionDep,
):
    db_room_images = await RoomImageDAO.get_all(
        session=session,
        filters=RoomImageFilter(
            hotel_id=hotel_id,
            room_id=room_id,
        ),
    )
    if not db_room_images:
        raise NotFoundException("Hotel doesn't have any images")
    return db_room_images


@router.post("/{hotel_id}/rooms/{room_id}/images")
async def add_room_image(
    hotel_id: int,
    room_id: int,
    photo: UploadFile,
    session=TransactionSessionDep,
):
    file_path = await file_utils.save_photo(
        file=photo,
        filename=f"room_{datetime.now(UTC).strftime('%Y-%m-%d_%H-%M-%S')}",
        folder=f"hotel_{hotel_id}",
    )
    return await RoomImageDAO.create(
        session=session,
        values=RoomImageFilter(
            room_id=room_id,
            image=file_path,
        ),
    )


@router.delete("/{hotel_id}/rooms/images/{image_id}")
async def delete_room_image(
    hotel_id: int,
    room_id: int,
    image_id: int,
    session=TransactionSessionDep,
):
    image = await RoomImageDAO.get_one_or_none_by_id(
        session=session,
        data_id=image_id,
    )
    if not image:
        raise NotFoundException("Image not found")
    await file_utils.delete_photo(
        photo_path=image.image,
    )
    await RoomImageDAO.delete(
        session=session,
        filters=RoomImageFilter(
            id=image_id,
        ),
    )
