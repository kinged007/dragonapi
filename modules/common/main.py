# This file houses the main class for the module. It is responsible for handling the module's data and business logic and shared resources
# Acts as a Controller
from loguru import logger as log
from src.basemodule import BaseModuleClass

# Import the module's schema

# Import the module's config

# Import the module's database model

class Module(BaseModuleClass):
    
    # config is autoloaded from the database, using config.py as a base.
    # module config is callable from self.config_get(key,fallback) or self.config_set(key,value)
    # global config is callable from self.global_config(key,fallback)
    
    # Correct permission format is: "module_name.permission_name"
    # callable via self.permission("permission_name")
    
    pass

    def __init__(self):
        super().__init__()
        # log.warning("CHILD MODULE (module controller) - Module Loaded: "+self.__class__.__name__)