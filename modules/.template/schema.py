# Beanie tables to Load on Startup + Schema classes to be used throughout the module
# Classes with the Document class are automatically loaded into the database at startup

from beanie import Document
from pydantic import ConfigDict, BaseModel, EmailStr
from enum import Enum


# class Example(Document):
#     name: str
#     email: EmailStr

class PermissionsOptions(Enum):
    read = "read"
    write = "write"