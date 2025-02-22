from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# class Language(IntIdPkMixin, Base):
#     name: Mapped[str] = mapped_column(String(255), unique=True)
#     hotels: Mapped[list["Hotel"]] = relationship(
#         "Hotel",
#         secondary="hotel_language_associations",
#         back_populates="languages",
#     )


# class HotelLanguageAssociation(Base):
#     __tablename__ = "hotel_language_associations"
#     hotel_id: Mapped[int] = mapped_column(
#         ForeignKey("hotels.id"),
#         primary_key=True,
#     )
#     language_id: Mapped[int] = mapped_column(
#         ForeignKey("languages.id"),
#         primary_key=True,
#     )
#     # association between Assocation -> Hotel
#     hotel: Mapped["Hotel"] = relationship(
#         "Hotel",
#         back_populates="hotel_language_association",
#     )
#     # association between Assocation -> Language
#     language: Mapped[Language] = relationship(
#         "Language",
#         back_populates="hotel_language_association",
#     )
#     __table_args__ = (
#         UniqueConstraint(
#             "hotel_id",
#             "language_id",
#             name="uq_hotel_language",
#         ),
#     )
