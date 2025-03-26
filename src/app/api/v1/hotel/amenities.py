from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel
from app.api.dependencies.partner import valid_hotel_admin
from app.core import SessionDep
from app.dao.hotel import HotelAmenityDAO
from app.schemas.hotel.info import HotelNameRead

router = APIRouter(
    prefix="/amenities",
    tags=["Hotel Amenities"],
)


@router.get("/{hotel_id}/amenities")
async def get_hotel_amenities(
    hotel_id: int,
    hotel: HotelNameRead = Depends(validate_hotel),
    session=SessionDep,
):
    return await HotelAmenityDAO.get_hotel_amenities(
        session=session,
        hotel_id=hotel_id,
    )


@router.post("/{hotel_id}/amenities")
async def add_amenities_to_hotel(
    hotel_id: int,
    amenities: list[int],
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    session=SessionDep,
):
    return await HotelAmenityDAO.add_amenities_to_hotel(
        session=session,
        hotel_id=hotel_id,
        amenities=amenities,
    )


@router.delete("/{hotel_id}/amenities")
async def remove_amenities_from_hotel(
    hotel_id: int,
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    session=SessionDep,
):
    return await HotelAmenityDAO.remove_all_amenities_from_hotel(
        session=session,
        hotel_id=hotel_id,
    )


@router.delete("/{hotel_id}/amenities/{amenity_id}")
async def remove_amenity_from_hotel_by_id(
    hotel_id: int,
    amenity_id: int,
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    session=SessionDep,
):
    await HotelAmenityDAO.remove_amenity_from_hotel(
        session=session,
        hotel_id=hotel_id,
        amenity_id=amenity_id,
    )
    return {"message": "Amenity removed from hotel"}
