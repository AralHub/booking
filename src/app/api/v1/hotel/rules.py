from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import valid_hotel_admin, validate_hotel_id
from app.core import SessionDep, TransactionSessionDep
from app.core.logger import logging
from app.dao.hotel.rules import RuleDAO
from app.schemas.hotel.info import HotelNameRead
from app.schemas.hotel.rules import (
    RuleCreate,
    RuleCreateInternal,
    RuleFilter,
    RuleUpdate,
    RuleUpdateInternal,
)

logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["Hotels Rules"],
)


@router.get("/{hotel_id}/rules")
async def get_hotel_rule(
    hotel_id: int,
    hotel: HotelNameRead = Depends(validate_hotel_id),
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
    hotel: HotelNameRead = Depends(valid_hotel_admin),
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
    hotel: HotelNameRead = Depends(valid_hotel_admin),
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
