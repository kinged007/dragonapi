# This file houses the main class for the module. It is responsible for handling the module's data and business logic and shared resources
# Acts as a Controller
from loguru import logger as log
from src.basemodule import BaseModuleClass
import requests
from vars import APP_VERSION, DEBUG

# Get global cache
from utils.cache import global_cache


# Import the module's schema

# Import the module's config

# Import the module's database model


class Module(BaseModuleClass):
    """
    CMS module interacts with database (in this case, Directus API) to manage content and projects.
    Main workflows
    - setup - called on module load, checks if Directus API is available and tables are present. If not, creates them.
    - cron - checks for new projects/tasks and updates the database
    - 
    
    """
    # def __init__(self):
    #     super().__init__()
    #     log.warning("CHILD MODULE (module controller) - Module Loaded: "+self.__class__.__name__)
    
    # config is autoloaded from the database, using config.py as a base.
    # module config is callable from self.config_get(key,fallback) or self.config_set(key,value)
    # global config is callable from self.global_config(key,fallback)
    
    # Correct permission format is: "module_name.permission_name"
    # callable via self.permission("permission_name")
    # or externally, Module().permission("permission_name")
    

    
    def __init__(self, url: str = None, token:str = None):
        super().__init__()
        
        
    async def init(self):
        pass

    async def run_cron(self):
        """
        This method is called by the cron job at the interval defined in the module's config.
        """
        # Check for new projects/tasks and process
        # Check for new content and process
        
        pass
    