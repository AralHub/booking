from fastapi import APIRouter, Depends

from app.api.dependencies.hotel_category import validate_hotel_category_by_id
from app.api.dependencies.user import get_current_superuser
from app.core import SessionDep, TransactionSessionDep
from app.core.i18n.responses import ListResponse
from app.core.logger import logging
from app.dao.hotel.category import HotelCategoryDAO
from app.schemas.hotel.category import (
    HotelCategoryBase,
    HotelCategoryCreate,
    HotelCategoryFilter,
    HotelCategoryUpdate,
    HotelCategoryRead,
)

logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["Superuser Hotel Categories"],
    prefix="/hotel-categories",
)


@router.get(
    "",
    response_model=ListResponse[HotelCategoryRead],
)
async def get_hotel_categories(
    session=SessionDep,
):
    categories = await HotelCategoryDAO.get_all(
        session=session,
        filters=None,
    )
    return ListResponse(
        data=[HotelCategoryRead.model_validate(category) for category in categories],
        total=len(categories),
    )


@router.post(
    "/",
    dependencies=[Depends(get_current_superuser)],
)
async def create_hotel_category(
    category_create_data: HotelCategoryCreate,
    session=TransactionSessionDep,
):
    return await HotelCategoryDAO.create(
        session=session,
        values=category_create_data,
    )


@router.put(
    "/{category_id}",
    dependencies=[Depends(get_current_superuser)],
)
async def update_hotel_category(
    category_update_data: HotelCategoryUpdate,
    category_id: int,
    hotel_category: HotelCategoryBase = Depends(validate_hotel_category_by_id),
    session=TransactionSessionDep,
):
    return await HotelCategoryDAO.update(
        session=session,
        values=category_update_data,
        filters=HotelCategoryFilter(id=category_id),
    )


@router.delete(
    "/{category_id}",
    dependencies=[Depends(get_current_superuser)],
)
async def delete_hotel_category(
    category_id: int,
    hotel_category: HotelCategoryBase = Depends(validate_hotel_category_by_id),
    session=TransactionSessionDep,
):
    return await HotelCategoryDAO.delete(
        session=session,
        filters=HotelCategoryFilter(
            id=category_id,
        ),
    )
