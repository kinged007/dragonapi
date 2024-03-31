# This file houses the main class for the module. It is responsible for handling the module's data and business logic and shared resources
# Acts as a Controller
from loguru import logger as log
import os
from fastapi import HTTPException, Request
from starlette.status import HTTP_403_FORBIDDEN




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
    
    async def run_cron(self):
        """
        This method is called by the cron job at the interval defined in the module's config.
        """
        log.debug("Main cron job for module started.")
        
        # Save specific log entries. Not starting or stopping the cron job.
        await self.cron.log("Some other info.", type="info")




    
    def verify_access_token(self, access_token: str):
        """
        This method is used to verify the admin access token. Obtains admin token from environment variable.
        """
        log.debug("Verifying access token.")
        
        admin_token = os.getenv("ADMIN_TOKEN") # TODO - Change this to a database call, global config, or other secure method.
        
        if access_token == admin_token:
            return True
        
        return False
    