from beanie import Document
from fastapi.security import HTTPBasicCredentials
from pydantic import ConfigDict, BaseModel, EmailStr
from bson import ObjectId

class Project(Document):
    name: str
    admin_id: str
    

    class Settings:
        name = "project"
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "My Awesome Project"
        }
    })
    
class AppKeys(Document):
    """
    Stores API keys for each project.
    """
    project_id: str # id of the project
    api_key: str
    api_secret: str = None
    user_id: str = None # id of the user who created the key
    platform: str = None # platform of the key, eg. openai, replicate, huggingface, zapier, etc.
    
    
    
    class Settings:
        name = "app_keys"
        
    # model_config = ConfigDict(json_schema_extra={
    #     "example": {
    #         # "_id": "60f3f2f01b7d8b4a9e4a9e0f",
    #         # "project_id": "15124f23g235232g24t24y53", # Saved automatically
    #         "api_key": "sk-...",
    #         "api_secret": "",
    #         # "owner": "3rohHPAHfh192yhfoeiwd", # Saved automatically
    #         "platform": "openai"
    #     }
    # })

class AppKeysInput(BaseModel):
    api_key: str
    api_secret: str = None
    # owner: str
    platform: str
    # project_id: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "api_key": "sk-...",
                "api_secret": "",
                # "owner": "3rohHPAHfh192yhfoeiwd",
                "platform": "openai",
                # "project_id": "15124f23g235232g24t24y53"
            }
        }

    @classmethod
    def from_orm(cls, app_keys: AppKeys):
        return cls(**app_keys.model_dump(exclude={"_id","project_id","owner"}))
