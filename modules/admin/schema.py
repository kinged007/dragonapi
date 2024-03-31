# Beanie tables to Load on Startup + Schema classes to be used throughout the module
# Classes with the Document class are automatically loaded into the database at startup

# from beanie import Document
from mongoengine import connect, Document
from pydantic import ConfigDict, BaseModel, EmailStr
from enum import Enum
from os import getenv

from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# class Example(Document):
#     name: str
#     email: EmailStr

class PermissionsOptions(Enum):
    read = "read"
    write = "write"
    environment_read = "environment_read"
    
class TokenBearer(HTTPBearer):

    def __init__(self, auto_error: bool = True):
        super(TokenBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(TokenBearer, self).__call__(request)
        # print("Credentials :", credentials)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid Access Token")
            
            _token = getenv("ADMIN_TOKEN", None)
            
            if not _token:
                raise HTTPException(status_code=403, detail="Server Error: Invalid Configuration")
            
            if not credentials.credentials == _token:
                raise HTTPException(status_code=403, detail="Invalid Access Token")
            
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid Access Token")
