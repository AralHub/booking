from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel_by_slug
from app.api.dependencies.user import get_current_auth_user
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings
from app.core.i18n.responses import (
    RESPONSE_MESSAGES,
    BaseResponse,
    DataResponse,
    ListResponse,
)
from app.dao.favorites import UserFavoriteDAO
from app.schemas.favorites import (
    UserFavoriteCreateInternal,
    UserFavoriteFilter,
    UserFavoriteRead,
)
from app.schemas.hotel.info import HotelNameRead
from app.schemas.user import UserRead

router = APIRouter(
    tags=["Favorites"],
    prefix=settings.api_v1.favorites_prefix,
)


@router.get(
    "",
    response_model=ListResponse[UserFavoriteRead],
)
async def get_favorites(
    current_user: UserRead = Depends(get_current_auth_user),
    session=SessionDep,
):
    favorites = await UserFavoriteDAO.get_all(
        session=session,
        filters=UserFavoriteFilter(
            user_id=current_user.id,
        ),
    )
    return ListResponse(
        data=[UserFavoriteRead.model_validate(favorite) for favorite in favorites],
        total=len(favorites),
    )


@router.post(
    "/{hotel_slug}",
    response_model=DataResponse[UserFavoriteRead],
)
async def add_favorite(
    hotel_slug: str,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    current_user: UserRead = Depends(get_current_auth_user),
    session=TransactionSessionDep,
):
    added_favorite = await UserFavoriteDAO.create(
        session=session,
        values=UserFavoriteCreateInternal(
            user_id=current_user.id,
            hotel_id=hotel.id,
        ),
    )
    return DataResponse(
        data=added_favorite,
        message=RESPONSE_MESSAGES.get(
            "DATA_CREATED",
            "Hotel added to favorites successfully",
        ),
    )


@router.delete(
    "/{hotel_slug}",
    response_model=BaseResponse,
)
async def delete_favorite(
    hotel_slug: str,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    current_user: UserRead = Depends(get_current_auth_user),
    session=TransactionSessionDep,
):
    await UserFavoriteDAO.delete(
        session=session,
        filters=UserFavoriteFilter(
            user_id=current_user.id,
            hotel_id=hotel.id,
        ),
    )
    return BaseResponse(
        success=True,
        message=RESPONSE_MESSAGES.get(
            "DATA_DELETED",
            "Hotel removed from favorites successfully",
        ),
    )
