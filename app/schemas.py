from typing import Optional
from pydantic import BaseModel


class RequestModel(BaseModel):
    city: str
    professional_role: str


class JobCreate(BaseModel):
    name: str
    alternate_url: str
    area_name: str
    professional_roles: str
    salary_from: int | None = None
    salary_to: int | None = None


class VacancyFilter(BaseModel):
    name: Optional[str] = None
    area_name: Optional[str] = None
    professional_roles: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None


class VacancyResponse(BaseModel):
    id: int
    name: str
    alternate_url: str
    area_name: str
    professional_roles: str
    salary_from: Optional[int] = None
    salary_to: Optional[int] = None

    class Config:
        orm_mode = True