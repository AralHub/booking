from typing import TYPE_CHECKING

from sqlalchemy import Float
from sqlalchemy.orm import Mapped, mapped_column

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from .room import RoomType  # noqa: F401


class Coordinate(IntIdPkMixin, Base):
    longtitude: Mapped[float] = mapped_column(Float)
    latitude: Mapped[float] = mapped_column(Float)


from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin


class Amenity(IntIdPkMixin, Base):
    pass


from typing import TYPE_CHECKING

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    from .room import RoomType  # noqa: F401


class Bed(IntIdPkMixin, Base):
    pass
