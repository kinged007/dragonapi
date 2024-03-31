from schema.basemodule import BaseModuleConfig, ConfigField
# from .schema import PermissionsOptions

class Config(BaseModuleConfig):
    
    module_active:bool = True
    module_active_disabled:bool = True
    cron_logs_to_keep:int = 100