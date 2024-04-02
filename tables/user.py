from typing import Optional, Any

from beanie import Document
from pydantic import ConfigDict, BaseModel, EmailStr

# TODO Users is a feature for developers. Not a requirement. So lets move this out to V1.

class User(Document):
    project_id: str # project_id owner
    fullname: str
    email: EmailStr
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "fullname": "Abdulazeez Abdulazeez Adeshina",
            "email": "abdul@school.com",
        }
    })


class UpdateUserModel(BaseModel):
    fullname: Optional[str] = None
    email: Optional[EmailStr] = None

    class Settings:
        name = "user"
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "fullname": "Abdulazeez Abdulazeez",
            "email": "abdul@school.com",
        }
    })


class Response(BaseModel):
    status_code: int
    response_type: str
    description: str
    data: Optional[Any] = None
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "status_code": 200,
            "response_type": "success",
            "description": "Operation successful",
            "data": "Sample data"
        }
    })