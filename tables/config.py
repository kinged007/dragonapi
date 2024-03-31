# from beanie import Document
from mongoengine import Document, StringField, DictField


class ModuleConfig(Document):
    # user_id: str
    # project_id: str
    
    module = StringField(required=True, unique=True)
    config = DictField()
    
    meta = {'collection': 'module_config'}
    