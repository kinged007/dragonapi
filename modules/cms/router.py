from fastapi import APIRouter, Query, Request, Depends
# from fastapi.responses import JSONResponse
# from loguru import logger as log
from os import path
from enum import Enum
from loguru import logger as log
from vars import DEBUG
# from rich import print

# Import module config
from .main import Module

# Import Permission checking function
# Accepts Enum object (eg. Permissions.read), string (eg. "read"), or list (eg. [Permissions.read, Permissions.write])
from auth.api_key import verify_permissions 

# Import app models
# from models.utils import html_to_markdown, markdown_to_html

# Load router and define permissions at module level if required.
router = APIRouter()

data_folder = path.join(path.dirname(__file__), 'data') # pending change


# Load module endpoints, and dependencies if required.
# @router.get('/cms/publish')
async def get_report(request: Request, query: str = Query()):
    
    return {"data":query} #report

# from .routes import projects
# from .routes import publish

# Project Manager endpoints
# router.include_router(projects.router, prefix="/projects", dependencies=[Depends(verify_permissions(Module().permission('write')))])

# # Publishing endpoints
# router.include_router(publish.router, prefix="/publish", dependencies=[Depends(verify_permissions(Module().permission('read')))])