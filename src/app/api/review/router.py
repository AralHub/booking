from fastapi import APIRouter

from app.core import SessionDep

router = APIRouter(
    tags=["Review"],
    prefix="/hotels",
)


@router.get("/{hotel_id}/reviews/categories")
async def get_review_categories(
    hotel_id: int,
    session=SessionDep,
):
    pass
