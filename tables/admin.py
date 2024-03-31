from beanie import Document
from fastapi.security import HTTPBasicCredentials
from pydantic import ConfigDict, BaseModel, EmailStr


class Admin(Document):
    name: str
    email: EmailStr
    password: str

    class Settings:
        name = "admin"
        
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "Abdulazeez Abdulazeez Adeshina",
            "email": "abdul@youngest.dev",
            "password": "3xt3m#"
        }
    })


class AdminSignIn(HTTPBasicCredentials):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "username": "abdul@youngest.dev", # must be username because that is how HTTPBasicCredentials is configured.
            "password": "3xt3m#"
        }
    })


class AdminData(BaseModel):
    name: str
    email: EmailStr
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "Abdulazeez Abdulazeez Adeshina",
            "email": "abdul@youngest.dev",
        }
    })