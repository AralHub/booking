from pydantic import BaseModel

from app.schemas.hotel import TIME_FIELD, TIME_FIELD_UPDATE


class RuleBase(BaseModel):
    check_in_from: TIME_FIELD
    check_in_until: TIME_FIELD_UPDATE
    check_out_from: TIME_FIELD
    check_out_until: TIME_FIELD_UPDATE


class RuleCreate(RuleBase):
    pass


class RuleCreateInternal(RuleCreate):
    hotel_id: int


class RuleUpdate(BaseModel):
    check_in_from: TIME_FIELD_UPDATE
    check_in_until: TIME_FIELD_UPDATE
    check_out_from: TIME_FIELD_UPDATE
    check_out_until: TIME_FIELD_UPDATE


class RuleUpdateInternal(RuleUpdate):
    hotel_id: int


class RuleFilter(BaseModel):
    id: int | None = None
    hotel_id: int | None = None
    check_in_from: TIME_FIELD_UPDATE | None = None
    check_in_until: TIME_FIELD_UPDATE | None = None
    check_out_from: TIME_FIELD_UPDATE | None = None
    check_out_until: TIME_FIELD_UPDATE | None = None
