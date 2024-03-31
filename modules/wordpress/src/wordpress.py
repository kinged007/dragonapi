import requests
from loguru import logger as log
from vars import APP_VERSION
from typing import List, Union
from requests.auth import HTTPBasicAuth
from pydantic import BaseModel

from models.html import strip_html_tags

class WordPress(BaseModel):
    
    pass