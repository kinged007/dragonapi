# Base module for all the modules. All modules should inherit from this class
# This class will contain shared resources and module specific data for quick reference

# TODO Create a logging function that creates logs relative to the module, so the admin ui can display module specific logs


from pydantic import BaseModel
from typing import Dict, Type, TypeVar
from models.utils import log_time
from importlib import import_module
from loguru import logger as log
import asyncio
from time import time
import inspect
from os import path, makedirs
import traceback
# from rich import print
from enum import Enum

from tables.cron import CronExecutor
from src.configmanager import ConfigManager
from src.cronmanager import CronManager
from vars import BASE_DIR

config_manager = ConfigManager()

class BaseModuleClass(BaseModel):
    
    # Public variables
    module_name:str = ""
    cron:CronManager = None

    # Private variables
    temp_module_config:dict = {}
    temp_global_config:dict = {}
    
    
    @classmethod
    def permission(cls, permission: str = None):
        """
        Method to verify permissions of the request. Method is likely to be called before initializing the class, but we need to identify the dirname of the child class to get the module name.
        # Allow for permission input to be string, enum
        """
        
        file_path = inspect.getfile(cls)
        directory = path.basename(path.dirname(file_path))
        if not directory:
            log.error("Could not identify module name")
            return False
        if isinstance(permission, list): # TODO Test this list of permissions str/enums.
            return [cls.permission(p) for p in permission]
            raise Exception("Permission checking for multiple permissions not allowed. Only string or Enum values.")
        if isinstance(permission, Enum):
            permission = permission.value
        if not isinstance(permission, str):
            raise Exception("Invalid permission type. Only string or Enum values allowed.")
        
        return f"{directory}.{permission}"
    
    
    def __init__(self):
        super().__init__()

        
        # Get the file that contains the child class
        child_class_file = inspect.getfile(self.__class__)
        
        # Get the filename and directory
        filename = path.basename(child_class_file)
        directory = path.dirname(child_class_file)
        self.module_name = path.basename(directory)
        # Get the directory of the current file
        # current_dir = path.dirname(os.path.abspath(__file__))

        # Import the config file
        # module_config = import_module(f'modules.{self.module_name}.config')
        # DEBUG TODO remove these in favor of config_get() method which communicates with config manager directly - single source of truth.
        self.temp_module_config = config_manager.get_config(self.module_name)
        self.temp_global_config = config_manager.get_config('common')
        
        # Load CronManager to cron variable
        # self.cron = CronManager(self.module_name)
        # print("CHILD CLASS", child_class_file, self.module_name, filename, directory)
        # print(self.module_name)
        log.debug(f"The instance of '{self.module_name}:{self.__class__.__name__}' is initializing.")
        
    async def init(self):
        """
        Placeholder for child init method
        """
        pass
        
    async def load_defaults(self):
        """
        Placeholder for child load_defaults method
        """
        pass
    
    async def refresh_config(self):
        """
        Update the module config and compare to config saved in database
        """
        return await config_manager.refresh_config(self.module_name)
    
    def config_get(self, var:str = None, fallback=None):
        """
        Get the value of a variable from the module's config
        """
        _c = config_manager.get_config(self.module_name)
        if var and var in _c:
            return _c.get(var, fallback)
        elif not var:
            return _c
        return fallback

    async def config_set(self, key:str, value):
        """
        Set the value of a variable in the module's config
        """
        if await config_manager.update_config_value(self.module_name, key, value):
            # self.module_config[key] = value
            return True
        
        return False
        
    def global_config(self, var:str, fallback=None):
        """
        Get the value of a variable from the global config
        """
        _c = config_manager.get_config('common')
        if var in _c:
            return _c.get(var, fallback)
        
        return fallback

    async def run_cron(self):
        """
        Placeholder for child cron method
        """
        pass
    
    async def _check_and_execute_cron(self, force=False):
        """
        Method to check and execute the cron job for the module
        """
        
        # Refresh module config from database
        config = await self.refresh_config()
        
        # check if module is active
        if not force and not self.config_get('module_active', False):
            log.debug(f"Module '{self.module_name}' is not active")
            return False
        
        # Get cron executor for module:
        # cron = await CronExecutor.find_one({
        #     "module": self.module_name
        # })
        cron = CronExecutor.objects(module=self.module_name).first()
        
        # If CronExecutor is not found, create it
        try:
            if not cron:
                log.debug(f"CronExecutor not found for '{self.module_name}'. Creating new one.")
                cron = CronExecutor(module=self.module_name)
                try:
                    cron.save()
                except Exception as e:
                    raise Exception(f"Failed to create cron executor for '{self.module_name}'")

        except Exception as e:
            log.error(e)
            return False
        
        if self.config_get('cron_active', None) != None:
            cron.active = self.config_get('cron_active', False)
            
        # If cron is not active, return
        if not force and not cron.active:
            log.debug(f"Cron job is not active for '{self.module_name}'")
            return False
        
        # Set up CronManager
        self.cron = CronManager(self.module_name, cron)
        
        # Initialize the cron manager
        try:
            if not await self.cron.init():
                log.error(f"Failed to initialize cron executor for '{self.module_name}'")
                return False
            
            # Check if it is time for the module to execute the cron job
            if force or self.cron.execute_now():
                log.info(f"Executing cron job: {self.module_name}")
                # Execute the cron job
                await self.run_cron()
                # Mark the cron job as complete. Automatically updates next_execution and saves log.
                await self.cron.execution_complete()
                
                
        except Exception as e:
            log.error(e)
            await self.cron.log(f"Error executing cron job: {e}", type="error")
            print(traceback.format_exc())
            await self.cron.execution_complete()
            return False
            
        # Finally, empty the cron executor
        self.cron = None
    
    def data_folder(self, folder:str = ""):
        """
        Get the path of a folder in the module's data directory
        """
        if not self.module_name: return None
        
        if folder == None: folder = ""
        _path = path.join(BASE_DIR, 'data', self.module_name, folder)
        makedirs(_path, exist_ok=True)
        return _path

    ########################################
    # Default pydantic methods override
    ########################################
    
    def model_dump(self):
        """
        Overrides the default model_dump() and Returns a dictionary skipping all the help and field attributes.
        """
        def recursive_walk(data):
            new_data = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    new_data[key] = recursive_walk(value)
                else:
                    if not any(x in key for x in ['_help', '_field', '_options', '_disabled']):
                        new_data[key] = value
            return new_data
        return recursive_walk(super().model_dump())
        
