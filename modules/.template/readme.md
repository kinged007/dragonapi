# Module

## Structure

main.py 

    class Module(BaseModuleClass)
        
        def __init__(self):
            super().__init__()
        
        
    ## Inherited
        
    ### Atributes
        
        module_name = name of module
        
        
    ### Methods
        
        # Read module config
        
            def get( key, fallback_value )
        
        # Update module config
        
            async def set( key, value )
        
        # Read Global config
        
            def global_config( key, fallback_value ) 
        
        # Gets correct format for checking module permissions
        
            @classmethod
            def permission( name ) -> (str) module_name.permission_name
        
        # Cron job manager. Is called when its time to execute according to modules cron config
        
            async def cron()
        
        # Get data folder for file storage. Function will ensure folder exists so you do not have to check it.
        
            def data_folder( subfolder )
        
        

config.py
    
    # Define all config variables and default values for the module. Saved in the database. Callable via Module().get('variable', 'fallback value')
    
        class Config(BaseModuleConfig)
            
            ## Defaults
            module_active:bool = False
            cron_interval:int = 15 # minutes
            cron_active:bool = False
        
schema.py

    # Use this file to store schema objects for your app. 
    
    ## required schemas:
    
        class PermissionsOptions(Enum)
            pass
        
    
    # This file also defines the database table schema stored in the main app database and automatically initialized via the app startup. The app database uses 'beanie' to manage database actions using this table schema.
    
    ## eg.
    
        from beanie import Document
        
        class Users(Document):
            first_name: str = ""
            last_name: str = ""
            email: EmailStr
            role: str = "customer"
            
            class Config:
                collection = "users"
                json_schema_extra = {
                    "example": {
                        "first_name": "John",
                        "last_name": "Doe",
                        "email": "example@email.com",
                        "role": "customer"
                    }
                }
        