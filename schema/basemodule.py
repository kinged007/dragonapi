from pydantic import BaseModel
from enum import Enum

class BaseModuleConfig(BaseModel):
    """
    Base class for module configuration
    """
    module_active:bool = False
    # cron_interval:int = 15 # minutes
    cron_active:bool = False
    cron_schedule:str = "*/15 * * * *" # Default to every 15 minutes

class ConfigField(Enum):
    text = "text"
    textarea = "textarea"
    integer = "integer"
    float = "float"
    email = "email"
    password = "password"
    select = "select"
    multiselect = "multiselect"
    checkbox = "checkbox" # boolean. Not really needed.
    radio = "radio"
    date = "date"
    datetime = "datetime"
    time = "time"
    # file = "file"
    # image = "image"
    color = "color"
    # range = "range"
    hidden = "hidden"
    html = "html"
    markdown = "markdown"
    code = "code"
    json = "json"
    yaml = "yaml"
    url = "url"
    # tel = "tel"
    # search = "search"
    cron = "cron"
    
    # Info and helpful fields
    header = "header"
    subheader = "subheader"
    divider = "divider"
    notice_info = "notice_info"
    notice_warning = "notice_warning"
    notice_error = "notice_error"
    notice_success = "notice_success"
    
    def __str__(self) -> str:
        return self.value
    def __repr__(self):
        return self.value

class ConfigFieldConfig(BaseModel):
    """
    Configuration for a field, primarily useful in the UI
    """
    type:ConfigField = ConfigField.text
    help:str = ""
    disabled:bool = False
    repeatable:bool = False
    required:bool = False
    options:list = []
    placeholder:str = ""
    
    def model_dump(self):
        return {
            "type": self.type.value,
            "help": self.help,
            "disabled": self.disabled,
            "repeatable": self.repeatable,
            "options": self.options,
            "required": False,
            "placeholder": self.placeholder,
        }