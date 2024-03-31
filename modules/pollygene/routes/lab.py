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

# POST /lab/v1/samples/recieve
@router.post('/v1/samples/receive') # dependencies
async def receive_sample(request: Request, body: List[LabTests] = Body(...)) -> JSONResponse:
    """
    Receive a sample from a lab user.

    """
    await module.init()

    async def verify_sample(sample: LabTests) -> bool:
        """
        Verify a sample by finding sample in wordpress and changing status.
        """
        # Search for order with sample code

        # If found, change status to "Received"

        # If not found, return False

        module.wp.wc.test()

        return True


    output = {"status": "ok", "message": "Sample received.", "failed": []}

    # Loop through body and verify each sample
    for sample in body:
        # Verify the sample Verify method will be here for v1.
        if not await verify_sample(sample):
            sample.status = "Failed to verify sample."
            output['failed'].append(sample.model_dump(exclude_none=True, exclude_unset=True))
            print(output)


    json_compatible_output = jsonable_encoder(output)
    return JSONResponse(status_code=200, content=json_compatible_output)
