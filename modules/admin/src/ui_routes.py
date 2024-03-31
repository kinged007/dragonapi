## Hidden routes, used for administrator only UI

from fastapi import APIRouter, Query, Request, Depends, Body
from fastapi.responses import JSONResponse
from loguru import logger as log
from importlib import import_module
from bson import ObjectId
from importlib import import_module, util
from beanie import Document
from os import path
import inspect

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

from vars import DEBUG
from models.utils import get_module_folders_generator
from models.permissions import list_permissions
from auth.api_key import generate_api_key, verify_permissions

# Load router and define permissions at module level if required.
# Only show in schema is working in DEBUG mode
router = APIRouter( include_in_schema=DEBUG )
module = Module()

# Load module endpoints, and dependencies if required.
# @router.get('/test', dependencies=[Depends(verify_permissions(Module.permission(PermissionsOptions.read)))])
@router.get('/token/verify')
async def login_using_access_token(
    access_token: str = Query(..., description="Access token to be used for login.")):

    if access_token:
        if module.verify_access_token(access_token):
            return JSONResponse(status_code=200, content={"message": "Login successful."})

    return JSONResponse(status_code=401, content={"message": "Login failed."})

@router.get('/modules', dependencies=[Depends(access_token_bearer)])
async def get_modules(name: str = Query(None, description="Module name to filter") ):

    res = await ModuleConfig.find({}).to_list()

    output = []

    if res:

        _names = [r.module for r in res]

        # Apply filter if name is provided
        if name:
            _names = [name] if name in _names else []

        for module_folder, module_name in get_module_folders_generator():

            try:
                if module_name in _names:

                    # Get list item where module name is equal to the current module name. Each item is a dict, so need to check for item['module'] == module_name
                    _db_module = [r for r in res if r.module == module_name]
                    if _db_module:
                        _db_config = _db_module[0].config

                    # ignore keys that are helpers, such as _help, _field, _options
                    _db_config = {
                        k: v for k, v in _db_config.items() if not any(
                            k.endswith(h) for h in ['_help', '_field', '_options']
                        )
                    }
                    # from rich import print
                    # print(type(_db_config),_db_config)

                    # Get Modules config and merge with database values
                    module_config = import_module(f"modules.{module_name}.config")
                    config = module_config.Config(**_db_config)
                    #TODO enable the use of pydantic basemodels for config types. 
                    # Currently, this function cannot process pydantic models from dicts from the DB.

                    # print(type(config),config)

                    _dict = {
                        **_db_module[0].model_dump(),
                        "config": config.model_dump()
                    }

                    # print(_dict)
                    output.append(  _dict )

            except Exception as e:
                log.error(f"Error processing module folder {module_folder}: {e}")

    return {"data": output}

# TODO Change these endpoints that refer to single item, to use singlular names. eg. /module/{id} instead of /modules/{id}
@router.patch('/modules/{id}', dependencies=[Depends(access_token_bearer)])
async def update_module_config(id: str, data: dict = Body(..., example={"key": "value"})):
    """
    Updates the module's configuration.
    """
    if id and data:

        res = await ModuleConfig.find_one({"_id": ObjectId(id) })

        if not res:
            return JSONResponse(status_code=404, content={"message": "Module not found."})

        if res:

            for key, value in data.items():
                if key in res.config:
                    if any(key.endswith(x) for x in ['_help', '_field', '_options','_type','_disabled']):
                        continue
                    if any(x in key for x in ['id','_id','_next_execution','_last_date']):
                        continue
                    res.config[key] = value

            # print(res)

            if await res.save():
                # TODO Clear cache for get_modules
                return JSONResponse(status_code=200, content={"message": "Module updated."})

            else:

                return JSONResponse(status_code=500, content={"message": "Failed to update module."})

    return JSONResponse(status_code=400, content={"message": "Invalid request."})


@router.get('/cronjobs', dependencies=[Depends(access_token_bearer)])
async def get_cron_jobs():

    res = await CronExecutor.find({}).to_list()

    output = []

    if res:

        _names = [r.module for r in res]

        for module_folder, module_name in get_module_folders_generator():

            try:
                if module_name in _names:

                    # Get list item where module name is equal to the current module name. Each item is a dict, so need to check for item['module'] == module_name
                    _db_module = [r for r in res if r.module == module_name]

                    if not _db_module:
                        continue

                    # # Get Modules config and merge with database values
                    # module_config = import_module(f"modules.{module_name}.config")
                    # config = module_config.Config(**_db_config)

                    output.append( _db_module[0].model_dump() )

            except Exception as e:
                log.error(f"Error processing module folder {module_folder}: {e}")

    # print(output)
    return {"data": output}

@router.post('/cronjobs/{id}/run', dependencies=[Depends(access_token_bearer)])
async def run_specific_cronjob_now(id: str):

    res = await CronExecutor.find_one({'_id': ObjectId(id)})

    if not res:
        return JSONResponse(status_code=404, content={"message": "Cron job not found."})

    try:
        module = import_module(f"modules.{res.module}.main")

        module = module.Module()

        await module._check_and_execute_cron(force=True)

        return JSONResponse(status_code=200, content={"message": "Cron job executed."})

    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Failed to execute cron job: {e}"})


@router.get('/dashboard', dependencies=[Depends(verify_permissions(Module().permission(PermissionsOptions.environment_read)))])
async def get_dashboard_data():

    from vars import DEBUG, LOGGING_LEVEL, ENVIRONMENT

    data = {
        "totals": {
            "modules": await ModuleConfig.count(),
            "cronjobs": await CronExecutor.count(),
        },
        "config": {
            "debug": DEBUG,
            "logging_level": LOGGING_LEVEL,
            "environment": ENVIRONMENT,
        },
    }

    tables_list = []

    # Fetch database tables from Schema documents that extend the Document type and autoload them if the module is active.
    for module_folder, module in get_module_folders_generator():
        try:
            tables_file = path.join(module_folder, 'schema.py')
            if path.exists(path.join(module_folder, 'schema.py')):
                log.debug(f"Importing 'modules.{module}.schema'...")

                # Load the module
                spec = util.spec_from_file_location(f"{module_folder}.tables", tables_file)
                tables = util.module_from_spec(spec)
                spec.loader.exec_module(tables)

                # Import classes of type Document
                for name, obj in inspect.getmembers(tables):
                    if inspect.isclass(obj) and issubclass(obj, Document) and obj is not Document:
                        log.info(f"Imported {name} from modules.{module}.schema")
                        tables_list.append(obj)
                        data['totals'][f"{name.lower()}"] = await obj.count()

        except Exception as e:
            print(f"Error processing module folder {module_folder}: {e}")

    return {"data": data}

@router.get('/api-keys', dependencies=[Depends(access_token_bearer)])
async def get_api_keys():

    res = await ApiKeys.find({}).to_list()

    # print(res)

    output = []

    for r in res:
        output.append(r.model_dump())

    return {"data": output}

@router.post('/api-keys', dependencies=[Depends(access_token_bearer)])
async def create_api_key(data: dict = Body(..., example={"name": "My API Key", "permissions": ["module.read", "module.write"]})):

    if data:

        if 'name' in data and 'permissions' in data:

            data['api_key'] = generate_api_key()
            api_key = ApiKeys(**data)

            if await api_key.save():
                return JSONResponse(status_code=200, content={"message": "API Key created."})

            else:
                return JSONResponse(status_code=500, content={"message": "Failed to create API Key."})

    return JSONResponse(status_code=400, content={"message": "Invalid request."})

@router.patch('/api-keys/{id}', dependencies=[Depends(access_token_bearer)])
async def update_api_key(id:str, data: dict = Body(..., example={"name": "My API Key", "permissions": ["module.read", "module.write"]})):

    if data:

        # print(data)

        if 'name' in data and 'permissions' in data:

            api_key = await ApiKeys.find_one({'_id': ObjectId(id)})

            if not api_key:
                return JSONResponse(status_code=404, content={"message": "API Key not found."})

            # print(api_key)

            for key, value in data.items():
                if key in ['name', 'permissions']:
                    setattr(api_key, key, value)

            # print(api_key)

            if await api_key.save():

                return JSONResponse(status_code=200, content={"message": "Api Key updated."})

            else:

                return JSONResponse(status_code=500, content={"message": "Failed to update Api Key."})


    return JSONResponse(status_code=400, content={"message": "Invalid request."})

@router.delete('/api-keys/{id}', dependencies=[Depends(access_token_bearer)])
async def delete_api_key(id:str):

    if id:

        api_key = await ApiKeys.find_one({'_id': ObjectId(id)})

        if not api_key:
            return JSONResponse(status_code=404, content={"message": "API Key not found."})

        if await api_key.delete():

            return JSONResponse(status_code=200, content={"message": "Api Key deleted."})

        else:

            return JSONResponse(status_code=500, content={"message": "Failed to delete Api Key."})


    return JSONResponse(status_code=400, content={"message": "Invalid request."})


@router.get('/api-keys/permissions', dependencies=[Depends(access_token_bearer)])
async def get_api_key_permissions():

    return {"data": list_permissions() }

if DEBUG:
    @router.get('/test_cache', tags=["Debug"])
    async def test_cache(request: Request):

        from utils.cache import global_cache
        sp1 = global_cache.get("special_key")
        sp2 = global_cache.storage
        log.debug(sp1)
        log.debug(sp2)
        return JSONResponse(content={
            "special_key":sp1,
            "storage":str(sp2)
        })
