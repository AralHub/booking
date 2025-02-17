from sqlalchemy import Computed, Date, ForeignKey, Integer, mapped_column
from sqlalchemy.orm import relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin


class Bookings(IntIdPkMixin, Base):

    pass
