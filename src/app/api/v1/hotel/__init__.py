import logging

from fastapi import APIRouter, Depends, Query

from app.api.partner.dependencies import get_current_active_auth_partner
from app.api.partner.schemas import PartnerRead
from app.api.rule.dao import RuleDAO
from app.api.rule.schemas import (
    RuleCreate,
    RuleCreateInternal,
    RuleFilter,
    RuleUpdate,
    RuleUpdateInternal,
)
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings
from app.core.utils.parse_date import parse_date

from .dao import HotelCategoryDAO, HotelDAO, HotelInfoDAO
from .dependencies import validate_hotel_id
from .schemas import (
    HotelCategoryCreate,
    HotelCategoryFilter,
    HotelCategoryUpdate,
    HotelFullCreate,
    HotelFullUpdate,
    HotelInfoCreate,
    HotelInfoCreateInternal,
    HotelInfoFilter,
    HotelInfoRead,
    HotelInfoUpdate,
    HotelInfoUpdateInternal,
    HotelNameBase,
)

logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["Hotels"],
    prefix=settings.api_v1.hotel_prefix,
)


# region Hotel
@router.get("/search")
async def search_hotels(
    city_id: int = Query(..., description="ID города"),
    check_in: str = Query(..., description="Дата заезда"),
    check_out: str = Query(..., description="Дата выезда"),
    guests: str = Query(
        ..., description="Количество гостей по комнатам, например: 3-1 для 2 комнат"
    ),
    session=SessionDep,
):
    parsed_check_in = parse_date(check_in)
    parsed_check_out = parse_date(check_out)
    return await HotelDAO.find_hotels(
        session=session,
        city_id=city_id,
        check_in_date=parsed_check_in,
        check_out_date=parsed_check_out,
        guests=guests,
    )


@router.post("/")
async def create_hotel(
    hotel_create_data: HotelFullCreate,
    partner: PartnerRead = Depends(get_current_active_auth_partner),
    session=TransactionSessionDep,
):
    return await HotelDAO.create_new_hotel(
        session=session,
        hotel_create_data=hotel_create_data,
        hotel_admin_id=partner.id,
    )


@router.put("/{hotel_id}")
async def update_hotel(
    hotel_update_data: HotelFullUpdate,
    hotel_id: int,
    partner: PartnerRead = Depends(get_current_active_auth_partner),
    session=TransactionSessionDep,
):
    return await HotelDAO.update_hotel(
        session=session,
        hotel_update_data=hotel_update_data,
        hotel_id=hotel_id,
    )


# endregion
# region Hotel Info


@router.get(
    "/{hotel_id}/info",
    response_model=HotelInfoRead,
)
async def get_hotel_info(
    hotel_id: int,
    hotel: HotelNameBase = Depends(validate_hotel_id),
    session=TransactionSessionDep,
):
    return await HotelInfoDAO.get_one_or_none(
        session=session,
        filters=HotelInfoFilter(hotel_id=hotel_id),
    )


@router.post("/{hotel_id}/info")
async def add_hotel_info(
    hotel_id: int,
    hotel_info_create_data: HotelInfoCreate,
    hotel: HotelNameBase = Depends(validate_hotel_id),
    session=TransactionSessionDep,
):

    return await HotelInfoDAO.create(
        session=session,
        values=HotelInfoCreateInternal(
            **hotel_info_create_data.model_dump(),
            hotel_id=hotel_id,
        ),
    )


@router.put("/{hotel_id}/info")
async def update_hotel_info(
    hotel_id: int,
    hotel_info_update_data: HotelInfoUpdate,
    hotel: HotelNameBase = Depends(validate_hotel_id),
    session=TransactionSessionDep,
):
    return await HotelInfoDAO.update(
        session=session,
        values=HotelInfoUpdateInternal(
            **hotel_info_update_data.model_dump(),
            hotel_id=hotel_id,
        ),
        filters=HotelInfoFilter(
            hotel_id=hotel_id,
        ),
    )


# endregion


# region Hotel Rules


@router.get("/{hotel_id}/rules")
async def get_hotel_rule(
    hotel_id: int,
    session=SessionDep,
):
    return await RuleDAO.get_one_or_none(
        session=session,
        filters=RuleFilter(hotel_id=hotel_id),
    )


@router.post("/{hotel_id}/rules")
async def add_hotel_rule(
    hotel_id: int,
    rule_create_data: RuleCreate,
    session=TransactionSessionDep,
):
    return await RuleDAO.create(
        session=session,
        values=RuleCreateInternal(
            **rule_create_data.model_dump(),
            hotel_id=hotel_id,
        ),
    )


@router.put("/{hotel_id}/rules")
async def update_hotel_rule(
    hotel_id: int,
    rule_update_data: RuleUpdate,
    session=TransactionSessionDep,
):
    return await RuleDAO.update(
        session=session,
        values=RuleUpdateInternal(
            **rule_update_data.model_dump(),
        ),
        filters=RuleFilter(
            hotel_id=hotel_id,
        ),
    )


# endregion
# region Hotel Category
@router.get("/categories")
async def get_hotel_categories(
    session=SessionDep,
):
    return await HotelCategoryDAO.get_all(
        session=session,
        filters=None,
    )


@router.post("/categories")
async def create_hotel_category(
    hotel_category_create_data: HotelCategoryCreate,
    session=TransactionSessionDep,
):
    return await HotelCategoryDAO.create(
        session=session,
        values=hotel_category_create_data,
    )


@router.put("/categories/{category_id}")
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


@router.delete("/categories/{category_id}")
async def delete_hotel_category(
    category_id: int,
    session=TransactionSessionDep,
):
    return await HotelCategoryDAO.delete(
        session=session,
        filters=HotelCategoryFilter(id=category_id),
    )


# endregion
