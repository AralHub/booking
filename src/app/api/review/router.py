# from fastapi import APIRouter

# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
# from app.core import SessionDep

# router = APIRouter(
#     tags=["Review"],
#     prefix="/hotels",
# )


# @router.get("/{hotel_id}/reviews")
# async def get_all_reviews(
#     hotel_id: int,
#     session=SessionDep,
# ):
#     pass
