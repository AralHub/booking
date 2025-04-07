from fastapi import APIRouter

from app.core import SessionDep
from app.core.config import settings
from app.core.i18n.responses import DataResponse
from app.dao.hotel.rating import HotelRatingDAO
from app.schemas.hotel.rating import HotelRatingRead

router = APIRouter(
    tags=["Hotel Rating"],
    prefix=settings.api_v1.hotel_prefix,
)


@router.get(
    "/{hotel_id}/rating",
    response_model=DataResponse[HotelRatingRead],
)
async def get_hotel_rating(
    hotel_id: int,
    session=SessionDep,
):

    hotel_rating = await HotelRatingDAO.get_hotel_summary_rating(
        session=session,
        hotel_id=hotel_id,
    )
    return DataResponse(
        data=hotel_rating,
    )
