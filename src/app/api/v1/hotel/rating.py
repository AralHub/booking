from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel_by_slug
from app.core import SessionDep
from app.core.config import settings
from app.dao.hotel.rating import HotelRatingDAO
from app.schemas.hotel.info import HotelNameRead

router = APIRouter(
    tags=["Hotel Rating"],
    prefix=settings.api_v1.hotel_prefix,
)


@router.get(
    "/{hotel_slug}/rating",
)
async def get_hotel_rating(
    hotel_slug: str,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    session=SessionDep,
):

    hotel_rating = await HotelRatingDAO.get_hotel_summary_rating(
        session=session,
        hotel_id=hotel.id,
    )
    if not hotel_rating:
        return {
            "data": {},
        }
    return {
        "data": hotel_rating,
    }
