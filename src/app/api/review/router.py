from fastapi import APIRouter

from app.core import SessionDep, TransactionSessionDep

from .dao import ReviewCategoryDAO
from .schemas import ReviewCategoryCreate, ReviewCategoryFilter

router = APIRouter(
    tags=["Review"],
    prefix="/reviews",
)


@router.get("/categories")
async def get_review_categories(
    session=SessionDep,
):
    return await ReviewCategoryDAO.get_all(
        session=session,
        filters=None,
    )


@router.post("/categories")
async def create_review_categories(
    review_category_create_data: ReviewCategoryCreate,
    session=TransactionSessionDep,
):
    await ReviewCategoryDAO.create(
        session=session,
        values=review_category_create_data,
    )


@router.put("/categories/{review_category_id}")
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


@router.delete("/categories/{review_category_id}")
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
