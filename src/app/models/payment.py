# from typing import TYPE_CHECKING


from app.models import Base
from app.models.mixins import IntIdPkMixin, MultilingualNameMixin

# if TYPE_CHECKING:
#     from app.models.user import User
#     from app.models.hotel import Hotel


class Payment(
    IntIdPkMixin,
    MultilingualNameMixin,
    Base,
):
    pass
