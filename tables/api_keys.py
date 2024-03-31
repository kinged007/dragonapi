from beanie import Document


class ApiKeys(Document):
    # user_id: str
    # project_id: str
    
    name: str
    api_key: str
    permissions: list[str] = []
    
    class Settings:
        name = "api_keys"
