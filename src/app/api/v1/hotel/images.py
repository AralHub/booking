from datetime import UTC, datetime

from fastapi import APIRouter, Depends, UploadFile

from app.api.dependencies.hotel import validate_hotel
from app.api.dependencies.partner import valid_hotel_admin
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
    "/{hotel_id}/images",
    response_model=ListResponse[HotelImageRead],
)
async def get_hotel_images(
    hotel_id: int,
    hotel: HotelNameRead = Depends(validate_hotel),
    session=SessionDep,
):
    hotel_images = await HotelImageDAO.get_hotel_images(
        session=session,
        hotel_id=hotel_id,
    )
    return ListResponse[HotelImageRead](
        data=hotel_images,
        total=len(hotel_images),
    )


@router.post(
    "/{hotel_id}/images",
    response_model=DataResponse[HotelImageRead],
)
async def add_hotel_image(
    hotel_id: int,
    photo: UploadFile,
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    session=TransactionSessionDep,
):

    file_path = await file_utils.save_png(
        file=photo,
        filename=f"hotel_{datetime.now(UTC).strftime('%Y-%m-%d_%H-%M-%S')}",
        folder=f"hotel_{hotel_id}",
    )
    added_image = await HotelImageDAO.add_hotel_image(
        session=session,
        hotel_id=hotel_id,
        file_path=file_path,
    )
    return DataResponse[HotelImageRead](
        data=added_image,
        message=RESPONSE_MESSAGES.get(
            "DATA_CREATED",
            "Hotel image created successfully",
        ),
    )


@router.delete(
    "/{hotel_id}/images/{image_id}",
    response_model=BaseResponse,
)
async def delete_hotel_image(
    hotel_id: int,
    image_id: int,
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    session=TransactionSessionDep,
):
    await HotelImageDAO.delete_hotel_image(
        session=session,
        hotel_id=hotel_id,
        image_id=image_id,
    )
    return BaseResponse(
        success=True,
        message=RESPONSE_MESSAGES.get(
            "DATA_DELETED",
            "Hotel image deleted successfully",
        ),
    )
