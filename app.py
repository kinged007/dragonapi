from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, Depends, Request, BackgroundTasks #, Body, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from time import time, sleep
from loguru import logger as log
import traceback
import os, asyncio
from importlib import import_module, util
from beanie import Document
import inspect
from dotenv import load_dotenv
import sys

from rich import print

# Load environment variables from .env file
load_dotenv(override=True)

# from auth.api_key import api_key_bearer, get_owner, generate_api_key
# from routes.admin import router as AdminRouter
# from routes.project import router as ProjectRouter
from auth.api_key import get_token_from_header
# from tables.admin import Admin
from tables.cron import CronExecutor
from tables.config import ModuleConfig
from tables.api_keys import ApiKeys
# from tables.project import Project
from models.utils import get_module_folders_generator, to_snake_case
from utils.cache import global_cache
from vars import BASE_DIR, DEBUG, LOGGING_LEVEL, ENVIRONMENT, APP_VERSION, BETTER_STACK_TOKEN, SENTRY_DSN


_start = time()

lifespan_variables = {}
db_initialised = False

log.info(f"Starting DragonAPI in {ENVIRONMENT.upper()} environment, with DEBUG = {DEBUG}")

# Set output logging level based on LOGGING_LEVEL environment variable
log.info(f"Setting log level to {LOGGING_LEVEL}")
log.remove()
log.add("logs/default.log", level=LOGGING_LEVEL, rotation="5 MB", compression="zip", retention="30 days")
log.add("logs/errors.log", level="WARNING", rotation="5 MB", compression="zip", retention="30 days", backtrace=True, diagnose=True)
log.add("logs/errors.log", level="ERROR", rotation="5 MB", compression="zip", retention="30 days", backtrace=True, diagnose=True)
if DEBUG:
    log.add("logs/debug.log", level="DEBUG", rotation="5 MB", compression="zip", retention="7 days")
log.add(sys.stdout, level=LOGGING_LEVEL)

# Better Stack logging
if BETTER_STACK_TOKEN:
    from logtail import LogtailHandler
    handler = LogtailHandler(source_token=BETTER_STACK_TOKEN)
    log.add(handler, level=os.getenv("BETTER_STACK_LOGLEVEL", "ERROR").upper()) 

# Sentry logging
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.starlette import StarletteIntegration
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.pymongo import PyMongoIntegration
    from sentry_sdk.integrations.loguru import LoguruIntegration
    from sentry_sdk.integrations.asyncio import AsyncioIntegration



    sentry_sdk.init(
        dsn=SENTRY_DSN,
        enable_tracing=True,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
        integrations=[
            StarletteIntegration(
                transaction_style="endpoint"
            ),
            FastApiIntegration(
                transaction_style="endpoint"
            ),
            PyMongoIntegration(),
            LoguruIntegration(),
            AsyncioIntegration(),


        ],
        release=f"{os.getenv('APP_TITLE', 'DragonAPI')}@{APP_VERSION}",
        environment=ENVIRONMENT,
    )

@asynccontextmanager
async def lifespan(application: FastAPI):
    # Load models and data that will be used throughout the lifespan of the app
    # eg.
    # lifespan_variables["test"] = name_of_function
    log.debug("Loading lifespan function")
    # Initialize MongoDB instances
    await start_database()
    # Initialize Module configurations and DB schemas
    await start_modules()
    
    log.info("Application started in {:.3f} seconds".format(time() - _start))

    yield
    # Clean up the models and data and release the resources
    log.debug("Lifespan shutdown")
    lifespan_variables.clear()


# @app.on_event("startup") # DEPRECATED https://fastapi.tiangolo.com/advanced/events/#async-context-manager

# executed on each new incoming request
async def start_database():
    global db_initialised
        
    if db_initialised:
        log.info("MongoDB Already Initialized")
        return db_initialised

    client = AsyncIOMotorClient(os.environ['DATABASE_URL'])
    # Specify the database
    database_name = 'production' if ENVIRONMENT.lower() in "production" else ENVIRONMENT.lower()[:3]+"_db"
    database = client[database_name]
    
    # database = client.get_default_database()
    log.info(f"Connecting to database: {database.name}")
    tables_list = [ApiKeys, CronExecutor, ModuleConfig]
    
    # Fetch database tables from Schema documents that extend the Document type and autoload them if the module is active.
    for module_folder, module in get_module_folders_generator():
        try:
            tables_file = os.path.join(module_folder, 'schema.py')
            if os.path.exists(os.path.join(module_folder, 'schema.py')):
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

        except Exception as e:
            print(f"Error processing module folder {module_folder}: {e}")
                
                
    await init_beanie(database=database, document_models=tables_list)
    
    for table in tables_list:
        collection = table.get_motor_collection()
        log.debug(f"Connected to DB collection: {collection.name}")
        
    log.info("MongoDB Initialized tables: " + str([t.__name__ for t in tables_list]))
    
    db_initialised = True
    
    return db_initialised

async def start_modules():
    """
    Loads modules configuration and database schemas.
    """
    
    loaded_modules = []
    active_modules = []
    
    for module_folder, module in get_module_folders_generator():
        try:
            # log.debug(module_folder)
            
            # Check if module has config, main and router files
            # Done already in get_module_folders_generator()
            # if all([os.path.exists(os.path.join( module_folder, p)) for p in ['config.py', 'main.py', 'router.py']]):
            
            log.debug(f"Importing 'modules.{module}'...")

            module = import_module(f'modules.{module}.main')
            module = module.Module()
            if not module:
                log.error(f"Module '{module}' failed to load")
                await asyncio.sleep(0.1)
                continue
            await module.refresh_config()
            await asyncio.sleep(0.1)
            loaded_modules.append(module)
            if module.config_get('module_active', False):
                active_modules.append(module)
            log.info(f"Module '{module.module_name}' loaded")
            # Execute the async init function of the module
            await module.init()
                
        except Exception as e:
            log.error(f"Failed to include config for module: {module}. Error: {e}")
            print(traceback.format_exc())
    
    await asyncio.sleep(0.1)
    
    global_cache.set('active_modules', [m.module_name for m in active_modules])
    
    get_module_routes()

def get_module_routes():

    active_modules = global_cache.get('active_modules')
    
    for module_folder, module_name in get_module_folders_generator():
        try:
                    
            module_router = import_module(f'modules.{module_name}.router').router
            
            app.include_router(module_router, prefix=f"/{module_name}", tags=[to_snake_case(module_name)])
            
            log.info(f"Imported 'modules.{module_name}.router'.")
            
        except Exception as e:
            
            log.error(f"Failed to include router for module: {module_name}. Error: {e}")
            print( traceback.format_exc() )
            
            
# Start FastAPI App
app = FastAPI( 
    # Get app title from envioronment variable
    title= os.getenv("APP_TITLE", "FastAPI"),
    
    description= os.getenv("APP_DESCRIPTION", "REST API Server"),
    summary= os.getenv("APP_SUMMARY", ""),
    version= APP_VERSION,
    terms_of_service= os.getenv("APP_TERMS_OF_SERVICE", ""),
    # contact={
    #     "name": "Deadpoolio the Amazing",
    #     "url": "http://x-force.example.com/contact/",
    #     "email": "dp@x-force.example.com",
    # },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    lifespan=lifespan
)

os.makedirs(os.path.join(BASE_DIR, 'static'), exist_ok=True)

# TODO remove this? - Serve static files from modules defined static folders
# app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
    "http://localhost",
    "https://localhost",
    "https://app.bebookapp.com", # BeBook App PRODUCTION
    "https://admin.bebook.es", # BeBook App DEVELOPMENT
    "https://agcommunity.preview.eu10.apps.build.cloud.sap", # SAP Cloud Platform
    "https://agcommunity.design-time.eu10.apps.build.cloud.sap/", # SAP Cloud Platform
]

# TODO Add CORS configuration to config options in the database, for administrative control through the admin panel.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

log.info("App Startup Complete")

# TODO Add a rate limiter middleware
# TODO Add a cache middleware
# TODO Add a security middleware

# TODO Add middleware to track statistics
@app.middleware("http")
async def track_statistics(request: Request, call_next):
    # Do something before the endpoint handler is called
    # log.debug(request.scope)
    _start = time()
    # Get the name of the endpoint
    endpoint_path = request.url.path
    endpoint_params = request.query_params    
    
    # TODO Determine module being used.
    # print(app)
    # TODO Check if config manager should refresh the config for the module. - Currently being done in common/ping - run_cron
    # TODO if module is not active, return a module not active json response

    # log.debug(request.headers)
    # log.debug(request.url)
    # log.debug(call_next)
    
    api_token = get_token_from_header(request.headers)
    project_id = None
    # if api_token:
        # project_id = await get_owner(api_token)
    
    response = await call_next(request)
    
    # Do something after the endpoint handler is called
    # print("TODO Done tracking statistics.")
    # If project_id is none, ignore tracking?
    # Do something with the endpoint information
    print(f"Endpoint: {endpoint_path}, Params: {endpoint_params or 'None'}, Time elapsed: {time() - _start:.5f} seconds.")
    print(f"Executed by Project #{project_id if project_id else 'Unknown'}, Bearer Token: ...{api_token[-14:] if api_token else 'Unknown'}")

    
    return response


# Main page
@app.get("/", include_in_schema=False, response_class=HTMLResponse)
async def home():
    _text = "<html><body><div style='margin-left:auto;margin-right:auto;max-width:400px;text-align:center; margin-top:20vh;'>"
    _text += "<h1 style='font-family: monospace;'> ヽ(•‿•)ノ </h1>"
    _text += f"<h1>{os.getenv('APP_TITLE', 'DragonAPI')}</h1>"
    _text += "<p>"+os.getenv('APP_DESCRIPTION', 'REST API Server')+"</p>"
    _text += f"<p><a href='/admin/panel'>Admin</a> | <a href='/docs'>Swagger Docs</a> | <a href='/redoc'>ReDoc Docs</a>"
    if BETTER_STACK_TOKEN:
        _text += " | <a href='https://logs.betterstack.com/team/0/tail' target='_blank'>Better Stack</a>"
    if SENTRY_DSN:
        _text += " | <a href='https://sentry.io/organizations/' target='_blank'>Sentry</a>"
    _text += f"</p><p>Version: {APP_VERSION}</body></html>"  # Redirect to docs
    return _text
    # return {"message": "Welcome to MyAPI Server for developers. Visit /docs for API documentation."}


# Get Module Routes from the Router Manager
# get_module_routes(app)





if DEBUG:
    
    if SENTRY_DSN:
        # Test Logging
        @app.get("/test-error", tags=["Debug"])
        async def trigger_sentry_error():
            division_by_zero = 1 / 0
    if BETTER_STACK_TOKEN:
        # Test Logging
        @app.get("/test-betterstack", tags=["Debug"])
        async def trigger_betterstack_error():
            log.error("This is a test error message")
            return {"status": "ok"}