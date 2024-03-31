from fastapi import APIRouter, Query, Request, Depends
from fastapi.responses import JSONResponse
from loguru import logger as log

# Import module main class
from . import Module
from .schema import PermissionsOptions

# Import Permission checking function
# Accepts Enum object (eg. PermissionsOptions.read), string (eg. "read"), or list (eg. [PermissionsOptions.read, PermissionsOptions.write])
from auth.api_key import verify_permissions 

# Import module config
# from modules._template.config import Config

# Load router and define permissions at module level if required.
# router = APIRouter(dependencies=[Depends(verify_permissions(Module.permission(PermissionsOptions.read)))], tags=["Extra Tags"])
router = APIRouter()

# TODO provide a simple endpoint to make translations
@router.post('/text', dependencies=[Depends(verify_permissions(Module.permission(PermissionsOptions.write)))])
async def translate(request: Request, query: str = Query()):
    return {"data": query}