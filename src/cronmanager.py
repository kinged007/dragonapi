## CronManager
## This class is used to manage cron jobs for a module.
## It is called from the cron scheduler and is responsible for running the cron job for the module.

from pydantic import BaseModel
from croniter import croniter
from utils.datetime import datetime, timezone, utc_now
from loguru import logger as log
# from rich import print


from src.configmanager import ConfigManager
from tables.cron import CronExecutor
from models.utils import log_time
from vars import log_level
from utils.datetime import utc_datetime, utc_now

class CronManager(BaseModel):
    
    cron_executor:object = None
    module_name:str = ""
    global_config: dict = {}
    config:dict = {}
    
    
    def __init__(self, module_name:str, cron_executor:object):
        super().__init__() 
        
        self.module_name = module_name
        self.cron_executor = cron_executor
        config_manager = ConfigManager()
        self.config = config_manager.get_config(module_name)
        self.global_config = config_manager.get_config("global")
        
    async def init(self):
        """
        Initialize the cron manager
        """
        _update = False
        
        # Check all variables are set
        if not self.cron_executor:
            return False
        
        # Merge module config with cron executor
        if self.config.get('cron_active', False) != self.cron_executor.active:
            self.cron_executor.active = self.config.get('cron_active', False)
            _update = True
        
        # Check if next_execution is not set.
        if not self.cron_executor.next_execution:
            self.cron_executor.next_execution = self.next_iter(self.config.get("cron_schedule", None))
            _update = True
        
        # Save the cron executor
        if _update:
            try:
                self.cron_executor.save()
            except Exception as e:
                raise Exception(f"Failed to save cron executor for '{self.module_name}'") from e
                log.error(f"Failed to save cron executor for '{self.module_name}'")
                return False
        
        # Return True if all checks pass
        return True

    def _log_format(self, message:str, type:str="info"):
        """
        Format log message
        """
        return f"{log_time()} [{type.upper()}] {message}"
        
    async def log(self, message:str, type:str="info"):
        
        # print(type, message, log_level(type) < log_level() )
        
        if log_level(type) < log_level():
            return
        
        self.cron_executor.log.append(self._log_format(message, type))
        
        if type.lower() == "error":
            log.opt(record=True, depth=1).error(f"{self.cron_executor.module}: {message}")
        elif type.lower() == "warning":
            log.opt(record=True, depth=1).warning(f"{self.cron_executor.module}: {message}")
        elif type.lower() == "debug":
            log.opt(record=True, depth=1).debug(f"{self.cron_executor.module}: {message}")
        else:   
            log.opt(record=True, depth=1).info(f"{self.cron_executor.module}: {message}")
        
        cron_logs_to_keep = self.global_config.get('cron_logs_to_keep', 100)
        
        # Cleanup log
        if len(self.cron_executor.log) > cron_logs_to_keep: 
            self.cron_executor.log = self.cron_executor.log[-cron_logs_to_keep:]
        
        self.cron_executor.save()

    def execute_now(self):
        """
        Check if the next iteration of the cron job is due.
        """
        
        if self.cron_executor.active and self.config.get("cron_active", False):
                        
            # Check if next_execution is passed.
            log.debug(f"{self.cron_executor.module}: Next cron execution: {self.cron_executor.next_execution} UTC")
            try:
                if utc_datetime(self.cron_executor.next_execution) <= utc_now():
                    return True
            except TypeError as e:
                log.warning(f"Error comparing datetime objects: {e}")
                # Run now and save next iteration
                return True
                # DEPRECATED method
                # if self.cron_executor.next_execution <= datetime.utcnow():
                #     return True
        
        return False
    
    @staticmethod
    def next_iter(schedule:str):
        """
        Returns the next execution time for the cron job.
        """
        # if self.cron_executor.active and self.config.get("cron_active", False):
            
        # Get the next iteration time
        # schedule = self.config.get("cron_schedule", None)
        if schedule:
            next_time = croniter(schedule, utc_now()).get_next(datetime)
            return next_time
        
        # return None # Throws an error. Return now instead
        return utc_now()
    
    async def execution_complete(self):
        """
        Method to be called after the cron job has been executed.
        """
        self.cron_executor.last_executed = utc_now()
        self.cron_executor.next_execution = self.next_iter(self.config.get("cron_schedule", None))
        # if log_level("info") >= log_level():
        #     self.cron_executor.log.append(self._log_format("Cron Job execution completed.", "info"))
        try:
            self.cron_executor.save()
        except Exception as e:
            raise Exception(f"Failed to save cron executor for '{self.module_name}'") from e
            log.error(f"Failed to save cron executor for '{self.module_name}'")
            return False
        
        return True