from fastapi import APIRouter, Query, Request, Depends
# from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from loguru import logger as log
from vars import DEBUG

# Import Permission checking function
# Accepts Enum object (eg. Permissions.read), string (eg. "read"), or list (eg. [Permissions.read, Permissions.write])
from auth.api_key import verify_permissions 

# Import module config
from .main import Module
# from .schema import PermissionsOptions

# Load router and define permissions at module level if required.
router = APIRouter() #dependencies=[Depends(verify_permissions(Module.permission(PermissionsOptions.read)))])


if DEBUG:
    @router.get('/test-telegram', tags=["Debug"])
    async def test_module(token:str = Query(None), chat_id:str = Query(None)):
        module = Module()
        
        if token:
            try:
                module.connect(token)
                
                res = module.send_message(chat_id, "Test message from API")
                
                return {"status": "ok", "result": res }
                
            except Exception as e:
                return {"status": "error", "result": str(e) }
        
        return {"status": "error", "result": "No token provided" }