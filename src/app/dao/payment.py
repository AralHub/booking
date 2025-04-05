from app.dao.base import BaseDAO
from app.models.payment import Payment


class PaymentDAO(BaseDAO):
    model = Payment
