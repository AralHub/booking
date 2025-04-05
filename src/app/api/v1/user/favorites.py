from fastapi import APIRouter, Depends

from app.api.dependencies.user import (
    get_current_auth_user,
)
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings
from app.dao.favorites import UserFavoriteDAO
from app.schemas.favorites import (
    UserFavoriteCreateInternal,
    UserFavoriteFilter,
)
from app.schemas.user import UserRead

# from app.core.utils.eskiz_client import code_generator

router = APIRouter(
    tags=["User Favorites"],
    prefix=settings.api_v1.favorites_prefix,
)


@router.get("")
async def get_favorites(
    current_user: UserRead = Depends(get_current_auth_user),
    session=SessionDep,
):
    return await UserFavoriteDAO.get_all(
        session=session,
        filters=UserFavoriteFilter(
            user_id=current_user.id,
        ),
    )


@router.post("/{hotel_id}")
async def add_favorite(
    hotel_id: int,
    current_user: UserRead = Depends(get_current_auth_user),
    session=TransactionSessionDep,
):
    return await UserFavoriteDAO.create(
        session=session,
        values=UserFavoriteCreateInternal(
            user_id=current_user.id,
            hotel_id=hotel_id,
        ),
    )


@router.delete("/{hotel_id}")
async def delete_favorite(
    hotel_id: int,
    current_user: UserRead = Depends(get_current_auth_user),
    session=TransactionSessionDep,
):
    return await UserFavoriteDAO.delete(
        session=session,
        filters=UserFavoriteFilter(
            user_id=current_user.id,
            hotel_id=hotel_id,
        ),
    )
