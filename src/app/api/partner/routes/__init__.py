from typing import Optional

from fastapi import APIRouter, Depends

from ..dependencies import get_current_auth_partner
from ..schemas import PartnerRead
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
