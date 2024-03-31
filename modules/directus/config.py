from schema.basemodule import BaseModuleConfig, ConfigField
# from .schema import PermissionsOptions

class Config(BaseModuleConfig):
        
    # module_active:bool = True
    # cron_interval:int = 5 # minutes
    # cron_active:bool = True
    # cron_schedule:str = "*/13 * * * *" # Default to every 15 minutes
    
    directus_url: str = ""
    directus_access_token: str = ""
    directus_public_files_folder_id: str = ""
    