from fastapi import (
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db_helper
from app.core.auth.helpers import ACCESS_TOKEN_TYPE
from app.core.auth.validation import (
    get_current_token_payload,
    get_partner_by_token_sub,
    validate_token_type,
)
from app.core.exceptions.http_exceptions import (
    UnauthorizedException,
)
from app.core.logger import logging
from app.schemas.hotel.info import HotelNameRead
from app.schemas.partner import PartnerBase, PartnerRead

from .hotel import validate_hotel, validate_hotel_by_slug

logger = logging.getLogger(__name__)


class PartnerGetterFromToken:
    def __init__(self, token_type: str):
        self.token_type = token_type

    async def __call__(
        self,
        payload: dict = Depends(get_current_token_payload),
        session: AsyncSession = Depends(db_helper.session_getter),
    ):
        validate_token_type(payload, self.token_type)
        partner = await get_partner_by_token_sub(session, payload)
        if not partner:
            raise UnauthorizedException("Inactive partner")
        return partner


get_current_auth_partner = PartnerGetterFromToken(ACCESS_TOKEN_TYPE)


async def get_current_active_auth_partner(
    partner: PartnerBase = Depends(get_current_auth_partner),
):
    if partner.is_active:
        return partner
    raise UnauthorizedException("Inactive partner")


async def valid_hotel_admin(
    hotel: HotelNameRead = Depends(validate_hotel),
    current_partner: PartnerRead = Depends(get_current_auth_partner),
):
    if hotel.hotel_admin_id != current_partner.id:
        raise UnauthorizedException("Permission denied")
    return hotel


async def valid_hotel_admin_by_slug(
    hotel: HotelNameRead = Depends(validate_hotel_by_slug),
    current_partner: PartnerRead = Depends(get_current_auth_partner),
):
    if hotel.hotel_admin_id != current_partner.id:
        raise UnauthorizedException("Permission denied")
    return hotel
