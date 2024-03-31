from mongoengine import Document, StringField, ListField

class ApiKeys(Document):
    name = StringField(required=True)
    api_key = StringField(required=True)
    permissions = ListField(StringField(), default=list)

    meta = {'collection': 'api_keys'}