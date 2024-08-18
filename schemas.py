from pydantic import BaseModel


class RequestModel(BaseModel):
    city: str
    professional_role: str