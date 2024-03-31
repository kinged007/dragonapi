"""
Baseclass for all models and modules to be inherited from.
Allows for easy access to the database and other shared resources, such as module config, global config, etc.

TODO Restructure module architecture to allow for easier access to shared resources.
Incorporate CRON operations into this class.
Incorporate logging into this class.
Incorporate config, permissions and structure into this class.
Incorporate API Key verification into this class.
Incorporate background task management into this class.
Incorporate database management into this class.
Incorporate shared resources into this class.


"""
from models.utils import log_time
from importlib import import_module
from loguru import logger as log
import asyncio
from time import time
import inspect
from os import path

class Baseclass():

    # Public variables
    module_name = ""

    # Private variables
    _global_config = {}
    _module_config = {}
    
    # This dictionary will store the created instances
    __instances = {}
    __initialised = 0

    def __new__(cls, *args, **kwargs):
        # Check if an instance already exists
        if cls not in cls.__instances:
            # Create a new instance and store it in the dictionary
            cls.__instances[cls] = super().__new__(cls)
            log.warning(f"BASECLASS: A new instance of {cls.__name__} has been created")

        return cls.__instances[cls]
    
    def __init__(self):
        # This code will be executed each time a new instance is created         
        if self.__initialised > time() - 15 :
            return
        
        log.warning(f"BASECLASS: The instance of ':{self.__class__.__name__}' is initializing.")
        
        # Initialize module config 
        self.__initialised = time()
                
        # Get the file that contains the child class
        child_class_file = inspect.getfile(self.__class__)
        
        # Get the filename and directory
        filename = path.basename(child_class_file)
        directory = path.dirname(child_class_file)
        self.module_name = path.basename(directory)
        # Get the directory of the current file
        # current_dir = path.dirname(os.path.abspath(__file__))

        # Import the config file
        module_config = import_module(f'modules.{self.module_name}.config')
        
        if hasattr(module_config, 'Config'):
            self.module_config = module_config.Config()
        
        
        print("CHILD CLASS", child_class_file, filename, directory)
        
        
    def __str__(self):
        return f"{self.__class__.__name__}"
    
    def config(self):
        return self._module_config
    
    def global_config(self):
        return self._global_config
    
    async def log(self, message:str, type="info"):
        if type == "error":
            log.error(f"{log_time()} {message}")
        elif type == "warning":
            log.warning(f"{log_time()} {message}")
        elif type == "debug":
            log.debug(f"{log_time()} {message}")
        else:
            log.info(f"{log_time()} {message}")
        
    