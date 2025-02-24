from datetime import UTC, datetime

# from app.core.config import settings
from fastapi import APIRouter, UploadFile

# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from app.core import SessionDep
from app.core.utils import file_utils

from .dao import HotelImageDAO, RoomImageDAO
from .models import HotelImage, RoomImage
from .schemas import HotelImageFilter, RoomImageFilter

router = APIRouter(
    tags=["Images"],
)


@router.get("/hotel/{hotel_id}/images")
async def get_all_hotel_images(
    hotel_id: int,
    session=SessionDep,
):
    return await HotelImageDAO.get_all(
        session=session,
        filters=HotelImageFilter(
            hotel_id=hotel_id,
        ),
    )


@router.post("/hotel/{hotel_id}/images")
async def add_hotel_image(
    hotel_id: int,
    photo: UploadFile,
    session=SessionDep,
):
    file_path = await file_utils.save_png(
        file=photo,
        filename=f"logo_{datetime.now(UTC).strftime('%Y-%m-%d_%H-%M-%S')}",
        folder=f"hotel_{hotel_id}",
    )
    return await HotelImageDAO.create(
        session=session,
        values=HotelImageFilter(
            hotel_id=hotel_id,
            image=file_path,
        ),
    )


@router.delete("/hotel/{hotel_id}/images/{image_id}")
async def delete_hotel_image(
    hotel_id: int,
    image_id: int,
    session=SessionDep,
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
