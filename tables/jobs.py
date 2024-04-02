from beanie import Document
from fastapi.security import HTTPBasicCredentials
from pydantic import ConfigDict, BaseModel, EmailStr
from typing import Type, Any

class Job(Document):
    
    
    # TODO Add function / endpoint name so we know which function the job belongs to, so this job queue can be used for all functions.
    
    data: Any = {}
    status: str = "executing"
    project_id: str
    
    date_created: float = 0
    date_completed: float = 0
    
    

    class Settings:
        name = "job"
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "_id": "60f3f2f01b7d8b4a9e4a9e0f",
            "data": {
                "...": "..."
            },
            "status": "executing",
            "project_id": "15124f23g235232g24t24y53"
        }
    })