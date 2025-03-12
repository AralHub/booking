from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel_id
from app.core import SessionDep
from app.dao.hotel import HotelAmenityDAO
from app.schemas.hotel.info import HotelNameBase

router = APIRouter(
    prefix="/amenities",
    tags=["Hotel Amenities"],
)


@router.get("/{hotel_id}/amenities")
async def get_hotel_amenities(
    hotel_id: int,
    hotel: HotelNameBase = Depends(validate_hotel_id),
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
    hotel: HotelNameBase = Depends(validate_hotel_id),
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
    hotel: HotelNameBase = Depends(validate_hotel_id),
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
    hotel: HotelNameBase = Depends(validate_hotel_id),
    session=SessionDep,
):
    await HotelAmenityDAO.remove_amenity_from_hotel(
        session=session,
        hotel_id=hotel_id,
        amenity_id=amenity_id,
    )
    return {"message": "Amenity removed from hotel"}
