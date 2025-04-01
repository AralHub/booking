from fastapi import APIRouter

from app.core import SessionDep
from app.core.config import settings
from app.dao.hotel.rating import HotelRatingDAO

router = APIRouter(
    tags=["Hotel Rating"],
    prefix=settings.api_v1.hotel_prefix,
)


@router.get("/{hotel_id}/rating")
async def get_hotel_rating(
    hotel_id: int,
    session=SessionDep,
):

    hotel_rating = await HotelRatingDAO.get_hotel_summary_rating(
        session=session,
        hotel_id=hotel_id,
    )
    return hotel_rating

# @router.get("/{hotel_id}/reviews/summary")
# async def get_hotel_review_summary(
#     hotel_id: int,
#     hotel: HotelNameRead = Depends(validate_hotel),
#     session=SessionDep,
# ):
#     summary_data = await ReviewDAO.get_hotel_review_summary(
#         session=session,
#         hotel_id=hotel_id,
#     )

#     # Получаем количество отзывов
#     review_count = await ReviewDAO.get_review_count_for_hotel(
#         session=session,
#         hotel_id=hotel_id,
#     )

#     return HotelReviewSummary(
#         average_rating=summary_data["average_rating"],
#         review_count=review_count,
#         category_ratings=summary_data["category_ratings"],
#     )
