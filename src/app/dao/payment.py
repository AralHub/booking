from app.dao.base import BaseDAO
from app.models.payment import PaymentMethod


class PaymentDAO(BaseDAO):
    model = PaymentMethod
