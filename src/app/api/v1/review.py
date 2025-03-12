from fastapi import APIRouter, Depends

from app.api.hotel.dependencies import validate_hotel_id
from app.api.hotel.schemas import HotelNameRead
from app.api.review.dao import ReviewCategoryRatingDAO, ReviewDAO
from app.api.review.schemas import (
    ReviewCategoryCreateInternal,
    ReviewCreate,
    ReviewCreateInternal,
)
from app.api.user.dependencies import (
    get_current_active_auth_user,
    get_current_superadmin_user,
)
from app.api.user.schemas import UserRead
from app.core import SessionDep, TransactionSessionDep
from app.dao.review import ReviewCategoryDAO
from app.schemas.review import ReviewCategoryCreate, ReviewCategoryFilter

router = APIRouter(
    tags=["Reviews"],
)


# region Hotel Reviews
@router.get("/hotels/{hotel_id}/reviews")
async def get_hotel_reviews(
    hotel_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_id),
    session=SessionDep,
):
    return await ReviewDAO.get_all_hotel_reviews(
        session=session,
        hotel_id=hotel_id,
    )


@router.post("/hotels/{hotel_id}/reviews")
async def create_hotel_reviews(
    hotel_id: int,
    review_create_data: ReviewCreate,
    hotel: HotelNameRead = Depends(validate_hotel_id),
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=TransactionSessionDep,
):

    craeted_review = await ReviewDAO.create(
        session=session,
        values=ReviewCreateInternal(
            **review_create_data.model_dump(
                exclude={
                    "category_ratings",
                }
            ),
            hotel_id=hotel_id,
            user_id=current_user.id,
        ),
    )
    if len(review_create_data.category_ratings) > 0:
        for review_category_rating in review_create_data.category_ratings:
            review_category_rating_create_data = ReviewCategoryCreateInternal(
                review_category_id=review_category_rating.review_category_id,
                rating=review_category_rating.rating,
                review_id=craeted_review.id,
            )

        await ReviewCategoryRatingDAO.create(
            session=session,
            values=review_category_rating_create_data,
        )
    return craeted_review


# endregion


# region Review Categories
@router.get(
    "/reviews/categories",
)
async def get_review_categories(
    session=SessionDep,
):
    return await ReviewCategoryDAO.get_all(
        session=session,
        filters=None,
    )


@router.post(
    "/reviews/categories",
    dependencies=[Depends(get_current_superadmin_user)],
)
async def create_review_categories(
    review_category_create_data: ReviewCategoryCreate,
    session=TransactionSessionDep,
):
    await ReviewCategoryDAO.create(
        session=session,
        values=review_category_create_data,
    )


@router.put(
    "/reviews/categories/{review_category_id}",
    dependencies=[Depends(get_current_superadmin_user)],
)
async def update_review_categories(
    review_category_id: int,
    review_category_update_data: ReviewCategoryCreate,
    session=TransactionSessionDep,
):
    await ReviewCategoryDAO.update(
        session=session,
        values=review_category_update_data,
        filters=ReviewCategoryFilter(
            id=review_category_id,
        ),
    )


@router.delete(
    "/reviews/categories/{review_category_id}",
    dependencies=[Depends(get_current_superadmin_user)],
)
async def delete_review_categories(
    review_category_id: int,
    session=TransactionSessionDep,
):
    await ReviewCategoryDAO.delete(
        session=session,
        filters=ReviewCategoryFilter(
            id=review_category_id,
        ),
    )


# endregion
