import logging

from fastapi import APIRouter

from app.core import SessionDep, TransactionSessionDep
from app.dao.hotel.rules import RuleDAO
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
