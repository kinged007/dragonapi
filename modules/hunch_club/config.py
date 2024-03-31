# from utils.datetime import datetime, timedelta
from schema.basemodule import BaseModuleConfig, ConfigField
from utils.datetime import utc_now, datetime, timedelta
# from .schema import PermissionsOptions

class Config(BaseModuleConfig):
        
    module_active:bool = True
    # cron_interval:int = 5 # minutes
    cron_active:bool = True
    cron_schedule:str = "*/15 * * * *" # Default to every 15 minutes
    cron_schedule_field:ConfigField = ConfigField.cron
    
    mongodb_url:str = ""
    mongodb_url_field:ConfigField = ConfigField.password
    mongodb_database:str = "hunch_club"
    
    fix_tips_schedule:str = "0 0 * * *" # Default to every day at midnight
    fix_tips_next_exection:datetime = utc_now()
    fix_tips_next_exection_disabled:bool = True
    fix_tips_from_last_date:datetime = utc_now() - timedelta(days=30)
    fix_tips_from_last_date_disabled:bool = True
    
    # TODO Move fields with _X to a config schema dict.
    # eg. config_schema = { "fix_tips_schedule": {
    #         "type": ConfigField.cron,
    #         "help": "The schedule for fixing tips. Default to every day at midnight."
    #     }, "fix_tips_next_exection": {
    #         "type": ConfigField.datetime,
    #         "help": "The next execution time for fixing tips.",
    #         "disabled": True,
    #     }, ...
        
    # }