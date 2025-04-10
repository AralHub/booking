from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel, validate_hotel_by_slug
from app.api.dependencies.partner import valid_hotel_admin, valid_hotel_admin_by_slug
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings
from app.core.exceptions.http_exceptions import NotFoundException
from app.core.i18n.responses import (
    RESPONSE_MESSAGES,
    DataResponse,
)
from app.dao.hotel.location import HotelLocationDAO
from app.schemas.hotel.info import HotelNameRead
from app.schemas.hotel.location import (
    LocationCreate,
    LocationFilter,
    LocationRead,
    LocationUpdate,
)

router = APIRouter(
    tags=["Hotel Location"],
    prefix=settings.api_v1.hotel_prefix,
)


@router.get(
    "/{hotel_slug}/location",
    response_model=DataResponse[LocationRead],
)
async def get_hotel_location(
    hotel_slug: str,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    session=SessionDep,
):
    db_hotel_location = await HotelLocationDAO.get_hotel_location(
        session=session,
        hotel_id=hotel.id,
    )
    if not db_hotel_location:
        raise NotFoundException("Hotel location not found")
    return DataResponse(
        data=db_hotel_location,
    )


@router.post(
    "/{hotel_slug}/location",
    response_model=DataResponse[LocationRead],
)
async def add_hotel_location(
    hotel_slug: str,
    location_create_data: LocationCreate,
    hotel: HotelNameRead = Depends(valid_hotel_admin_by_slug),
    session=TransactionSessionDep,
):
    created_location = await HotelLocationDAO.add_hotel_location(
        session=session,
        location_create_data=location_create_data,
        hotel_id=hotel.id,
    )
    return DataResponse(
        data=created_location,
        message=RESPONSE_MESSAGES.get(
            "DATA_CREATED",
            default="Hotel location created successfully",
        ),
    )


@router.put(
    "/{hotel_slug}/location",
    response_model=DataResponse[LocationRead],
)
async def update_hotel_location(
    hotel_slug: str,
    location_update_data: LocationUpdate,
    hotel: HotelNameRead = Depends(valid_hotel_admin_by_slug),
    session=TransactionSessionDep,
):
    updated_location = await HotelLocationDAO.update_hotel_location(
        session=session,
        location_update_data=location_update_data,
        hotel_id=hotel.id,
    )
    return DataResponse(
        data=updated_location,
        message=RESPONSE_MESSAGES.get(
            "DATA_UPDATED",
            default="Hotel location created successfully",
        ),
    )
