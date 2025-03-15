from pydantic import BaseModel, ConfigDict

from .field_validation import (
    NAME_FIELD_UPDATE,
    PHONE_NUMBER_FIELD,
    PHONE_NUMBER_FIELD_UPDATE,
)


class PartnerBase(BaseModel):
    phone_number: PHONE_NUMBER_FIELD
    first_name: NAME_FIELD_UPDATE
    last_name: NAME_FIELD_UPDATE


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
    phone_number: PHONE_NUMBER_FIELD_UPDATE
    is_active: bool | None = None
    is_verified: bool | None = None
    is_fully_registered: bool | None = None
    model_config = ConfigDict(extra="forbid")


class PartnerFilter(BaseModel):
    id: int | None = None
    phone_number: PHONE_NUMBER_FIELD_UPDATE | None = None
    first_name: NAME_FIELD_UPDATE | None = None
    last_name: NAME_FIELD_UPDATE | None = None
    is_active: bool | None = None
    is_verified: bool | None = None
    is_fully_registered: bool | None = None
