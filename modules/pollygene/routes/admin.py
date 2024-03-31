# Admin routes for Pollygene module
# Path: modules/pollygene/routes/admin.py
# This file houses the admin routes for the module. It is responsible for handling the module's admin endpoints and shared resources
# Primary database interaction will be with Directus which is the Pollygene Admin UI.


from fastapi import APIRouter, Query, Request, Depends, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from loguru import logger as log
# from utils.datetime import datetime
from typing import List

from vars import DEBUG

# Import module main class
from .. import Module
from ..schema import PermissionsOptions, LabTests

# Import Permission checking function
# Accepts Enum object (eg. PermissionsOptions.read), string (eg. "read"), or list (eg. [PermissionsOptions.read, PermissionsOptions.write])
from auth.api_key import verify_permissions

# Load router and define permissions at module level if required.
# router = APIRouter(dependencies=[Depends(verify_permissions(Module.permission(PermissionsOptions.read)))], tags=["Extra Tags"])
router = APIRouter()

# Load module and config
module = Module()

# Load module endpoints, and dependencies if required.

#### Routes

###### V1
# V1 endpoints communicate directly with Wordpress instead of Directus, as a temporary measure until Directus is fully implemented.
