from pydantic import BaseModel, ConfigDict

from app.api.user.schemas import (
    NAME_FIELD,
    NAME_FIELD_UPDATE,
    PHONE_NUMBER_FIELD,
)


class PartnerBase(BaseModel):
    phone_number: PHONE_NUMBER_FIELD
    first_name: NAME_FIELD
    last_name: NAME_FIELD


class PartnerRead(PartnerBase):
    id: int


class PartnerCreate(PartnerBase):
    model_config = ConfigDict(extra="forbid")


class PartnerCreateInternal(PartnerCreate):
    is_active: bool = False
    is_verified: bool = True
    is_fully_registered: bool = False
    model_config = ConfigDict(extra="forbid")


class PartnerUpdate(PartnerBase):
    first_name: NAME_FIELD_UPDATE
    last_name: NAME_FIELD_UPDATE
    model_config = ConfigDict(extra="forbid")


class PartnerUpdateInternal(PartnerUpdate):
    is_active: bool
    is_verified: bool
    is_full_verified: bool
    model_config = ConfigDict(extra="forbid")


class PartnerFilter(BaseModel):
    id: int | None = None
    phone_number: PHONE_NUMBER_FIELD | None = None
    first_name: NAME_FIELD | None = None
    last_name: NAME_FIELD | None = None
