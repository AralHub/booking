from datetime import UTC, datetime

from fastapi import APIRouter, UploadFile

from app.core import SessionDep, TransactionSessionDep
from app.core.exceptions.http_exceptions import NotFoundException
from app.core.utils import file_utils
from app.dao.hotel.images import HotelImageDAO
from app.dao.room.images import RoomImageDAO
from app.schemas.hotel.images import HotelImageFilter
from app.schemas.room.images import RoomImageFilter

router = APIRouter(
    tags=["Hotel Images"],
)


@router.get("/{hotel_id}/images")
async def get_hotel_images(
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
    if not image:
        raise NotFoundException("Image not found")
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
