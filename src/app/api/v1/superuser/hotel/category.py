import logging

from fastapi import APIRouter

from app.core import SessionDep, TransactionSessionDep
from app.dao.hotel.categoty import HotelCategoryDAO
from app.schemas.hotel.category import (
    HotelCategoryFilter,
    HotelCategoryUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["Superuser Hotel Categories"],
    prefix="/hotel-categories",
)


@router.get("")
async def get_hotel_categories(
    session=SessionDep,
):
    return await HotelCategoryDAO.get_all(
        session=session,
        filters=None,
    )


@router.put("/{category_id}")
async def update_hotel_category(
    category_update_data: HotelCategoryUpdate,
    category_id: int,
    session=TransactionSessionDep,
):
    return await HotelCategoryDAO.update(
        session=session,
        values=category_update_data,
        filters=HotelCategoryFilter(id=category_id),
    )
