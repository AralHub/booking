from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins import IntIdPkMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.hotel.amenities import HotelAmenity, HotelAmenityAssociation
    from app.models.hotel.category import HotelCategory
    from app.models.hotel.images import HotelImage
    from app.models.hotel.info import HotelInfo
    from app.models.hotel.location import HotelLocation
    from app.models.hotel.rules import Rule
    from app.models.partner import Partner
    from app.models.review import Review
    from app.models.room import Room


class Hotel(IntIdPkMixin, TimestampMixin, Base):
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )
    image: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
    )
    # relationships
    rooms: Mapped[list["Room"]] = relationship(
        "Room",
        back_populates="hotel",
        cascade="all, delete-orphan",
    )
    hotel_category_id: Mapped[int] = mapped_column(
        ForeignKey("hotel_categories.id"),
    )
    hotel_category: Mapped["HotelCategory"] = relationship(
        "HotelCategory",
        back_populates="hotels",
    )
    hotel_amenity_association: Mapped[list["HotelAmenityAssociation"]] = relationship(
        "HotelAmenityAssociation",
        back_populates="hotel",
    )
    hotel_amenities: Mapped[list["HotelAmenity"]] = relationship(
        secondary="hotel_amenity_associations",
        back_populates="hotels",
    )
    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="hotel",
    )
    location: Mapped["HotelLocation"] = relationship(
        "HotelLocation",
        uselist=False,
        single_parent=True,
    )
    hotel_images: Mapped[list["HotelImage"]] = relationship(
        "HotelImage",
        back_populates="hotel",
    )
    rule: Mapped["Rule"] = relationship(
        "Rule",
        back_populates="hotel",
    )
    hotel_admin_id: Mapped[int] = mapped_column(ForeignKey("partners.id"))
    hotel_admin: Mapped["Partner"] = relationship(
        "Partner",
        back_populates="hotel",
    )
    hotel_info: Mapped["HotelInfo"] = relationship(back_populates="hotel")

    # languages: Mapped[list["Language"]] = relationship(
    #     secondary="hotel_language_associations",
    #     back_populates="hotels",
    # )
