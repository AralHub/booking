from fastapi import APIRouter, Depends

from app.api.dependencies.user import (
    get_current_active_auth_user,
)
from app.core import TransactionSessionDep
from app.dao.review import ReviewDAO
from app.schemas.review import ReviewCreate
from app.schemas.user import UserRead

router = APIRouter(
    tags=["Reviews"],
    prefix="/reviews",
)


@router.post("/")
async def create_review(
    review_create_data: ReviewCreate,
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=TransactionSessionDep,
):
    await ReviewDAO.create(
        session=session,
        values=review_create_data,
    )
