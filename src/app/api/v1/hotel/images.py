from datetime import UTC, datetime

from fastapi import APIRouter, Depends, UploadFile

from app.api.dependencies.hotel import validate_hotel_by_slug
from app.api.dependencies.partner import valid_hotel_admin_by_slug
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings
from app.core.i18n.responses import (
    RESPONSE_MESSAGES,
    BaseResponse,
    DataResponse,
    ListResponse,
)
from app.core.utils import file_utils
from app.dao.hotel.images import HotelImageDAO
from app.schemas.hotel.images import HotelImageRead
from app.schemas.hotel.info import HotelNameRead

router = APIRouter(
    tags=["Hotel Images"],
    prefix=settings.api_v1.hotel_prefix,
)


@router.get(
    "/{hotel_slug}/images",
    response_model=ListResponse[HotelImageRead],
)
async def get_hotel_images(
    hotel_slug: str,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    session=SessionDep,
):
    hotel_images = await HotelImageDAO.get_hotel_images(
        session=session,
        hotel_id=hotel.id,
    )
    if not hotel_images:
        return ListResponse[HotelImageRead](
            data=[],
            total=0,
        )
    return ListResponse[HotelImageRead](
        data=hotel_images,
        total=len(hotel_images),
    )


@router.post(
    "/{hotel_slug}/images",
    response_model=DataResponse[HotelImageRead],
)
async def add_hotel_image(
    hotel_slug: str,
    photo: UploadFile,
    hotel: HotelNameRead = Depends(valid_hotel_admin_by_slug),
    session=TransactionSessionDep,
):

    file_path = await file_utils.save_photo(
        file=photo,
        filename=f"hotel_{datetime.now(UTC).strftime('%Y-%m-%d_%H-%M-%S')}",
        folder=f"hotel_{hotel.id}",
    )
    added_image = await HotelImageDAO.add_hotel_image(
        session=session,
        hotel_id=hotel.id,
        file_path=file_path,
    )
    return DataResponse(
        data=added_image,
        message=RESPONSE_MESSAGES.get(
            "DATA_CREATED",
            "Hotel image created successfully",
        ),
    )


@router.delete(
    "/{hotel_slug}/images/{image_id}",
    response_model=BaseResponse,
)
async def delete_hotel_image(
    hotel_slug: str,
    image_id: int,
    hotel: HotelNameRead = Depends(valid_hotel_admin_by_slug),
    session=TransactionSessionDep,
):
    await HotelImageDAO.delete_hotel_image(
        session=session,
        hotel_id=hotel.id,
        image_id=image_id,
    )
    return BaseResponse(
        success=True,
        message=RESPONSE_MESSAGES.get(
            "DATA_DELETED",
            "Hotel image deleted successfully",
        ),
    )
