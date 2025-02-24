from datetime import UTC, datetime

# from app.core.config import settings
from fastapi import APIRouter, UploadFile

# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from app.core import SessionDep
from app.core.utils import file_utils

from .dao import ImageDAO
from .schemas import ImageFilter

router = APIRouter(
    tags=["Images"],
)


@router.get("/hotel/{hotel_id}/images")
async def get_all_hotel_images(
    hotel_id: int,
    session=SessionDep,
):
    return await ImageDAO.get_all(
        session=session,
        filters=ImageFilter(
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
    return await ImageDAO.create(
        session=session,
        values=ImageFilter(
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
    image = await ImageDAO.get_one(
        session=session,
        filters=ImageFilter(
            hotel_id=hotel_id,
            id=image_id,
        ),
    )
    await file_utils.delete_photo(
        photo_path=image.image,
    )
    await ImageDAO.delete(
        session=session,
        filters=ImageFilter(
            hotel_id=hotel_id,
            id=image_id,
        ),
    )
    return {
        "message": "Image deleted successfully",
    }
