from pydantic import BaseModel


class CompanyBase(BaseModel):
    company_name: str
    address: str
    inn: str
    bank_name: str
    city_id: int


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    company_name: str | None = None
    address: str | None = None
    inn: str | None = None
    bank_name: str | None = None
    city_id: int | None = None
