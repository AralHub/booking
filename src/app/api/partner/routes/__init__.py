from typing import Optional

from fastapi import APIRouter, Depends

from app.core import SessionDep, TransactionSessionDep

from ..dao import PartnerDAO
from ..dependencies import get_current_auth_partner
from ..schemas import (
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


@router.put("/")
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
