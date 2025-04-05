from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.user import GENDER_TYPES
from app.schemas.field_validation import (
    BIRTHDAY_FIELD,
    GENDER_FIELD,
    NAME_FIELD,
    NAME_FIELD_UPDATE,
    PASSWORD_FIELD,
    PHONE_NUMBER_FIELD,
    PHONE_NUMBER_FIELD_UPDATE,
    VERIFY_CODE_FIELD,
)


class CorpUserBase(BaseModel):
    first_name: str
    last_name: str
    position: str
    phone_number: PHONE_NUMBER_FIELD
    password: PASSWORD_FIELD


class CorpUserRead(CorpUserBase):
    id: int
    company_name: str | None = None


class CorpUserCreate(CorpUserBase):
    company_name: str
    address: str


class CorpUserCrateInternal(CorpUserBase):
    company_id: int
    is_verified: bool = False
    is_fully_registered: bool = False
    is_active: bool = False


class CorpUserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    position: str | None = None


class CorpUserFilter(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    position: str | None = None
    phone_number: str | None = None
    company_id: int | None = None
    is_verified: bool | None = None
    is_fully_registered: bool | None = None
    is_active: bool | None = None
