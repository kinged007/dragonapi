from fastapi import APIRouter, Query, Request, Depends
from fastapi.responses import JSONResponse
from loguru import logger as log
# from utils.datetime import datetime

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

# Import module main class
from . import Module
# from .src.publish_tips import PublishTips
from .schema import PermissionsOptions, HunchClubPublishPlatformSchema


# Load module endpoints, and dependencies if required.

if DEBUG:
    @router.get('/test_hunch_club', dependencies=[
        Depends(verify_permissions(Module.permission(PermissionsOptions.write)))
    ], tags=["Debug"])
    async def test_endpoint(request: Request):
        
        module = Module()
        await module._check_and_execute_cron()
        
        return {"module_object":module, "permission": module.permission("read")} 







# Admin UI
from .src import admin_routes
router.include_router(admin_routes.router)