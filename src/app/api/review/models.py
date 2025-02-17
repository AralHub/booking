from typing import TYPE_CHECKING

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin

if TYPE_CHECKING:
    pass


class Reviews(IntIdPkMixin, Base):

    pass
