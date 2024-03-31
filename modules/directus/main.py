# This file houses the main class for the module. It is responsible for handling the module's data and business logic and shared resources
# Acts as a Controller
from loguru import logger as log
from src.basemodule import BaseModuleClass
import requests
from vars import APP_VERSION, DEBUG

# Get global cache
from utils.cache import global_cache


# Import the module's schema

# Import the module's config

# Import the module's database model


class Module(BaseModuleClass):
    
    # def __init__(self):
    #     super().__init__()
    #     log.warning("CHILD MODULE (module controller) - Module Loaded: "+self.__class__.__name__)
    
    # config is autoloaded from the database, using config.py as a base.
    # module config is callable from self.config_get(key,fallback) or self.config_set(key,value)
    # global config is callable from self.global_config(key,fallback)
    
    # Correct permission format is: "module_name.permission_name"
    # callable via self.permission("permission_name")
    
    
    url: str = ""
    token: str = ""
    
    
    def __init__(self, url: str = None, token:str = None):
        super().__init__()
        
        self.url = url if url else self.config_get("directus_url","")
        self.token = token if token else self.config_get("directus_access_token", "")
        
    async def init(self):
        if not self.url: self.url = self.config_get("directus_url","")
        if not self.token: self.token = self.config_get("directus_access_token", "")

    
    # @cached(cache, key=lambda self: f"{self.url}{self.token}")
    @global_cache.cache(ttl=5 if DEBUG else 60, key=lambda self: f"{self.url}{self.token}", namespace="directus")
    def test_connection(self):
        # Test connection to Directus
        log.debug(f"Directus: Testing connection to {self.url}")
        if not self.url or not self.token:
            return False
        req = self.get("server/health")
        if req.status_code == 200:
            return True
        log.error(req.text)
        return False
    
    def directus_request(self, endpoint: str, method: str = "GET", data: dict = None, params: dict = None) -> requests.Response:
        """
        Make a request to the Directus API.
        """
        if not self.url or not self.token:
            raise Exception("Directus could not be connected.")
        
        url = f"{self.url.strip('/')}/{endpoint.strip('/')}"
        
        log.debug(f"Directus Request: {method} {url}")
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "User-Agent": f"DRAGON-API/{APP_VERSION}",
            "Content-Type": "application/json",
        }
        if method == "GET":
            req = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            req = requests.post(url, headers=headers, params=params, json=data)
        elif method == "PATCH":
            req = requests.patch(url, headers=headers, params=params, json=data)
        elif method == "DELETE":
            req = requests.delete(url, headers=headers, params=params )
        else:
            raise Exception(f"Invalid method {method}")
        return req
    
    @global_cache.cache(ttl=5 if DEBUG else 60, key=lambda self: f"{self.url}{self.token}", namespace="directus")
    def get(self, endpoint: str, data: dict = None, params: dict = None) -> requests.Response:
        return self.directus_request(endpoint, method="GET", data=data, params=params)
    
    def post(self, endpoint: str, data: dict = None, params: dict = None) -> requests.Response:
        global_cache.clear(namespace='directus')
        return self.directus_request(endpoint, method="POST", data=data, params=params)
    
    def patch(self, endpoint: str, data: dict = None, params: dict = None) -> requests.Response:
        global_cache.clear(namespace='directus')
        return self.directus_request(endpoint, method="PATCH", data=data, params=params)
    
    def delete(self, endpoint: str, data: dict = None, params: dict = None) -> requests.Response:
        global_cache.clear(namespace='directus')
        return self.directus_request(endpoint, method="DELETE", data=data, params=params)
    
    def comment(self, comment: str, collection: str, item: str) -> requests.Response:
        global_cache.clear(namespace='directus')
        return self.directus_request(f"activity/comment", method="POST", data={
            "comment": comment,
            "item": item,
            "collection": collection,
        })

    @classmethod
    def user_name(cls, item_data:dict, first_name=True, last_name=True):
        """
        Return a user's name from a Directus item.
        """
        user_obj = None
        if item_data.get("first_name", None):
            # Dealing with user object
            user_obj = item_data
        elif item_data.get("data", None):
            # User object is nested
            if item_data.get("first_name", None):
                user_obj = item_data.get("data")
            elif item_data.get('data',{}).get("directus_users_id", {}).get('first_name', None):
                user_obj = item_data.get('data').get("directus_users_id")
                
        elif item_data.get("directus_users_id", None) and item_data.get("directus_users_id", {}).get("first_name", None):
            # User object is nested
            user_obj = item_data.get("directus_users_id")
        
        if user_obj:
            _fn = user_obj.get("first_name", "") if first_name else ""
            _ln = user_obj.get("last_name", "") if last_name else ""
            _fn = "" if _fn and _fn.lower() == "none" else _fn
            _ln = "" if _ln and _ln.lower() == "none" else _ln
            
            log.debug(f"{_fn} {_ln}".strip())
            
            return f"{_fn} {_ln}".strip()

        return ""

    def asset_url(self, asset_id:str, include_filename:bool=True):
        """
        Return a URL for an asset.
        """
        if asset_id:
            if include_filename:
                asset = self.get(f"files/{asset_id}").json()
                if asset.get("data", None):
                    asset = asset.get("data")
                    return f"{self.url}/assets/{asset_id}/{asset.get('filename_download', '')}"
            return f"{self.url}/assets/{asset_id}"
        return ""


    async def run_cron(self):
        """
        This method is called by the cron job at the interval defined in the module's config.
        """
        pass
    