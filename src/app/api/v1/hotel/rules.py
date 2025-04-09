from fastapi import APIRouter, Depends

from app.api.dependencies.hotel import validate_hotel
from app.api.dependencies.partner import valid_hotel_admin
from app.core import SessionDep, TransactionSessionDep
from app.core.config import settings
from app.core.logger import logging
from app.dao.hotel.rules import HotelRuleDAO
from app.schemas.hotel.info import HotelNameRead
from app.schemas.hotel.rules import (
    RuleCreate,
    RuleCreateInternal,
    RuleFilter,
    RuleUpdate,
    RuleUpdateInternal,
    RuleRead,
)
from app.core.i18n.responses import (
    ListResponse,
    DataResponse,
    BaseResponse,
    RESPONSE_MESSAGES,
)

logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["Hotel Rules"],
    prefix=settings.api_v1.hotel_prefix,
)


@router.get(
    "/{hotel_id}/rules",
    response_model=DataResponse[RuleRead],
)
async def get_hotel_rule(
    hotel_id: int,
    hotel: HotelNameRead = Depends(validate_hotel),
    session=SessionDep,
):
    hotel_rule = await HotelRuleDAO.get_one_or_none(
        session=session,
        filters=RuleFilter(hotel_id=hotel_id),
    )
    return DataResponse[RuleRead](
        data=hotel_rule,
    )


@router.post("/{hotel_id}/rules", response_model=DataResponse[RuleRead])
async def add_hotel_rule(
    hotel_id: int,
    rule_create_data: RuleCreate,
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    session=TransactionSessionDep,
):
    added_rule = await HotelRuleDAO.create(
        session=session,
        values=RuleCreateInternal(
            **rule_create_data.model_dump(),
            hotel_id=hotel_id,
        ),
    )
    return DataResponse[RuleRead](
        data=added_rule,
        message=RESPONSE_MESSAGES.get(
            "DATA_CREATED",
            "Hotel rule created successfully",
        ),
    )


@router.put(
    "/{hotel_id}/rules",
    response_model=DataResponse[RuleRead],
)
async def update_hotel_rule(
    hotel_id: int,
    rule_update_data: RuleUpdate,
    hotel: HotelNameRead = Depends(valid_hotel_admin),
    session=TransactionSessionDep,
):
    updated_rule = await HotelRuleDAO.update(
        session=session,
        values=RuleUpdateInternal(
            **rule_update_data.model_dump(),
        ),
        filters=RuleFilter(
            hotel_id=hotel_id,
        ),
    )
    return DataResponse[RuleRead](
        data=updated_rule,
        message=RESPONSE_MESSAGES.get(
            "DATA_UPDATED",
            "Hotel rule updated successfully",
        ),
    )
