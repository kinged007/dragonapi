
from fastapi import APIRouter, Query, Request, Depends, Body
from fastapi.responses import JSONResponse
from loguru import logger as log
from importlib import import_module
from bson import ObjectId
from importlib import import_module, util
from beanie import Document
from os import path
import inspect
from time import time
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
from src.configmanager import ConfigManager
config_manager = ConfigManager()

from vars import DEBUG
from models.utils import get_module_folders_list
from models.permissions import list_permissions
from auth.api_key import generate_api_key, verify_permissions

from utils.cache import global_cache

# Load router and define permissions at module level if required.
# Only show in schema is working in DEBUG mode
router = APIRouter( include_in_schema=DEBUG )
module = Module()

from src.task_manager import TaskManager
queue = TaskManager.queue # gets the rq.Queue object

@router.get('/queues')
async def redis_queue_queues(request: Request):
    """
    Gets a list of all queues in the Redis Queue
    """
    pass