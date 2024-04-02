from enum import Enum
from typing import Any
from tables.config import ModuleConfig
import asyncio
from time import time, sleep
import os
import inspect

from loguru import logger as log

class BaseModulePermissions(Enum):
    pass
    
    
class BaseModuleConfig():
    
    ModuleName:str = ""
    Permissions:Any = None
    CronInterval:int = 5 # minutes
    CronActive:bool = False
    
    CronInterval_help:str = "Default Interval in minutes. May be overridden by Cron Job config."

    # This dictionary will store the created instances
    __instances = {}
    __initialised = 0
    # __config = {}

    def __new__(cls, *args, **kwargs):
        # Check if an instance already exists
        if cls not in cls.__instances:
            # Create a new instance and store it in the dictionary
            cls.__instances[cls] = super().__new__(cls)
            log.debug(f"A new instance of {cls.__name__} has been created")
        return cls.__instances[cls]
    
    def __init__(self):
        # This code will be executed each time a new instance is created 

        asyncio.ensure_future(self.init())
        
        
    async def init(self):
        
        if not self.ModuleName:
            
            # Get the file that contains the child class
            child_class_file = inspect.getfile(self.__class__)

            # Get the filename and directory
            # filename = os.path.basename(child_class_file)
            directory = os.path.dirname(child_class_file)
            
            self.ModuleName = os.path.basename(directory)

        if not self.ModuleName:
            log.warning("No module name provided")
            return False
        
        if self.__initialised > time() - 15 :
            return
        
        log.info(f"The instance of '{self.ModuleName}:{self.__class__.__name__}' is initializing.")
        
        # Initialize module config 
        self.__initialised = time()
    
        # Get class-level attributes
        class_attributes = {key: value for key, value in vars(self.__class__).items() if not key.startswith('_') and not callable(value)}

        # Get instance-level attributes
        instance_attributes = {key: value for key, value in vars(self).items() if not key.startswith('_') and not callable(value)}

        # Merge the two dictionaries
        _config = {**class_attributes, **instance_attributes}
        # print(" - - - - - ", _config.items())
        
        # Get database
        # TODO Use Directus db instead of MongoDB
        _dbconfig = await ModuleConfig.find_one({
            "module": self.ModuleName
        })
        
        # print("DB Config", _dbconfig)
        
        try:
            if not _dbconfig:
                _dbconfig = ModuleConfig(module=self.ModuleName, config=_config)
                await _dbconfig.create()
            else:
                # print(type(_dbconfig),_dbconfig)
                # Merge app config with db config
                _merged_config = {**_config, **_dbconfig.config}
                if _dbconfig.config != _merged_config:
                    _dbconfig.config = _merged_config
                    log.info("Saving updated config")
                    await _dbconfig.save()
                
                # Overwrite the attributes in the child class
                for key, value in _dbconfig.config.items():
                    setattr(self, key, value)
        except Exception as e:
            log.error(e)
            pass
        # self.__config = _dbconfig.config
            
    def get(self, attr_name, default = None):
        return getattr(self, attr_name, default)

    async def set(self, attr_name, value):
        
        # Try to update config
        _dbconfig = await ModuleConfig.find_one({
            "module": self.ModuleName
        })
        # Update config parameter with new value
        _dbconfig.config[attr_name] = value
        
        log.debug("Updating config for '"+self.ModuleName+"'."+attr_name)
        
        # Save config
        if await _dbconfig.save():
            # Update instance attribute
            setattr(self, attr_name, value)
            return True
        
        return False
    
    @classmethod
    def permission(cls, permission: str = None):
        """
        Method to verify permissions of the request. Method is likely to be called before initializing the class, but we need to identify the dirname of the child class to get the module name.
        """
        file_path = inspect.getfile(cls)
        directory = os.path.basename(os.path.dirname(file_path))
        if not directory:
            log.error("Could not identify module name")
            return False
        log.debug(f"Permission request: '{directory}.{permission}'")
        return f"{directory}.{permission}"