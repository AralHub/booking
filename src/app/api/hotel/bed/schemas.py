from pydantic import BaseModel


class BedBase(BaseModel): ...


class BedCreate(BedBase):
    pass


class BedCreateInternal(BedCreate):
    pass


class BedUpdate(BedBase):
    pass


class BedUpdateInternal(BedUpdate):
    pass


class BedFilter(BaseModel):
    id: int | None = None
