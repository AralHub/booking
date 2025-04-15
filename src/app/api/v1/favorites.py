from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel_by_slug
from app.api.dependencies.user import get_current_auth_user
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings
from app.core.exceptions.http_exceptions import NotFoundException
from app.core.i18n.responses import (
    RESPONSE_MESSAGES,
    BaseResponse,
    DataResponse,
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
    "/{hotel_slug}",
)
async def is_my_favorite(
    hotel_slug: str,
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    current_user: UserRead = Depends(get_current_auth_user),
    session=TransactionSessionDep,
):
    if not current_user:
        return {
            "data": False,
        }
    favorite = await UserFavoriteDAO.get_one_or_none(
        session=session,
        filters=UserFavoriteFilter(
            user_id=current_user.id,
            hotel_id=hotel.id,
        ),
    )
    return {
        "data":  True if favorite else False,
    }


@router.get(
    "",
)
async def get_favorites(
    current_user: UserRead = Depends(get_current_auth_user),
    session=SessionDep,
):
    favorites = await UserFavoriteDAO.get_user_favorites(
        session=session,
        user_id=current_user.id,
    )
    return {
        "data": favorites,
        "total": len(favorites),
    }


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
    "/{favorite_id}",
    response_model=BaseResponse,
)
async def delete_favorite(
    favorite_id: int,
    current_user: UserRead = Depends(get_current_auth_user),
    session=TransactionSessionDep,
):
    favorite = await UserFavoriteDAO.get_by_id(
        session=session,
        id=favorite_id,
    )
    if not favorite:
        raise NotFoundException(
            error_code="NOT_FOUND",
        )
    await UserFavoriteDAO.delete(
        session=session,
        filters=UserFavoriteFilter(
            user_id=current_user.id,
            id=favorite_id,
        ),
    )
    return BaseResponse(
        success=True,
        message=RESPONSE_MESSAGES.get(
            "DATA_DELETED",
            "Hotel removed from favorites successfully",
        ),
    )
