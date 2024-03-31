## Hidden routes, used for administrator only UI

from fastapi import APIRouter, Query, Request, Depends, Body
from fastapi.responses import JSONResponse
from loguru import logger as log
from importlib import import_module
from bson import ObjectId
from importlib import import_module, util
from beanie import Document
from os import path
import asyncio
# from utils.datetime import datetime

# from rich import print

# Import module main class
from src.cronmanager import CronManager
from .. import Module
from ..schema import PermissionsOptions, HunchClubPublishPlatformSchema, HunchClubPublishPlatform, TipSchema
# from modules.admin.schema import TokenBearer

# Customized token bearer for direct admin access to this app
# access_token_bearer = TokenBearer()
from auth.api_key import verify_permissions 

# Import module config
from .publish_tips import PublishTips
from tables.config import ModuleConfig
from tables.cron import CronExecutor
from tables.api_keys import ApiKeys

from vars import DEBUG
from models.utils import get_module_folders_generator
from models.permissions import list_permissions
from auth.api_key import generate_api_key

# Load router and define permissions at module level if required.
# Only show in schema is working in DEBUG mode
router = APIRouter( include_in_schema=DEBUG )
module = Module()

# Load module endpoints, and dependencies if required.

@router.get('/platforms', dependencies=[Depends(verify_permissions(Module.permission(PermissionsOptions.write)))])
async def get_publishing_platforms():
    
    try:
        from .model_tips import Tips
        tips_model = Tips(module.config_get('mongodb_url',None), module.config_get('mongodb_database',None))
        
        platforms = await tips_model.fetch_publish_platforms()

        return JSONResponse(status_code=200, content={"data": platforms })
    
    except Exception as e:
        log.error(e)
        return JSONResponse(status_code=500, content={"error": "Error fetching platforms"})

        
@router.post('/platform', dependencies=[Depends(verify_permissions(Module.permission(PermissionsOptions.write)))])
async def create_new_publishing_platform(request: Request, platform:dict = Body(...)):
    
    try:
        log.debug("Creating new platform")
        
        from .model_tips import Tips
        tips_model = Tips(module.config_get('mongodb_url',None), module.config_get('mongodb_database',None))
        
        plat_obj = HunchClubPublishPlatform(**platform)
        # print(plat_obj.model_dump())
        platform = await tips_model.add_publish_platform(plat_obj.model_dump())
        log.debug(plat_obj.model_dump())
        log.debug(platform)
        
        if platform:
            return JSONResponse(status_code=200, content={"status": "success", "id": "??" })
        
    except Exception as e:
        log.error(e)
        return JSONResponse(status_code=500, content={"error": "Error inserting platforms"})
    

@router.patch('/platform/{id}', dependencies=[Depends(verify_permissions(Module.permission(PermissionsOptions.write)))])
async def update_publishing_platform(id:str, platform:dict = Body(...)):
    
    try:
        from .model_tips import Tips
        tips_model = Tips(module.config_get('mongodb_url',None), module.config_get('mongodb_database',None))
        
        # Drop columns that are not allowed to be updated
        _save_dict = {}
        for key, value in platform.items():
            if any(x in key for x in ['next_publish', 'created_at', 'updated_at']):
                continue
            if any(key.endswith(x) for x in ['_help', '_example', '_field' '_options', '_default', '_required', '_min', '_max', '_min_length', '_max_length', '_regex', '_disabled','_options','_placeholder']):
                continue
            _save_dict[key] = value
        
        # log.debug(platform)
        # log.debug(_save_dict)
        # Updates next publish time
        _save_dict['next_publish'] = CronManager.next_iter(platform.get('publish_schedule','30 8 * * *'))
        try:
            plat_obj = HunchClubPublishPlatform(**_save_dict)
            # All good.
        except Exception as e:
            raise Exception(e)
        
        # platform = await tips_model.update_publish_platform(id, plat_obj.model_dump())
        platform = await tips_model.update_publish_platform(id, _save_dict) # Patching only the selected fields
        
        log.debug(platform)
        
        if platform:
            return JSONResponse(status_code=200, content={"status": "success" })
        
    except Exception as e:
        log.error(e)
        return JSONResponse(status_code=500, content={"error": "Error fetching platforms"})


@router.delete('/platform/{id}', dependencies=[Depends(verify_permissions(Module.permission(PermissionsOptions.write)))])
async def delete_publishing_platform(id:str):
    
    try:
        from .model_tips import Tips
        tips_model = Tips(module.config_get('mongodb_url',None), module.config_get('mongodb_database',None))
        
        platform = await tips_model.delete_publish_platform(id)
        
        log.debug(platform)
        
        if platform:
            return JSONResponse(status_code=200, content={"status": "success" })
        
    except Exception as e:
        log.error(e)
        return JSONResponse(status_code=500, content={"error": "Error deleting platform"})



@router.get('/tips/all', dependencies=[Depends(verify_permissions(Module.permission(PermissionsOptions.write)))])
async def get_tips():
    """
    Retrieves tips from the database.
    """
    try:
        from .model_tips import Tips
        tips_model = Tips(module.config_get('mongodb_url',None), module.config_get('mongodb_database',None))
        
        tips = await tips_model.fetch_all_tips()

        return JSONResponse(status_code=200, content={"data": tips })
    
    except Exception as e:
        log.error(e)
        return JSONResponse(status_code=500, content={"error": "Error fetching tips"})
    
    
@router.patch('/tips/{id}', dependencies=[Depends(verify_permissions(Module.permission(PermissionsOptions.write)))])
async def update_tip(id:str, tip:dict = Body(...)):
    """
    Updates a tip in the database.
    """
    try:
        from .model_tips import Tips
        tips_model = Tips(module.config_get('mongodb_url',None), module.config_get('mongodb_database',None))
        
        tip = await tips_model.update_tip(id, tip)
        
        log.debug(tip)
        
        if tip:
            return JSONResponse(status_code=200, content={"status": "success" })
        
    except Exception as e:
        log.error(e)
        return JSONResponse(status_code=500, content={"error": "Error fetching tips"})


@router.get('/tips/fields', dependencies=[Depends(verify_permissions(Module.permission(PermissionsOptions.write)))])
async def get_platform_fields(request: Request):
    return TipSchema().model_dump()


@router.get('/platform/fields', dependencies=[Depends(verify_permissions(Module.permission(PermissionsOptions.write)))])
async def get_platform_fields(request: Request):
    return HunchClubPublishPlatformSchema().model_dump()

@router.post('/platform/test/{id}', dependencies=[Depends(verify_permissions(Module.permission(PermissionsOptions.write)))])
async def test_platform(request: Request, id:str): #platform: HunchClubPublishPlatform):
        
    try:

        from .model_tips import Tips
        tips_model = Tips(module.config_get('mongodb_url',None), module.config_get('mongodb_database',None))
        
        platform = await tips_model.fetch_publish_platforms({"_id": ObjectId(id)})
        
        log.debug([{'id':i['id'], 'name':i['name'], 'channel':i['channel'], 'publish_type':i['publish_type']} for i in platform])
        
        if not platform:
            return JSONResponse(status_code=404, content={"status": "error", "message": "Platform not found" })
        
        if isinstance(platform, list):
            platform = platform[0]
            
        platform = HunchClubPublishPlatform(**platform)
        
        log.info(f"Testing platform {id}...{platform.name}:{platform.channel}")
        
        tips = await module.fetch_tips(platform=platform)
        res = await module.publish_tips(tips, platform, force=True)
        if res == True: # Auto checks if time to publish
            return JSONResponse(status_code=200, content={"status": "success", "message": f"Filtered through {len(tips)} {platform.publish_type.capitalize()} data and published to {platform.name}:{platform.channel}."})
        else:
            raise Exception(res)
        
    except Exception as e:
        log.error(e)
        return JSONResponse( status_code=400, content={"status":"error", "message":str(e)} )

    return {"status":"success"}