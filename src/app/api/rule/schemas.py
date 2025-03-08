from datetime import time

from pydantic import BaseModel


class RuleBase(BaseModel):
    check_in_from: time
    check_in_until: time | None = None
    check_out_from: time
    check_out_until: time | None = None


class RuleCreate(RuleBase):
    pass


class RuleCreateInternal(RuleCreate):
    hotel_id: int


class RuleUpdate(BaseModel):
    check_in_from: time | None = None
    check_in_until: time | None = None
    check_out_from: time | None = None
    check_out_until: time | None = None


class RuleUpdateInternal(RuleUpdate):
    hotel_id: int


class RuleFilter(BaseModel):
    id: int | None = None
    check_in_from: time | None = None
    check_in_until: time | None = None
    check_out_from: time | None = None
    check_out_until: time | None = None
