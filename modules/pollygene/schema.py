from beanie import Document
from fastapi.security import HTTPBasicCredentials
from pydantic import ConfigDict, BaseModel, EmailStr
from enum import Enum
import datetime as dt
from typing import Optional

class PermissionsOptions(Enum):
    read = "read"
    tips_read = "tips_read"
    write = "write"


class LabTests(BaseModel):
    id: str = None
    status: str = None
    code: str = None
    suspend: bool = False
    species: str = None
    mutation: str = None
    comments: str = None
    test_type: str = None
    date_arrived: dt.datetime = None
    date_submit_results: dt.datetime = None
    date_publish_results: dt.datetime = None
    lab_user: str = None
    test_results: str = None
    test_results_options: list = None
    lab_feedback: str = None
    
    
    
    