import uuid as uuid_pkg
from datetime import UTC, datetime

from pydantic import (
    BaseModel,
    Field,
    field_serializer,
)

from .field_validation import HOTEL_NAME_FIELD


class UUIDSchema(BaseModel):
    uuid: uuid_pkg.UUID = Field(default=uuid_pkg.uuid4)


class TimestampSchema(BaseModel):
    created_at: datetime = Field(default=datetime.now(UTC))
    updated_at: datetime | None = Field(default=None)

    @field_serializer("created_at", "updated_at")
    def serialize_dt(self, value: datetime | None) -> str | None:
        if value is not None:
            return value.isoformat()
        return None


class SoftDeleteSchema(BaseModel):
    deleted_at: datetime | None = Field(default=None)
    is_deleted: bool = Field(default=False)

    @field_serializer("deleted_at")
    def serialize_dates(self, value: datetime | None) -> str | None:
        if value is not None:
            return value.isoformat()
        return None


class MultilingualNameBase(BaseModel):
    """Базовый класс для многоязычных имен с отдельными полями"""

    name_ru: HOTEL_NAME_FIELD
    name_en: HOTEL_NAME_FIELD
    name_uz: HOTEL_NAME_FIELD
    name_kr: HOTEL_NAME_FIELD

    def to_dict_name(self):
        return {
            "ru": self.name_ru,
            "en": self.name_en,
            "uz": self.name_uz,
            "kr": self.name_kr,
        }


class MultilingualDescriptionBase(BaseModel):
    """Миксин для многоязычных описаний"""

    description_ru: str
    description_en: str
    description_uz: str
    description_kr: str

    def to_dict_description(self):
        return {
            "ru": self.description_ru,
            "en": self.description_en,
            "uz": self.description_uz,
            "kr": self.description_kr,
        }
