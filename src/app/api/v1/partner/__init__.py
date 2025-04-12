from fastapi import APIRouter, Depends

from app.api.dependencies.partner import get_current_auth_partner
from app.core import TransactionSessionDep
from app.core.i18n.responses import DataResponse
from app.dao.partner import PartnerDAO
from app.schemas.partner import (
    PartnerFilter,
    PartnerRead,
    PartnerUpdate,
    PartnerUpdateInternal,
)

from .auth import router as auth_router
from .hotel import router as hotel_router
from .booking import router as booking_router

router = APIRouter(
    tags=["Partners"],
    prefix="/partners",
)
router.include_router(auth_router)
router.include_router(hotel_router)
router.include_router(booking_router)


@router.get(
    "/me",
    response_model=DataResponse[PartnerRead],
)
async def get_my_profile(
    partner: PartnerRead = Depends(get_current_auth_partner),
):
    return DataResponse(
        data=partner,
    )


@router.put(
    "/me",
    response_model=DataResponse[PartnerRead],
)
async def update_partner_profile(
    partner_update: PartnerUpdate,
    session=TransactionSessionDep,
    partner: PartnerRead = Depends(get_current_auth_partner),
):

    updated_partner = await PartnerDAO.update(
        session=session,
        values=PartnerUpdateInternal(
            **partner_update.model_dump(),
        ),
        filters=PartnerFilter(id=partner.id),
    )
    return DataResponse(
        data=updated_partner,
    )
