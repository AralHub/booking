from fastapi import APIRouter

from app.core import SessionDep, TransactionSessionDep
from app.dao.payment import PaymentDAO
from app.schemas.payment import (
    PaymentCreate,
    PaymentCreateInternal,
    PaymentFilter,
    PaymentUpdate,
    PaymentUpdateInternal,
)

router = APIRouter(
    tags=["Superuser Payment"],
    prefix="/payment",
)


@router.get("")
async def get_payment_methods(
    session=SessionDep,
):
    return await PaymentDAO.get_all(
        session=session,
        filters=None,
    )


@router.post(
    "",
    # dependencies=[Depends(get_current_superuser)],
)
async def create_payment_method(
    payment_create_data: PaymentCreate,
    session=TransactionSessionDep,
):
    payment_create_internal = PaymentCreateInternal(
        name=payment_create_data.to_dict_name(),
    )
    # Create main hotel record
    db_payment = await PaymentDAO.create(
        session=session,
        values=payment_create_internal,
    )
    return db_payment


@router.put(
    "/{payment_id}",
    # dependencies=[Depends(get_current_superuser)],
)
async def update_payment_method(
    payment_id: int,
    payment_update_data: PaymentUpdate,
    session=TransactionSessionDep,
):
    payment_update = PaymentUpdateInternal(
        name=payment_update_data.to_dict_name(),
    )
    # Create main hotel record
    await PaymentDAO.update(
        session=session,
        values=payment_update,
        filters=PaymentFilter(
            id=payment_id,
        ),
    )
