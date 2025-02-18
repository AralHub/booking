from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.db.schema_mixins import TimestampSchema
from app.api.user.models import GENDER_TYPES, ROLE_TYPES

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

EMAIL_FIELD = Annotated[
    EmailStr | None,
    Field(
        examples=["user.userson@example.com"],
        default=None,
    ),
]
BIRTHDAY_FIELD = Annotated[
    datetime | None,
    Field(
        examples=["1990-01-01"],
        default=None,
    ),
]
GENDER_FIELD = Annotated[
    GENDER_TYPES,
    Field(
        examples=["MALE"],
        default=GENDER_TYPES.MALE,
    ),
]
ROLE_TYPE_FIELD = Annotated[
    ROLE_TYPES,
    Field(
        examples=["USER"],
        default=ROLE_TYPES.USER,
    ),
]
VERIFY_CODE_FIELD = Annotated[
    str,
    Field(pattern=r"^\d{5}$", examples=["12345"]),
]


class Login(BaseModel):
    phone_number: PHONE_NUMBER_FIELD
    password: PASSWORD_FIELD

    model_config = ConfigDict(extra="forbid")


class PhoneNumber(BaseModel):
    phone_number: PHONE_NUMBER_FIELD


class VerifyPhoneNumber(PhoneNumber):
    code: VERIFY_CODE_FIELD

    model_config = ConfigDict(extra="forbid")


class UserBase(BaseModel):
    phone_number: PHONE_NUMBER_FIELD
    email: EMAIL_FIELD
    first_name: NAME_FIELD
    last_name: NAME_FIELD
    birthday: BIRTHDAY_FIELD
    gender: GENDER_FIELD


class UserRead(UserBase, TimestampSchema):
    id: int
    phone_number: PHONE_NUMBER_FIELD
    is_superuser: bool
    is_active: bool
    is_verified: bool
    is_fully_registered: bool


class UserCreate(UserBase):
    role: ROLE_TYPE_FIELD


class UserCreateInternal(UserCreate):
    role: ROLE_TYPE_FIELD
    is_active: bool = False
    is_verified: bool = True
    is_fully_registered: bool = False

    model_config = ConfigDict(extra="forbid")


class UserUpdate(BaseModel):

    name: NAME_FIELD_UPDATE

    model_config = ConfigDict(extra="forbid")


class UserUpdateInternal(UserUpdate):
    phone_number: PHONE_NUMBER_FIELD_UPDATE
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
