

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin


class Amenity(IntIdPkMixin, Base):
    pass
