from models.utils import log_time
from os import getenv
from importlib import import_module
from loguru import logger as log
import asyncio
from utils.datetime import datetime, timedelta
from numbers import Number

from tables.cron import CronExecutor
from utils.datetime import utc_now

class BaseCronManager():
    
    CronExecutor = None
    Config = {}
    LogsToKeep = 50
    
    def __init__(self, CronExecutor = None, Config:dict = None ):
        self.CronExecutor = CronExecutor
        self.Config = Config
        self.LogsToKeep = int(getenv("CRON_LOGS_TO_KEEP", 50))
    
    async def log(self, message:str):
        
        self.CronExecutor.log.append(f"{log_time()} {message}")
        
        log.info(f"{self.CronExecutor.module}: {message}")
        
        if len(self.CronExecutor.log) > self.LogsToKeep: 
            # Cleanup log
            self.CronExecutor.log = self.CronExecutor.log[-self.LogsToKeep:]
        
        await self.CronExecutor.save()
    
    async def check_and_execute_cron(self):
        pass
        
    async def run_child_method(self):
        try:
            await self.log("Cron Job started.")
            await self.run()
            await self.log("Cron Job completed.")
        except Exception as e:
            # log.error(f"Cron Execution raised an error: {self.Config.ModuleName}. Error: {e}")
            await self.log(f"ERROR: Cron Execution raised an error: {e}")
            print(f"ERROR: Cron Execution raised an error: {e}")
            
async def check_and_execute_cron(module_name): # TODO Move this function into class.
    
    log.debug(">>>>>>>> check_and_execute_cron " +str(module_name))
    
    # Get cron executor for module:
    cron = await CronExecutor.find_one({
        "module": module_name
    })
    
    
    
    # Import config file
    module_config = import_module(f'modules.{module_name}.config')
    
    _interval = 5
    _active = False
    
    try:
        if hasattr(module_config, 'Config'):
            # print("Config found")
            _config = module_config.Config()
            _interval = _config.get("CronInterval")
            _active = _config.get("CronActive") or False
            if not _config.get("ModuleName"):
                await _config.set("ModuleName", module_name)
                
        else: 
            # print("Config not found")
            pass
        
        # print(_config.__dict__)
        # print(type(module_config.Config().Permissions), module_config.Config().Permissions.__members__.keys())
        # print(module_config.Config().CronInterval)
        # print(module_config.Config().CronActive)
        
    except Exception as e:
        log.error(e)
    
    # Only run cron jobs that are active in module config 
    if not _active: return
    log.debug(">>>>>>>> check_and_execute_cron " +str(module_name))

    # Create cron job if it does not exist
    if not cron:
        cron = CronExecutor(module=module_name, last_executed=utc_now(), interval=_interval)
        await cron.insert()
        log.info(f"Creating new Cron Job for module: {module_name}")
        
    else:
        
        # FIX: Convert non-datetime format from float timestamp to datetime
        if isinstance(cron.last_executed, Number):
            cron.last_executed = datetime.utcfromtimestamp(cron.last_executed)
        
        # Only run cron jobs that are active in module config AND in database
        if cron.status != "active": return
        
        # Check if cron job needs to be executed
        # if utc_now() - cron.last_executed < cron.interval * 60:
        if utc_now() - cron.last_executed < timedelta(minutes=cron.interval):
            # Cron job has been executed recently, skip
            # return # TODO DEBUG - add this back for production
            pass
        
        # Execute Cron Job
        log.info(f"Executing Cron Job for module: {module_name}")
        
        # Update last_executed in UTC time
        cron.last_executed = utc_now()
        
        # Cleanup and update if required. 
        cron.interval = _interval # updates interval incase changed in module config
            
        # await cron.save()
    
    # Save CronExecutor
    await cron.save()
    
    try:
        import traceback
        # Import cron file
        module_cron = import_module(f'modules.{module_name}.cron')
    except Exception as e:
        log.error(e)
        traceback.print_exc() # for detailed error message and traceback
        return
    
    log.debug(f"Included Module: {module_name}")

    # Run Cron job in background
    if hasattr(module_cron, 'CronManager'):
        # print("CronManager found")
        # Run CronManager in background
        task = asyncio.create_task(module_cron.CronManager(cron, _config).run_child_method())
        # await module_cron.CronManager().run(cron)
    else: 
        # print("CronManager not found")
        pass
    