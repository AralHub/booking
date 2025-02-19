from fastapi import APIRouter

# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from app.core import SessionDep
from app.core.config import settings

from .dao import ReviewDAO

router = APIRouter(
    tags=["Review"],
    prefix=settings.api_v1.review_prefix,
)


@router.get("/")
async def get_all_reviews(
    session=SessionDep,
):
    return await ReviewDAO.get_all(
        session=session,
        filters=None,
    )


