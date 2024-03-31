from beanie import Document


class ModuleConfig(Document):
    # user_id: str
    # project_id: str
    
    module: str
    config: dict    
    
    class Settings:
        name = "module_config"
