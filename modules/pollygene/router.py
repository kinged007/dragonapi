from fastapi import APIRouter, Query, Request, Depends
from fastapi.responses import JSONResponse
from loguru import logger as log
# from utils.datetime import datetime

from vars import DEBUG

# Import module main class
from . import Module
from .schema import PermissionsOptions
from utils.cache import global_cache

# Import Permission checking function
# Accepts Enum object (eg. PermissionsOptions.read), string (eg. "read"), or list (eg. [PermissionsOptions.read, PermissionsOptions.write])
from auth.api_key import verify_permissions

# Load router and define permissions at module level if required.
# router = APIRouter(dependencies=[Depends(verify_permissions(Module.permission(PermissionsOptions.read)))], tags=["Extra Tags"])
router = APIRouter()

# Load module and config
# module = Module()

# Load module endpoints, and dependencies if required.

if DEBUG:

    @router.get('/test-pollygene', tags=["Debug"]) #, dependencies=[     Depends(verify_permissions(Module.permission(PermissionsOptions.write)))    ])
    @global_cache.async_cache(ttl=10, key=lambda param: f"test_key_{param}")
    async def test_module(param:str = Query(None)) :
        # module = Module()

        # await module._check_and_execute_cron(True)
        log.warning("Test endpoint called.")
        # return {"module_object":module, "permission": module.permission("read")}
        log.debug(global_cache.storage)

        return JSONResponse(content={"test":"success"})


from .routes import admin, public, lab
router.include_router(admin.router, prefix="/admin")
router.include_router(lab.router, prefix="/lab")
router.include_router(public.router )
