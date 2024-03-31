from loguru import logger as log
from enum import Enum
# import asyncio
# from time import sleep
from asyncio import sleep
# # from rich import print
from time import time
from importlib import import_module

from tables.config import ModuleConfig
from schema.singleton import SingletonMeta
from utils.ui import remove_ui_params

class ConfigManager(metaclass=SingletonMeta):
    
    _config:dict = {}
    _last_refresh:dict = {}
    _time_to_refresh:int = 3 # seconds

    def get_config(self, module_name:str):
        
        if module_name.lower() == "global": module_name = "common"
        
        if module_name in self._config:
            return self._config[module_name]
            
        return {}
    
    async def refresh_config(self, module_name:str):
        
        if not self._config or module_name not in self._config or self._needs_refresh(module_name):
            
            log.debug("Time to refresh config for '"+module_name+"'.")

            if not self._config:
                self._config = {}
            
            if module_name not in self._config:
                
                self._config[module_name] = {}
                
            await self._fetch_config_from_db(module_name)
            await sleep(0.1)
            
            self._last_refresh[module_name] = time()
        
        return self.get_config(module_name)
  
    
    async def _fetch_config_from_db(self, module_name:str):
        # implement database fetch here
        log.info(f"Loading '{module_name}' config.")
        
        # Get module config from database
        _dbconfig = await ModuleConfig.find_one({
            "module": module_name
        })

        # Fetch module config file
        _import = import_module(f'modules.{module_name}.config')
        module_config = _import.Config()
        
        try:
            
            if not _dbconfig:
                _dbconfig = ModuleConfig(module=module_name, config=remove_ui_params(module_config.model_dump()))
                log.debug(f"No config found for {module_name}. Creating new config.")
                if not await _dbconfig.create():
                    raise Exception(f"Failed to create config for '{module_name}'")
                
            # print(type(_dbconfig),_dbconfig)
            # Merge app config with db config
            # TODO TEST apply filters for suffixes which should not be saved in the database. eg. _help, _options, ...
            _merged_config = {**module_config.model_dump(), **_dbconfig.config}
            if remove_ui_params(_dbconfig.config) != remove_ui_params(_merged_config):
                _dbconfig.config = remove_ui_params(_merged_config)
                log.debug(f"'{module_name}' Module Config Updated.")
                await _dbconfig.save()
            self._config[module_name] = _dbconfig.config
            await sleep(0.1)
                
        except Exception as e:
            log.error(e)
            
        return

    def _needs_refresh(self, module_name:str):
        
        if not self._last_refresh or module_name not in self._last_refresh:
            return True
        
        if (time() - self._last_refresh[module_name]) > self._time_to_refresh:
            return True
        
        return False
    
    async def update_config_value(self, module_name:str, key:str, value):
        
        if module_name.lower() in ['common','global']:
            raise Exception("Cannot edit common configuration.") # NOTE May need to change this to allow it.
        
        # Try to update config
        _dbconfig = await ModuleConfig.find_one({
            "module": module_name
        })
        
        # Update config parameter with new value
        _dbconfig.config[key] = value
        
        log.debug("Updating config for '"+module_name+"'."+key)
        
        # Save config
        if await _dbconfig.save():
            # Update instance attribute
            self._config[module_name][key] = value
            return True
        
        return False

    def get(self, module_name:str, var:str, fallback=None):
        """
        Get the value of a variable from the module's config dict
        """
        _c = self.get_config(module_name)
        if var in _c:
            return _c.get(var, fallback)
        
        return fallback
