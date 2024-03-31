# Public routes for Pollygene module
# Path: modules/pollygene/routes/public.py
# This file houses the public routes for the module. It is responsible for handling the module's public endpoints and shared resources
# Primary database interaction will be with Directus which is the Pollygene Admin UI.


from fastapi import APIRouter, Query, Request, Depends, Body
from fastapi.responses import JSONResponse
from loguru import logger as log
from utils.datetime import datetime, timedelta

# Cache
from utils.cache import global_cache

from vars import DEBUG

# Import module main class
from .. import Module
from ..schema import PermissionsOptions

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
# Auth, User, Wallet, Tests, Certificate, Lab, Language/Translations, Notifications, Settings, Marketplace, Species

# Common, unauthorized endpoints
# GET /species/{search query}
@router.get('/species')
@global_cache.async_cache(ttl=300, namespace="pollygene")
async def species(search: str = Query(None)):
    """
    Get a list of species from the database.
    """
    try:
        if not search: search = ""
                
        log.debug("Getting species list.")
        filtered_results = []
        data = module.get_species()
        if not data:
            log.warning("No species found.")
        if search:
            for item in data:
                if search.lower() in item['name'].lower() \
                    or search.lower() in item['scientific_name'].lower() \
                        or search.lower() in item['common_name'].lower() :
                    filtered_results.append(item)
        else :
            filtered_results = data
        
        return JSONResponse(content=filtered_results)
    except Exception as e:
        log.error(f"Failed to get species list: {e}")
        return JSONResponse(status_code=422, content={"message":"Failed to get species list."})
    
@router.get('/test_types')
@global_cache.async_cache(ttl=300, namespace="pollygene")
async def test_types():
    """
    Get a list of species from the database.
    """
    try:

        log.debug("Getting list.")

        data = module.get_test_types()
        if not data:
            log.warning("No data found.")
                    
        return JSONResponse(content=data)
    except Exception as e:
        log.error(f"Failed to get test type list: {e}")
        return JSONResponse(status_code=422, content={"message":"Failed to get test type list."})

# Auth
# Auth exchanges a JWT with Wordpress, where is the primary database of users. 
# Users are then copied to Directus, where it will be referenced in M2M relationships with Tests and other data.
# The users in Directus will have a field that stores the users Wordpress user ID.
# POST /auth/login - Login with Wordpress credentials. Returns JWT.
# POST /auth/logout - Logout and invalidate JWT.
# POST /auth/refresh - Refresh JWT.
# POST /auth/verify - Verify JWT.

@router.post('/auth/jwt/verify/{token}')
async def verify_auth(request: Request, token: str = None):
    """
    Verify JWT.
    """
    try:
        await module.init()
        verify = module.jwt.verify(token)
        return JSONResponse(content=verify)
    except Exception as e:
        log.error(f"Failed to verify token: {e}")
        return JSONResponse(status_code=422, content={"message":"Failed to verify token."})

# Refresh token
@router.post('/auth/jwt/refresh')
async def refresh_auth(request: Request, token: str = None):
    """
    Refresh JWT.
    """
    try:
        await module.init()
        data = module.jwt.verify(token)
        token = module.jwt.create(data, expires_delta=timedelta(minutes=1))
        return JSONResponse(content={"token":token})
    except Exception as e:
        log.error(f"Failed to refresh token: {e}")
        return JSONResponse(status_code=422, content={"message":"Failed to refresh token."})

# Login
@router.post('/auth/login')
async def login_auth(request: Request, body: dict = Body(..., example={"username":"myusername","password":"example"})):
    """
    Login with Wordpress credentials. Returns JWT.
    """
    try:
        body['username']
        body['password']
        await module.init()
        login_data = module.login(body.get('username'), body.get('password'))
        # token = module.jwt.create(body, expires_delta=timedelta(minutes=1))
        return JSONResponse(content=login_data)
    except Exception as e:
        log.error(f"Failed to login: {e}")
        return JSONResponse(status_code=403 , content={"message": "Failed to login"})

if DEBUG:
    @router.post('/auth/jwt/create', tags=["Debug"])
    async def create_auth(request: Request, body: dict = Body(..., example={"user_id":14, "email":"example@exa.com"})):
        """
        Create JWT.
        """
        try:
            await module.init()
            token = module.jwt.create(body, expires_delta=timedelta(minutes=1))
            return JSONResponse(content={"token":token})
        except Exception as e:
            log.error(f"Failed to create token: {e}")
            return JSONResponse(status_code=403 , content={"message":"Failed to create token."})
    
    
# **User Endpoints:**
#    - `GET /user/profile`: Parameters: `user_id`
#    - `PUT /user/profile`: Parameters: `user_id`, `email`, `first_name`, `last_name`, `preferred_language`
#    - `GET /user/wallet`: Parameters: `user_id`
#    - `POST /user/wallet/credits/add`: Parameters: `user_id`, `amount`
#    - `POST /user/wallet/credits/redeem`: Parameters: `user_id`, `coupon_code`

# **Certificate Endpoints:**
#    - `GET /certificate/{test_id}`: Parameters: `test_id`, `format`
#    - `GET /certificate/{test_id}/qr`: Parameters: `test_id`

# **User Endpoints:**
#    - `GET /user/profile`: Parameters: `user_id`
#    - `PUT /user/profile`: Parameters: `user_id`, `email`, `first_name`, `last_name`, `preferred_language`
#    - `GET /user/wallet`: Parameters: `user_id`
#    - `POST /user/wallet/credits/add`: Parameters: `user_id`, `amount`
#    - `POST /user/wallet/credits/redeem`: Parameters: `user_id`, `coupon_code`

# 3. **Test Activation and Management Endpoints:**
#    - `POST /tests/activate`: Parameters: `user_id`, `test_type_id`, `lab_id`
#    - `GET /tests`: Parameters: `user_id`
#    - `GET /tests/closest-lab`: Parameters: `user_id`, `test_type_id`, `user_location`
#    - `GET /tests/{test_id}/status`: Parameters: `test_id`
#    - `POST /tests/{test_id}/certificate`: Parameters: `test_id`, `format`

# **Marketplace Integration Endpoints:**
#    - `POST /marketplace/verify-purchase`: Parameters: `order_number`, `username`, `marketplace_id`
#    - `POST /marketplace/webhook`: Parameters: `webhook_data`

# 8. **Geolocation Endpoints:**
#    - `GET /geolocation/labs`: Parameters: `user_location`, `test_type_id`

# 9. **Notification Endpoints:**
#    - `POST /notifications/send`: Parameters: `user_id`, `notification_type`, `additional_data`

# 10. **Miscellaneous Endpoints:**
#     - `GET /languages`: No parameters required.
#     - `GET /settings`: No parameters required.