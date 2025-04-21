# from typing import TYPE_CHECKING

# from sqlalchemy import ForeignKey, String
# from sqlalchemy.orm import Mapped, mapped_column, relationship

# from app.models import Base
# from app.models.mixins import IntIdPkMixin, TimestampMixin

# if TYPE_CHECKING:
#     from app.models.company import Company


# class CompanyInfo(
#     IntIdPkMixin,
#     TimestampMixin,
#     Base,
# ):
#     email: Mapped[str] = mapped_column(
#         String(255),
#         unique=True,
#         nullable=True,
#     )
#     address: Mapped[str] = mapped_column(
#         String(255),
#         nullable=True,
#     )
#     inn: Mapped[str] = mapped_column(
#         String(20),
#         unique=True,
#         nullable=False,
#         index=True,
#     )
#     bank_name: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )
#     company_id: Mapped[int] = mapped_column(
#         ForeignKey("companies.id"),
#     )
#     company: Mapped["Company"] = relationship(
#         "Company",
#         back_populates="company_info",
#     )
