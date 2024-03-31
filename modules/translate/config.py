from schema.basemodule import BaseModuleConfig, ConfigField
# from .schema import PermissionsOptions

class Config(BaseModuleConfig):
        
    # module_active:bool = True
    
    translate_tool: str = "google-free" # or deepl
    translate_tool_options: list = ["google-free","google", "deepl"] # or deepl
    tool_url: str = ""
    api_key: str = ""
    api_secret: str = ""
    
    
    
    
    