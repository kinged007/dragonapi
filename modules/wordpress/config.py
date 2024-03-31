from schema.basemodule import BaseModuleConfig, ConfigField
# from .schema import PermissionsOptions

class Config(BaseModuleConfig):
        
    # module_active:bool = True
    # cron_interval:int = 5 # minutes
    # cron_active:bool = True
    # cron_schedule:str = "*/13 * * * *" # Default to every 15 minutes
    
    wordpress_url: str = ""
    
    wordpress: dict = {
        "admin_username": "",
        "admin_app_password": "",
    }
    woocommerce: dict = {
        "consumer_key": "",
        "consumer_secret": "",
    }
    jwt: dict = {
        "secret": "",
        "secret_help": "For JWT exchanges. Use the same Secret defined in your WP Config. Plugin and configuration: https://wordpress.org/plugins/jwt-auth/",
        "expiry_minutes": 10,   
    }
    
    admin_username: str = ""
    admin_app_password: str = ""
    woo_consumer_key: str = ""
    woo_consumer_secret: str = ""
    jwt_secret: str = ""
    jwt_secret_help: str = "For JWT exchanges. Use the same Secret defined in your WP Config. Plugin and configuration: https://wordpress.org/plugins/jwt-auth/"
    jwt_expiry_minutes: int = 10