from fastapi import APIRouter, Depends

from app.api.dependencies.partner import get_current_auth_partner
from app.core import TransactionSessionDep
from app.dao.partner import PartnerDAO
from app.schemas.partner import (
    PartnerFilter,
    PartnerRead,
    PartnerUpdate,
    PartnerUpdateInternal,
)

from .auth import router as auth_router

router = APIRouter(
    tags=["Partners"],
    prefix="/partners",
)
router.include_router(auth_router)


@router.get("/me", response_model=PartnerRead)
async def get_my_profile(
    partner: PartnerRead = Depends(get_current_auth_partner),
):
    return partner


@router.put("/me", response_model=PartnerRead)
async def update_partner_profile(
    partner_update: PartnerUpdate,
    session=TransactionSessionDep,
    partner: PartnerRead = Depends(get_current_auth_partner),
):

    await PartnerDAO.update(
        session=session,
        values=PartnerUpdateInternal(
            **partner_update.model_dump(),
        ),
        filters=PartnerFilter(id=partner.id),   
    )
