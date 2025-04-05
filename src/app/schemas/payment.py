from pydantic import BaseModel

from .mixins import MultilingualNameBase, MultilingualNameBaseUpdate


class PaymentBase(MultilingualNameBase):
    pass


class PaymentRead(BaseModel):
    id: int
    name: dict[str, str]


class PaymentCreate(MultilingualNameBase):
    pass


class PaymentCreateInternal(BaseModel):
    name: dict[str, str]


class PaymentUpdate(MultilingualNameBaseUpdate):
    pass


class PaymentUpdateInternal(BaseModel):
    name: dict[str, str]


class PaymentFilter(BaseModel):
    id: int | None = None
