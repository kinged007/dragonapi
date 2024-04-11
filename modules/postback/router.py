from fastapi import APIRouter, Query, Request, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse
# from fastapi.responses import JSONResponse
from loguru import logger as log
import os, asyncio
from enum import Enum
from importlib import import_module
import traceback


# Get global cache
from utils.cache import global_cache

# from auth.api_key import api_key_bearer, get_owner, generate_api_key
from models.utils import get_module_folders_generator
from vars import DEBUG

# Import Permission checking function
# Accepts Enum object (eg. Permissions.read), string (eg. "read"), or list (eg. [Permissions.read, Permissions.write])
from auth.api_key import verify_permissions 

# Import module config

# Load router and define permissions at module level if required.
router = APIRouter()


if DEBUG:
    @router.get("/test_endpoint", tags=["Debug"])
    async def test_endpoint():
        from .main import Module
        temp = Module()
        return {"module_object":temp, "permission": Module.permission("read"), "active_modules": router.active_modules}
