import datetime
from pydantic import BaseModel
from datetime import datetime


class RuleBase(BaseModel):
    check_in_from: datetime
    check_in_until: datetime
    check_out_from: datetime
    check_out_until: datetime
    is_pet_allowed: bool


class RuleCreate(RuleBase):
    hotel_id: int


class RuleCreateInternal(RuleCreate):
    pass


class RuleUpdate(BaseModel):
    check_in_from: datetime | None = None
    check_in_until: datetime | None = None
    check_out_from: datetime | None = None
    check_out_until: datetime | None = None
    is_pet_allowed: bool | None = None


class RuleUpdateInternal(RuleUpdate):
    hotel_id: int


class RuleFilter(BaseModel):
    id: int | None = None
    check_in_from: datetime | None = None
    check_in_until: datetime | None = None
    check_out_from: datetime | None = None
    check_out_until: datetime | None = None
    is_pet_allowed: bool | None = None
    hotel_id: int | None = None
