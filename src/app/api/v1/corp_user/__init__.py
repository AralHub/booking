from fastapi import APIRouter, Depends

from app.api.dependencies.corp_user import get_current_auth_corp_user
from app.core import TransactionSessionDep
from app.schemas.corp_user import CorpUserRead

from .auth import router as auth_router

router = APIRouter(
    tags=["Corp Users"],
    prefix="/corp_users",
)
router.include_router(auth_router)


@router.get("/me", response_model=CorpUserRead)
async def get_my_profile(
    corp_user: CorpUserRead = Depends(get_current_auth_corp_user),
):
    return corp_user
