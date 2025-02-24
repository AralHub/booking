from fastapi import APIRouter

# from app.api.user.functions.dependencies import get_current_active_auth_user
# from app.api.user.schemas import UserRead
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings

from .dao import RuleDAO
from .schemas import (
    RuleCreate,
    RuleCreateInternal,
    RuleFilter,
    RuleUpdate,
    RuleUpdateInternal,
)

router = APIRouter(
    tags=["Hotel Rules"],
    prefix=settings.api_v1.hotel_prefix,
)


@router.get("/{hotel_id}/rule")
async def get_rule(
    hotel_id: int,
    session=SessionDep,
):
    return await RuleDAO.get_one_or_none(
        session=session,
        filters=RuleFilter(hotel_id=hotel_id),
    )


@router.post("{hotel_id}/rule")
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


@router.put("{hotel_id}/rule")
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
