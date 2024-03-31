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

@router.get("/ping")
@global_cache.async_cache(ttl=5 if DEBUG else 15, namespace="common")
async def ping(background: BackgroundTasks):
    """ Simple endpoint to check the health status of the API server. """
    
    # Use this function to find cron jobs from modules and send to background
    background.add_task(run_cron_manager)
    
    return {
        "status_code": 200,
        "response_type": "success",
        "description": "Ping Received",
        "data": False
    } 


async def run_cron_manager():
    """ Simple endpoint to execute background and repeated tasks. """

    # Manage the timing of the cron manager    
    execute_cron_manager_wait = global_cache.get('execute_cron_manager_wait')

    if execute_cron_manager_wait == True:
        log.debug("Not time to run cron manager yet...")
        return

    global_cache.set('execute_cron_manager_wait', True, ttl=15 if DEBUG else 180)
    
    log.info("Executing cron jobs from modules...")

    for module_folder, module_name in get_module_folders_generator():
        try:
            # This is the new version of module imports
            log.debug(f"Loading module '{module_name}'")
            module = import_module(f'modules.{module_name}')
            module = module.Module()

            if not module:
                log.error(f"Module '{module_name}' failed to load")
                await asyncio.sleep(0.1)
                continue
            
            log.info(f"Module '{module_name}' loaded")
            await asyncio.sleep(0.1)
            
            # Check if cron should run. BaseModule has a function for this. Method also refreshes config, and executes the run_cron() method in the module.
            await module._check_and_execute_cron()

        except Exception as e:
            log.error(e)
            print(traceback.format_exc())