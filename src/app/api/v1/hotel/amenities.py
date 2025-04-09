from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel
from app.api.dependencies.partner import valid_hotel_admin
from app.core import SessionDep, TransactionSessionDep
from app.core.i18n.responses import (
    RESPONSE_MESSAGES,
    BaseResponse,
    DataResponse,
    ListResponse,
)
from app.dao.hotel import HotelAmenityDAO
from app.schemas.hotel.amenities import HotelAmenityRead
from app.schemas.hotel.info import HotelNameRead

router = APIRouter(
    prefix="/amenities",
    tags=["Hotel Amenities"],
)


@router.get(
    "/{hotel_id}/amenities",
    response_model=ListResponse[HotelAmenityRead],
)
async def get_hotel_amenities(
    hotel_id: int,
    hotel: HotelNameRead = Depends(validate_hotel),
    session=SessionDep,
):
    hotel_amenities = await HotelAmenityDAO.get_hotel_amenities(
        session=session,
        hotel_id=hotel_id,
    )
    return ListResponse(
        data=hotel_amenities,
        total=len(hotel_amenities),
    )


@router.post(
    "/{hotel_id}/amenities",
    response_model=DataResponse[HotelAmenityRead],
)
async def add_amenities_to_hotel(
    hotel_id: int,
    amenities: list[int],
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    session=TransactionSessionDep,
):
    created_amenities = await HotelAmenityDAO.add_amenities_to_hotel(
        session=session,
        hotel_id=hotel_id,
        amenities=amenities,
    )
    return DataResponse(
        data=created_amenities,
        message=RESPONSE_MESSAGES.get(
            "DATA_CREATED",
            "Amenities added to hotel successfully",
        ),
    )


@router.delete(
    "/{hotel_id}/amenities",
    response_model=BaseResponse,
)
async def remove_amenities_from_hotel(
    hotel_id: int,
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    session=TransactionSessionDep,
):
    await HotelAmenityDAO.remove_all_amenities_from_hotel(
        session=session,
        hotel_id=hotel_id,
    )
    return BaseResponse(
        success=True,
        message=RESPONSE_MESSAGES.get(
            "DATA_DELETED",
            "Amenities removed from hotel successfully",
        ),
    )


@router.delete(
    "/{hotel_id}/amenities/{amenity_id}",
    response_model=BaseResponse,
)
async def remove_amenity_from_hotel_by_id(
    hotel_id: int,
    amenity_id: int,
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    session=TransactionSessionDep,
):
    await HotelAmenityDAO.remove_amenity_from_hotel(
        session=session,
        hotel_id=hotel_id,
        amenity_id=amenity_id,
    )
    return BaseResponse(
        success=True,
        message=RESPONSE_MESSAGES.get(
            "DATA_DELETED",
            "Amenity removed from hotel successfully",
        ),
    )
