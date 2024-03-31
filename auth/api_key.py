from typing import Annotated
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from beanie import PydanticObjectId
from enum import Enum
import random, string, os
from loguru import logger as log
# from config.config import Settings
from tables.api_keys import ApiKeys
from tables.admin import Admin
from tables.project import Project

# oauth2_scheme = OAuth2PasswordBearer( tokenUrl="tokenUrl")  # use token authentication


# def api_key_auth(api_key: str = Depends(oauth2_scheme)):
#     api_keys = [] 
#     # Get api keys from db - unencrypt
#     # decoded_token = decode_jwt(await token_listener(request))
#     log.debug(api_key)
    
#     if api_key not in api_keys:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Forbidden"
#         )


def generate_api_key(user_id=None):
    # SECRET_KEY = os.environ['SECRET_KEY']
    
    # payload = {
    #     'user_id': user_id,
    # }
    # api_key = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    api_key = "ak-" + ''.join(random.choices(string.ascii_letters + string.digits, k=64))
    return api_key




async def verify_api(api_key: str) -> bool:
    isTokenValid: bool = False
    # log.debug("Verifying API Key: " +  str(api_key))
    try:
        valid = await ApiKeys.find_one({
            "api_key" : api_key
        })
        # log.debug(valid)
        
        if valid:
            return True
            pass
            # owner = await Admin.get(PydanticObjectId(valid.user_id) )
            # if owner:
            #     # TODO Check if owner account is active.
            #     isTokenValid = True
        elif os.getenv("ADMIN_TOKEN",None) and api_key == os.getenv("ADMIN_TOKEN"):
            return True
    except Exception as e:
        log.error(e)
        pass
    return isTokenValid


class APIBearer(HTTPBearer):

    def __init__(self, auto_error: bool = True):
        super(APIBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(APIBearer, self).__call__(request)
        # print("Credentials :", credentials)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid API Key")

            if not await verify_api(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid API Key")

            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid API Key")

# Define the api key bearer
api_key_bearer = APIBearer()

async def get_owner(api_key: Annotated[str, Depends(api_key_bearer)]) -> Admin:
    valid = await ApiKeys.find_one({
        "api_key" : api_key
    })
    
    try:
        if valid:
            # log.debug(valid)
            owner = await Admin.get(PydanticObjectId(valid.user_id) ) # TODO Change to Project/Organisation, to keep data & user data contained within a project.
            project = await Project.get(PydanticObjectId(valid.project_id))
            # log.debug(owner)
            if owner and project:
                # TODO Do some validation checks to ensure this project is ACTIVE and has sufficient billing/subscription allowances.
                return str(valid.project_id)
            
    except Exception as e:
        log.error(e)
        
    return False

def get_token_from_header(header: dict):
    """
    Returns the token from the header.
    """
    bearer = header.get("authorization")
    if bearer and bearer.startswith("Bearer "):
        api_token = header.get("authorization").split(" ")[1]
        return api_token
    return None

def verify_permissions(permission: str = None):
    """
    Method to verify permissions of the request.
    """
    async def check_api_key_permission(api_key: ApiKeys, permission = None):
        # permission checking logic 
        # permission is passed with the module name included, eg. cms.read, or cms.write
        
        granted = False
        
        if api_key:
            
            if permission:
                try:
                    log.debug("Checking permission: " + str(type(permission)) + ": " + str(permission))
                    log.debug("API Key Permissions: " + str(api_key.permissions))
                    # print(api_key)
                    if isinstance(permission, Enum):
                        # print(permission.value, api_key.permissions)
                        granted = permission.value in api_key.permissions
                    if isinstance(permission, str):
                        granted = permission in api_key.permissions
                    if isinstance(permission, list):
                        granted = all([await check_api_key_permission(api_key,item) for item in permission])
                    # log.debug("Permission Granted: " + str(granted))
                except Exception as e:
                    log.error(e)
            else:
                granted = True
                
        # log.debug("Permission Granted: " + str(granted))
        return granted

    async def _verify_permissions(api_key: str = Depends(api_key_bearer)):
        # Replace this with your actual permission checking logic
        log.debug("Verifying Permissions: " + str(api_key)[:10] + "... - " + str(permission))
        _api = await ApiKeys.find_one({
                "api_key" : api_key
            })
        # print(_api)
        if _api:
            # log.debug("Verify API key = PASS")
            has_permission = await check_api_key_permission(_api, permission)
            if not has_permission:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return True
        elif os.getenv("ADMIN_TOKEN",None) and api_key == os.getenv("ADMIN_TOKEN"):
            log.debug("Access via ADMIN_TOKEN")
            return True
        
        return False
    
    return _verify_permissions
