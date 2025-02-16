import uuid as uuid_pkg
from datetime import UTC, datetime

from pydantic import BaseModel, Field, field_serializer


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
