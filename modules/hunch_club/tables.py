# from beanie import Document
from mongoengine import connect, Document
from fastapi.security import HTTPBasicCredentials
from pydantic import ConfigDict, BaseModel, EmailStr

