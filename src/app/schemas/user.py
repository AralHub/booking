from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.user import GENDER_TYPES

from .field_validation import (
    BIRTHDAY_FIELD,
    GENDER_FIELD,
    NAME_FIELD,
    NAME_FIELD_UPDATE,
    PASSWORD_FIELD,
    PHONE_NUMBER_FIELD,
    PHONE_NUMBER_FIELD_UPDATE,
    VERIFY_CODE_FIELD,
)
from .mixins import TimestampSchema

# region Login


class PhoneNumber(BaseModel):
    phone_number: PHONE_NUMBER_FIELD


class LoginUser(BaseModel):
    phone_number: PHONE_NUMBER_FIELD
    password: PASSWORD_FIELD

    model_config = ConfigDict(extra="forbid")


class VerifyPhoneNumber(BaseModel):
    phone_number: PHONE_NUMBER_FIELD
    code: VERIFY_CODE_FIELD

    model_config = ConfigDict(extra="forbid")


# endregion


# region User
class UserBase(BaseModel):
    phone_number: PHONE_NUMBER_FIELD
    first_name: NAME_FIELD
    last_name: NAME_FIELD


class UserRead(UserBase, TimestampSchema):
    id: int
    birthday: Optional[BIRTHDAY_FIELD] = None
    gender: Optional[GENDER_FIELD] = None
    country_id: Optional[int] = None
    is_active: bool
    is_verified: bool
    is_fully_registered: bool


class UserCreate(UserBase):
    password: PASSWORD_FIELD


class UserCreateInternal(UserCreate):
    is_active: bool = False
    is_verified: bool = False
    is_fully_registered: bool = False
    model_config = ConfigDict(extra="forbid")


class UserUpdate(BaseModel):
    first_name: NAME_FIELD_UPDATE
    last_name: NAME_FIELD_UPDATE
    birthday: BIRTHDAY_FIELD | None = None
    gender: GENDER_FIELD | None = None
    country_id: int | None = None
    model_config = ConfigDict(extra="forbid")


class UserUpdateInternal(UserUpdate):
    phone_number: PHONE_NUMBER_FIELD_UPDATE
    is_active: bool | None = None
    is_verified: bool | None = None
    is_fully_registered: bool | None = None
    is_deleted: bool | None = None
    deleted_at: datetime | None = None
    updated_at: datetime | None = None


class UserFilter(BaseModel):
    id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    birthday: datetime | None = None
    gender: GENDER_TYPES | None = None
    role_id: int | None = None
    is_verified: bool | None = None
    is_active: bool | None = None
    is_fully_registered: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    is_deleted: bool | None = None
    deleted_at: datetime | None = None


# endregion


# region Token
class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class RefreshToken(BaseModel):
    refresh_token: str | None = None


class TokenBlacklistBase(BaseModel):
    jti: str
    expires_at: datetime


class TokenBlacklistCreate(TokenBlacklistBase):
    is_blacklisted: bool = True


class TokenBlacklistUpdate(TokenBlacklistBase):
    pass


class TokenBlacklistFilter(BaseModel):
    id: int | None = None
    jti: str | None = None
    expires_at: datetime | None = None
    is_blacklisted: bool | None = None


# endregion
