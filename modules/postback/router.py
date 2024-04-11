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
from .schema import PostbackProject, PostbackItem
from .main import Module
from fastapi import HTTPException
from beanie import PydanticObjectId

# Import module config

# Load router and define permissions at module level if required.
router = APIRouter()


@router.post("/projects", response_model=PostbackProject)
async def create_project(project: PostbackProject):
    await project.insert()
    return project

@router.put("/projects/{project_id}", response_model=PostbackProject)
async def update_project(project_id: PydanticObjectId, project: PostbackProject):
    stored_project = await PostbackProject.get(project_id)
    if not stored_project:
        raise HTTPException(status_code=404, detail="Project not found")
    await stored_project.replace(project)
    return project

@router.get("/projects", response_model=List[PostbackProject])
async def list_projects():
    projects = await PostbackProject.find_all().to_list()
    return projects

@router.post("/postbacks", response_model=PostbackItem)
async def receive_postback(item: PostbackItem):
    await item.insert()
    return item

@router.get("/postbacks", response_model=List[PostbackItem])
async def list_postback_items():
    items = await PostbackItem.find_all().to_list()
    return items

if DEBUG:
    @router.get("/test_endpoint", tags=["Debug"])
    async def test_endpoint():
        temp = Module()
        return {"module_object":temp, "permission": Module.permission("read"), "active_modules": router.active_modules}
