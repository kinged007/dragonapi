from fastapi import APIRouter, Query, Request, Depends, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, Response, FileResponse
from loguru import logger as log
# from importlib import import_module
# import ObjectId
# from bson import ObjectId

# from rich import print

# Import module main class
from . import Module
# from .schema import PermissionsOptions, TokenBearer

# Customized token bearer for direct admin access to this app
# access_token_bearer = TokenBearer()

# Import Permission checking function
# Accepts Enum object (eg. PermissionsOptions.read), string (eg. "read"), or list (eg. [PermissionsOptions.read, PermissionsOptions.write])
# from auth.api_key import verify_permissions 

# Import module config
# from modules._template.config import Config
# from tables.config import ModuleConfig
# from tables.cron import CronExecutor
# from models.utils import get_module_folders_generator

# Load router and define permissions at module level if required.
# router = APIRouter(dependencies=[Depends(verify_permissions(Module.permission(PermissionsOptions.read)))], tags=["Extra Tags"])
router = APIRouter()

module = Module()

from .src import ui_routes

router.include_router(ui_routes.router, prefix="")

# Load module endpoints, and dependencies if required.
# @router.get('/test', dependencies=[Depends(verify_permissions(Module.permission(PermissionsOptions.read)))])

# NOTE Mounting static files through APIRouter() does not work. Workaround is using our own endpoint to serve static files.
# TODO Create an admin panel page to manage the API and conifuigurations
@router.get("/static/{rest_of_path:path}", response_class=Response, include_in_schema=False)
async def static_files(
    rest_of_path: str,
):
    return FileResponse(f"modules/admin/static/{rest_of_path}")

from .src import admin_panel
router.include_router(admin_panel.router, prefix="")
