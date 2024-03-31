## Hidden routes, used for administrator only UI

from fastapi import FastAPI, Request, APIRouter, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from loguru import logger as log
from importlib import import_module
from bson import ObjectId
from importlib import import_module, util
from beanie import Document
from os import path
import inspect


templates = Jinja2Templates(directory="modules/admin/views/templates")

# from rich import print

# Import module main class
from .. import Module
from ..schema import TokenBearer, PermissionsOptions

# Customized token bearer for direct admin access to this app
access_token_bearer = TokenBearer()

# Import module config
# from modules._template.config import Config
from tables.config import ModuleConfig
from tables.cron import CronExecutor
from tables.api_keys import ApiKeys

from vars import DEBUG
from models.utils import get_module_folders_generator
from models.permissions import list_permissions
from auth.api_key import generate_api_key, verify_permissions

# Load router and define permissions at module level if required.
# Only show in schema is working in DEBUG mode
router = APIRouter( include_in_schema=DEBUG )
module = Module()

# Main admin panel page. 
@router.get('/panel')
async def access_admin_panel(request: Request):
    
    # Load template
    
    return templates.TemplateResponse("dashboard_sample.html", {"request": request, "id": 12})


