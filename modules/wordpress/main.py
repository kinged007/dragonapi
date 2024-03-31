# This file houses the main class for the module. It is responsible for handling the module's data and business logic and shared resources
# Acts as a Controller
from loguru import logger as log
from src.basemodule import BaseModuleClass
import requests
from vars import APP_VERSION, DEBUG
from typing import Union, List
import requests
from requests.auth import HTTPBasicAuth
from models.html import strip_html_tags
from models.jwt import JWT
from utils.datetime import timedelta

from .src.woocommerce import WooCommerce

# Get global cache object
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
    
    
    base_url: str = ""
    auth: str = ""
    jwt_secret: str = ""
    token: str = ""
    jwt: JWT = None
    consumer_key: str = ""
    consumer_secret: str = ""
    
    wc: WooCommerce = None
    
    def __init__(self, username: str = None, password:str = None, url: str = None, token:str = None, base_url: str = None, jwt_secret:str = None, consumer_key:str = None, consumer_secret:str = None):
        super().__init__()
        
        self.base_url = base_url.strip('/') if base_url else self.config_get("wordpress_url","").strip('/')
        if username and password:
            self.auth = HTTPBasicAuth(username, password)
        # elif self.config_get("admin_username","") and self.config_get("admin_app_password",""):
        #     self.auth = HTTPBasicAuth(self.config_get("admin_username",""), self.config_get("admin_app_password",""))
        else:
            self.auth = None
        self.token = token
        self.consumer_key = consumer_key if consumer_key else self.config_get("woo_consumer_key","")
        self.consumer_secret = consumer_secret if consumer_key else self.config_get("woo_consumer_key","")
        self.jwt_secret = jwt_secret if jwt_secret else self.config_get('jwt_secret', None)
        if not self.jwt and self.jwt_secret:
                self.jwt = JWT(self.jwt_secret, 'HS256', timedelta(minutes=int(self.config_get('jwt_expiry_minutes', 10))))
        
        self.wc = WooCommerce(self.base_url, self.consumer_key, self.consumer_secret)
        
    async def init(self):
        # Load the defaults from the config
        if not self.base_url: self.base_url = self.config_get("wordpress_url","").strip('/')
        if not self.auth: self.auth = HTTPBasicAuth(self.config_get("admin_username",""), self.config_get("admin_app_password",""))
        if not self.jwt_secret: self.jwt_secret = self.config_get('jwt_secret', None)
        if not self.jwt and self.jwt_secret:
                self.jwt = JWT(self.jwt_secret, 'HS256', timedelta(minutes=int(self.config_get('jwt_expiry_minutes', 10))))
        if not self.consumer_key: self.consumer_key = self.config_get("woo_consumer_key","")
        if not self.consumer_secret: self.consumer_secret = self.config_get("woo_consumer_key","")

    @global_cache.cache(ttl=15, key=lambda self: f"wordpress_test_connection_{self.base_url}")
    def test_connection(self):
        # Test connection to Directus
        log.warning(f"Wordpress: Testing connection to {self.base_url}")
        if not self.base_url:
            return False
        req = self.get("wp-json/wp-site-health/v1", headers={"Something Extra":"Extra"}, unauthenticated=True)
        if req.status_code == 200:
            return True
        log.error(req.text)
        return False


    def authenticate(self, username:str, password:str):
        # This method is just a placeholder to indicate where authentication would be handled.
        # Actual authentication will occur with each request using the HTTPBasicAuth.
        self.auth = HTTPBasicAuth(username, password)
    
    def login(self, username:str, password:str):
        """
        Log the user in by authenticating with Wordpress and return a Directus JWT token
        """
        response = self.post("/jwt-auth/v1/token", data={
            "username": username,
            "password": password,
        }, unauthenticated=True)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to login: {response.text}")

    def use_token(self, token:str):
        self.token = token
        self.auth = None

    def wordpress_request(self, endpoint: str, method: str = "GET", data: dict = None, params: dict = None, **kwargs) -> requests.Response:
        """
        Make a request to the Directus API.
        """
        if not self.base_url:
            raise Exception("Wordpress could not be connected.")
        
        url = f"{self.base_url}/wp-json/{endpoint.strip('/')}"
        
        log.debug(f"Wordpress Request: {method} {url}")
        
        headers = {}
        if 'headers' in kwargs:
            headers = kwargs.get('headers',{})
            del kwargs['headers']
            
        headers.update({
            # "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "User-Agent": f"DRAGON-API/{APP_VERSION}",
            "Content-Type": "application/json",
        })
        
        _auth = None
        if kwargs.get('unauthenticated', False):
            del kwargs['unauthenticated']
        else:
            if self.auth and not self.token:
                _auth=self.auth
            elif self.token:
                headers['Authorization'] = f"Bearer {self.token}"
            
        if method == "GET":
            req = requests.get(url, headers=headers, params=params, auth=_auth, **kwargs)
        elif method == "POST":
            req = requests.post(url, headers=headers, params=params, json=data, auth=_auth, **kwargs)
        elif method == "PATCH":
            req = requests.patch(url, headers=headers, params=params, json=data, auth=_auth, **kwargs)
        elif method == "DELETE":
            req = requests.delete(url, headers=headers, params=params, auth=_auth, **kwargs)
        else:
            raise Exception(f"Invalid method {method}")
        return req
    
    @global_cache.cache(ttl=5 if DEBUG else 60, key=lambda self: f"{self.base_url}{self.auth}{self.token}{self.consumer_key}{self.consumer_secret}", namespace="wordpress")
    def get(self, endpoint: str, data: dict = None, params: dict = None, **kwargs) -> requests.Response:
        return self.wordpress_request(endpoint, method="GET", data=data, params=params, **kwargs)
    
    def post(self, endpoint: str, data: dict = None, params: dict = None, **kwargs) -> requests.Response:
        global_cache.clear(namespace='wordpress')
        return self.wordpress_request(endpoint, method="POST", data=data, params=params, **kwargs)
    
    def patch(self, endpoint: str, data: dict = None, params: dict = None, **kwargs) -> requests.Response:
        global_cache.clear(namespace='wordpress')
        return self.wordpress_request(endpoint, method="PATCH", data=data, params=params, **kwargs)
    
    def delete(self, endpoint: str, data: dict = None, params: dict = None, **kwargs) -> requests.Response:
        global_cache.clear(namespace='wordpress')
        return self.wordpress_request(endpoint, method="DELETE", data=data, params=params, **kwargs)
    

    def get_posts(self, search:str = None):
        _params = {"search": search} if search else {}
        # response = requests.get(f"{self.base_url}/wp-json/wp/v2/posts", auth=self.auth, params=_params)
        response = self.get("/wp/v2/posts", params=_params)
        return response.json()
    
    def get_post(self, post_id:str = None):
        # response = requests.get(f"{self.base_url}/wp-json/wp/v2/posts/{post_id}", auth=self.auth)
        response = self.get(f"/wp/v2/posts/{post_id}")
        return response.json()

    def _create_post(self, data):
        response = self.post(f"/wp/v2/posts", data=data)
        # response = requests.post(f"{self.base_url}/wp-json/wp/v2/posts", auth=self.auth, json=data)
        return response.json()
    
    def _update_post(self, post_id, data):
        response = self.post(f"/wp/v2/posts/{post_id}", data=data)
        # response = requests.post(f"{self.base_url}/wp-json/wp/v2/posts/{post_id}", auth=self.auth, json=data)
        return response.json()

    def get_categories(self):
        response = self.get(f"/wp/v2/categories", params={"_fields": "id,slug,name"})
        # response = requests.get(f"{self.base_url}/wp-json/wp/v2/categories", auth=self.auth, params={"_fields": "id,slug,name"})
        return response.json()

    def create_category(self, data):
        response = self.post(f"/wp/v2/categories", data=data)
        # response = requests.post(f"{self.base_url}/wp-json/wp/v2/categories", auth=self.auth, json=data)
        return response.json()

    def get_tags(self):
        response = self.get(f"/wp/v2/tags", params={"_fields": "id,slug,name"})
        # response = requests.get(f"{self.base_url}/wp-json/wp/v2/tags", auth=self.auth, params={"_fields": "id,slug,name"})
        return response.json()

    def create_tag(self, data):
        response = self.post(f"/wp/v2/tags", params={"_fields": "id,slug,name"})
        # response = requests.post(f"{self.base_url}/wp-json/wp/v2/tags", auth=self.auth, json=data)
        return response.json()

    def get_media(self):
        response = self.get(f"/wp/v2/media", params={"_fields": "id,slug,name"})
        # response = requests.get(f"{self.base_url}/wp-json/wp/v2/media", auth=self.auth)
        return response.json()

    def upload_media(self, file, data):
        headers = {'Content-Disposition': f"attachment; filename={file.name}"}
        response = self.post(f"/wp/v2/media", data=data, headers=headers, files={'file': file})
        # response = requests.post(f"{self.base_url}/wp-json/wp/v2/media", auth=self.auth, headers=headers, files={'file': file}, data=data)
        return response.json()

    # def get_users(self):
    #     response = requests.get(f"{self.base_url}/wp-json/wp/v2/users", auth=self.auth)
    #     return response.json()

    # def create_user(self, data):
    #     response = requests.post(f"{self.base_url}/wp-json/wp/v2/users", auth=self.auth, json=data)
    #     return response.json()
    
    def _find_in_list_of_dicts(self, list_of_dicts, key, value):
        return [d for d in list_of_dicts if d.get(key) == value]
    
    def _wp_ensure_tag_or_cat_exists(self, items, type ):
        
        final_items = []
        
        if type not in ['categories', 'tags']: raise Exception("Invalid type")
        
        if items:
            wp_items = self.get_categories() if type =='categories' else self.get_tags()
            # wp_categories = {cat.get('id'):cat.get('slug') for cat in wp_categories}
            for cat in items:
                new_item = {}
                if isinstance(cat, int):
                    if len(self._find_in_list_of_dicts(wp_items, 'id', cat)) > 0: 
                        final_items.append(cat)
                    continue # Cant add new categories from just an ID
                if isinstance(cat, str):
                    match = self._find_in_list_of_dicts(wp_items, 'slug', cat)
                    if not match: match = self._find_in_list_of_dicts(wp_items, 'name', cat)
                    if len(match) > 0: 
                        final_items.append(match[0].get('id'))
                        continue
                    new_item = {
                        "name": cat,
                    }
                if isinstance(cat, dict):
                    match = self._find_in_list_of_dicts(wp_items, 'id', cat.get('id'))
                    if not match: match = self._find_in_list_of_dicts(wp_items, 'slug', cat.get('slug'))
                    if not match: match = self._find_in_list_of_dicts(wp_items, 'name', cat.get('name'))
                    if len(match) > 0:
                        final_items.append(match[0].get('id'))
                        continue
                    new_item = {
                        "name": cat.get('name', None),
                        "slug": cat.get('slug', None),
                        "description": cat.get('description', None),
                    }
                # Category not found, create it
                new_item["parent"] = 0 
                add_new_item = self.create_category(new_item) if type == 'categories' else self.create_tag(new_item)
                if add_new_item and add_new_item.get('id', None):
                    final_items.append(add_new_item.get('id'))
                    wp_items.append(add_new_item)
                    continue
                    
        return final_items


    def prepare_categories(self, categories: List[Union[int, str, dict]] = None):
        """
        Asserts category ID's and they exist in wordpress.
        """
        return self._wp_ensure_tag_or_cat_exists(categories, 'categories')
        
    def prepare_tags(self, tags: List[Union[int, str, dict]] = None):
        """
        Asserts tag ID's and they exist in wordpress.
        """
        return self._wp_ensure_tag_or_cat_exists(tags, 'tags')
        
    def update_post( self,
        post_id: int,
        title: str = None,
        content: str= None,
        author: int = None,
        # status: str = None, # dont change status. it should be published already
        categories: List[Union[int, str, dict]] = None, # Accepts category ID's or slugs
        tags: List[Union[int, str]] = None, # Accepts tag ID's or slugs
        featured_media: int = None,  # Accepts media ID or dict with media details
        excerpt: str = None,
        slug:str = None,
        format:str = None,
    ):
        """
        Updates a post if it exists.
        """
        # from rich import print
        
        if not post_id: raise Exception("Post ID is required")
        
        # Get the original post
        original_post = self.get_post(post_id)
        
        if original_post and original_post.get('id', None):
            
            if categories and not isinstance(categories[0], int):
                # Get category ID's from slugs
                categories = self.prepare_categories(categories)
                
            if tags and not isinstance(tags[0], int):
                # Get tag ID's from slugs
                tags = self.prepare_tags(tags)

            # print(original_post)
            print("Original Post: " + str(original_post.get('id')))

            # Compare
            to_update = {}
            
            for key in ['title', 'content', 'author', 'categories', 'tags', 'featured_media', 'excerpt', 'slug', 'format']:
                if locals().get(key):
                    _source_post = strip_html_tags(locals().get(key).strip()) if isinstance(locals().get(key), str) else locals().get(key)
                    if isinstance(original_post.get(key), dict):
                        _published_post = strip_html_tags(original_post.get(key).get('rendered', '').strip())
                    elif isinstance(original_post.get(key), str):
                        _published_post = strip_html_tags(original_post.get(key).strip())
                    else:
                        _published_post = original_post.get(key)
                    # print(_source_post, " <> ", _published_post)
                    if _published_post != _source_post:
                        print("\n\n[red]NOT MATCHING[/red]", key, "(length)" , len(_published_post), " <> ", len(_source_post)  )
                        print('[yellow]'+str(_published_post))
                        print('[blue]' + str(_source_post))
                        to_update[key] = locals().get(key)
                        
                    # original_post[key] = locals().get(key)
            if to_update:
                print("Changes Found - Updating post")
                # print(to_update)
                published_post = self._update_post(post_id, to_update)
                # print(published_post)
                return published_post
            else:
                print("No changes found")
                return original_post
        
        raise Exception(f"Post '{post_id}' not found")
        # return {"error": f"Post '{post_id}' not found"}


    def publish_post( self,
        title: str,
        content: str,
        author: int = None,
        status: str = "draft",
        categories: list = Union[int, str], # Accepts category ID's or slugs, assumes correct ID's
        tags: list = Union[int, str], # Accepts tag ID's or slugs, assumes correct ID's
        featured_media: int = None,  # Accepts media ID or dict with media details, assumes correct ID
        excerpt: str = None,
        slug:str = None,
        format:str = "standard",
    ):
        
        if not title or not content: raise Exception("Title and Content are required")

        if not slug: slug = title.lower().replace(" ","-")
        if not status: status = "draft"

        if categories and not isinstance(categories[0], int):
            # Get category ID's from slugs
            categories = self.prepare_categories(categories)
            
        if tags and not isinstance(tags[0], int):
            # Get tag ID's from slugs
            tags = self.prepare_tags(tags)
        
        # Convert content to wordpress blocks
        # content = html_to_wordpress_blocks(content)
        
        # Publish post
        publish_post = {
            "title": title,
            "slug": slug,
            "content": content,
            "status": status,
            "categories": categories,
            "tags": tags,
            "featured_media": featured_media,
            "excerpt": excerpt,
            "author": author,
            "format": format,
        }
        
        # if Successful, increment publish_count
        published_post = self._create_post(publish_post)
        
        return published_post
    
    