from fastapi import APIRouter, Query, Request, Depends
from fastapi.responses import JSONResponse
from loguru import logger as log


from vars import DEBUG

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

# Load module endpoints, and dependencies if required.
# @router.get('/test', dependencies=[Depends(verify_permissions(Module.permission(PermissionsOptions.read)))])

if DEBUG:
    @router.get('/test-module', dependencies=[Depends(verify_permissions(Module.permission(PermissionsOptions.write)))], tags=["Debug"])
    async def test_module(request: Request):
        
        module = Module()
        await module._check_and_execute_cron()
        
        return {
            "permission": module.permission(PermissionsOptions.write),
            "module_object":module, 
        } 

