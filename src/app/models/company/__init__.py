# from typing import TYPE_CHECKING

# from sqlalchemy import ForeignKey, String
# from sqlalchemy.orm import Mapped, mapped_column, relationship

# from app.models import Base
# from app.models.mixins import IntIdPkMixin, TimestampMixin

# if TYPE_CHECKING:
#     from app.models.company.company_info import CompanyInfo
#     from app.models.user import User


# class Company(
#     IntIdPkMixin,
#     TimestampMixin,
#     Base,
# ):
#     position: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )
#     company_name: Mapped[str] = mapped_column(
#         String(255),
#         unique=True,
#         nullable=False,
#         index=True,
#     )
#     city_id: Mapped[int] = mapped_column(
#         ForeignKey("cities.id"),
#         nullable=False,
#     )
#     user_id: Mapped[int] = mapped_column(
#         ForeignKey("users.id"),
#         nullable=False,
#     )
#     user: Mapped["User"] = relationship(
#         "User",
#         back_populates="company",
#     )
#     company_info: Mapped["CompanyInfo"] = relationship(
#         "CompanyInfo",
#         back_populates="company",
#     )
