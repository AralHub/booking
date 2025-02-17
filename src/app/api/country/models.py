from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core import Base
from app.core.db.model_mixins import IntIdPkMixin


class Country(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(30))
    code: Mapped[str] = mapped_column(String(30), unique=True)
    cities: Mapped[list["City"]] = relationship(
        "City",
        back_populates="country",
        cascade="all, delete-orphan",
    )


class City(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(30))
    country_id: Mapped[int] = mapped_column(ForeignKey("countrys.id"))
    country: Mapped["Country"] = relationship(back_populates="cities")
