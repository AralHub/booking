from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.core.db.schema_mixins import TimestampSchema

# Константы
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 30


# Общие поля с аннотациями
NAME_FIELD = Annotated[
    str,
    Field(
        min_length=MIN_NAME_LENGTH,
        max_length=MAX_NAME_LENGTH,
        examples=["User Userson"],
    ),
]
NAME_FIELD_UPDATE = Annotated[
    str | None,
    Field(
        min_length=MIN_NAME_LENGTH,
        max_length=MAX_NAME_LENGTH,
        examples=["User Userberg"],
        default=None,
    ),
]
PASSWORD_FIELD = Annotated[
    str,
    Field(
        pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$",
        examples=["pass123"],
    ),
]

PHONE_NUMBER_FIELD = Annotated[
    str, Field(pattern=r"^[1-9]\d{1,14}$", examples=["998991234567"])
]

PHONE_NUMBER_FIELD_UPDATE = Annotated[
    str | None,
    Field(
        pattern=r"^[1-9]\d{1,14}$",
        examples=["998991112233"],
        default=None,
    ),
]
VERIFY_CODE_FIELD = Annotated[
    str,
    Field(pattern=r"^\d{5}$", examples=["12345"]),
]


class SuperAdminLogin(BaseModel):
    phone_number: PHONE_NUMBER_FIELD
    password: PASSWORD_FIELD


class UserPhoneNumber(BaseModel):
    phone_number: PHONE_NUMBER_FIELD


class UserVerifyPhoneNumber(UserPhoneNumber):
    code: VERIFY_CODE_FIELD

    model_config = ConfigDict(extra="forbid")


class UserCreateViaPhoneNumberInternal(UserPhoneNumber):
    name: NAME_FIELD
    is_active: bool = False
    is_verified: bool = True
    is_fully_registered: bool = False

    model_config = ConfigDict(extra="forbid")


class UserProfileCreate(BaseModel):
    name: NAME_FIELD


class UserBase(BaseModel):
    """Базовая схема пользователя с основными полями."""

    name: NAME_FIELD
    phone_number: PHONE_NUMBER_FIELD


class UserRead(UserBase, TimestampSchema):
    id: int
    is_superuser: bool = False
    is_active: bool = True
    is_verified: bool = False
    is_fully_registered: bool = False
    tier_id: int | None = None


class UserUpdate(BaseModel):
    """Схема обновления данных пользователя."""

    model_config = ConfigDict(extra="forbid")

    name: NAME_FIELD_UPDATE
    phone_number: PHONE_NUMBER_FIELD_UPDATE


class UserNameUpdate(BaseModel):
    name: NAME_FIELD_UPDATE


class UserUpdateInternal(UserUpdate):
    id: int
    updated_at: datetime | None = None
    is_active: bool = True
    is_fully_registered: bool = True


class UserFilter(BaseModel):
    id: int | None = None
    name: str | None = None
    phone_number: str | None = None

    is_verified: bool | None = None
    is_active: bool | None = None
    is_fully_registered: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


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
