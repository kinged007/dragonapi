import os
from loguru import logger as log
from importlib import import_module
from models.utils import get_module_folders_generator

def list_permissions():
    
    permissions = []

    # for module_folder in module_folders:
    for module_folder, module_name in get_module_folders_generator():

        try:
            
            schema_path = os.path.join(module_folder, 'schema.py')
            
            if os.path.exists(schema_path) :
                
                log.debug(f"Importing 'modules.{module_name}.schema'...")

                # Import config file
                module_schema = import_module(f'modules.{module_name}.schema')
                
                try:
                    if hasattr(module_schema, 'PermissionsOptions'):
                        log.debug(f"PermissionsOptions for '{module_name}' found")    
                        _config = module_schema.PermissionsOptions
                        for permission in _config:
                            log.debug(f"{module_name}.{permission.value}")
                            permissions.append(f"{module_name}.{permission.value}")

                    else: 
                        # print("Config not found")
                        pass
                    
                except Exception as e:
                    log.error(e)
                
                
        except Exception as e:
            log.error(f"Failed to include config for module: {module_name}. Error: {e}")
            
    return permissions
