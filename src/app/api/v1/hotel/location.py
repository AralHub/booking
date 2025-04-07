from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel
from app.api.dependencies.partner import valid_hotel_admin
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings
from app.core.exceptions.http_exceptions import NotFoundException
from app.core.i18n.responses import RESPONSE_MESSAGES, DataResponse
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
    "/{hotel_id}/location",
    response_model=DataResponse[LocationRead],
)
async def get_hotel_location(
    hotel_id: int,
    hotel: HotelNameRead = Depends(validate_hotel),
    session=SessionDep,
):
    db_hotel_location = await HotelLocationDAO.get_one_or_none(
        session=session,
        filters=LocationFilter(
            hotel_id=hotel_id,
        ),
    )
    if not db_hotel_location:
        raise NotFoundException("Hotel location not found")
    return DataResponse(
        data=db_hotel_location,
    )


@router.post(
    "/{hotel_id}/location",
    response_model=DataResponse[LocationRead],
)
async def add_hotel_location(
    hotel_id: int,
    location_create_data: LocationCreate,
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    session=TransactionSessionDep,
):
    created_location = await HotelLocationDAO.add_hotel_location(
        session=session,
        location_create_data=location_create_data,
        hotel_id=hotel_id,
    )
    return DataResponse(
        data=created_location,
        message=RESPONSE_MESSAGES.get(
            "DATA_CREATED",
            default="Hotel location created successfully",
        ),
    )


@router.put(
    "/{hotel_id}/location",
    response_model=DataResponse[LocationRead],
)
async def update_hotel_location(
    hotel_id: int,
    location_update_data: LocationUpdate,
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    session=TransactionSessionDep,
):
    updated_location = await HotelLocationDAO.update_hotel_location(
        session=session,
        location_update_data=location_update_data,
        hotel_id=hotel_id,
    )
    return DataResponse(
        data=updated_location,
        message=RESPONSE_MESSAGES.get(
            "DATA_UPDATED",
            default="Hotel location created successfully",
        ),
    )
