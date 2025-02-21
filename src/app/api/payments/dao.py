# from sqlalchemy.ext.asyncio import AsyncSession
from app.api.payments.models import Payment, PaymentType
from app.core.dao import BaseDAO


class PaymentTypeDAO(BaseDAO):
    model = PaymentType


class PaymentDAO(BaseDAO):
    model = Payment
