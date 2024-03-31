# This file houses the main class for the module. It is responsible for handling the module's data and business logic and shared resources
# Acts as a Controller

# NOTE Primary database interaction will be with Directus which is the Pollygene Admin UI.

from loguru import logger as log
from utils.datetime import datetime, timedelta, timezone, utc_now
import asyncio
import requests

from src.basemodule import BaseModuleClass

# Import the module's schema and models
# from .schema import
from src.cronmanager import CronManager
from models.jwt import JWT
from vars import APP_VERSION, DEBUG

# Get global cache object
# from utils.cache import global_cache

from modules import directus
from modules import wordpress
# Import the module's config

# Import the module's database model

class Module(BaseModuleClass):


    db: directus.Module = None
    wp: wordpress.Module = None
    jwt: JWT = None

    # config is autoloaded from the database, using config.py as a base.
    # module config is callable from self.config_get(key,fallback) or self.config_set(key,value)
    # global config is callable from self.global_config(key,fallback)

    # Correct permission format is: "module_name.permission_name"
    # callable via self.permission("permission_name")

    async def init(self):
        pass

    async def run_cron(self):
        """
        This method is called by the cron job at the interval defined in the module's config.
        """
        log.debug("Main cron job for module started.")



    def db_connect(self):
        """
        This method ensures that the database is connected before any operations are performed.
        """
        if not self.db:
            self.db = directus.Module()
            if not self.db.test_connection():
                log.error("Failed to connect to Directus")
        if not self.wp:
            self.wp = wordpress.Module()
            if not self.wp.test_connection():
                log.error("Failed to connect to Wordpress")
        
        if self.db and self.wp:
            log.debug("DB is connected.")
            return True
        
        log.debug("DB is not connected.")
        return False
        # if not self.db:
        #     # Connect to the database
        #     log.debug("Connecting to database.")
        #     # if not self.config_get('directus_url') or not self.config_get('directus_token'):
        #     #     raise Exception("Directus URL or Access Token not set.")
        #     # self.db = Directus(self.config_get('directus_url'), self.config_get('directus_token'))
        #     self.db = directus.Module()
        #     if not self.db:
        #         raise Exception("Failed to connect to Directus.")
        #     print(type(self.db), self.db)
        # if not self.db.test_connection():
        #     self.db = None
        #     raise Exception("Failed to connect to Directus.")

        return True

    def get_species(self):
        """
        Get the list of species from the database
        """
        # Make sure we are connected to the DB
        if not self.db_connect():
            return []

        try:
            species = self.db.get("items/species")
            if species.status_code == 200:
                species = species.json()
                return species['data']
        except Exception as e:
            log.error(f"Failed to get species from Directus: {e}")

        return []

    def get_test_types(self):
        """
        Get the list of test_types from the database
        """
        # Make sure we are connected to the DB
        if not self.db_connect():
            return []

        try:
            resp = self.db.get("items/test_type", params={
                "fields":"*",
                "filter[status][_eq]":"published",
            } )
            if resp.status_code == 200:
                data = resp.json()['data']
                return_data = []
                for item in data:
                    return_data.append({
                        "id": item['id'],
                        "test_type": item['test_type'],
                        "test_result_options": [x['result'] for x in item['test_result_options']],
                    })
                return return_data
        except Exception as e:
            log.error(f"Failed to get test_types from Directus: {e}")

        return []

    # Method to log user in and get a token
    # @global_cache.cache(ttl=10 if DEBUG else 60)
    def login(self, username:str, password:str):
        """
        Log the user in by authenticating with Wordpress and return a Directus JWT token
        """
        log.warning("Logging in user.")
        if not username or not password:
            raise Exception("Username and password are required.")

        # if f"{username}:{password}" in auth_cache:
        #     log.warning("Returning cached token.")
        #     return auth_cache[f"{username}:{password}"]

        if not self.db_connect():
            raise Exception("Failed to connect to Database.")

        # Try wordpress login
        try:
            login_req = self.wp.login(username, password)
        except Exception as e:
            log.error(f"Failed to login to Wordpress: {e}")
            raise Exception("Failed to login.")

        wp_user = login_req.get('data', {})

        if not wp_user:
            raise Exception("User data not found: " + str(login_req))

        db_user_req = self.db.get("users", params={
            "filter[wordpress_user_id][_eq]": wp_user.get('id',None),
            # "fields": "id,first_name,last_name,email,wordpress_user_id,email_notifications,language,role",
        })

        if db_user_req.status_code != 200 :
            raise Exception("Error with Directus request.")

        db_data = db_user_req.json()
        db_data = db_data.get('data', [])

        if not db_data:
            log.debug("User not found in Directus. Checking for email.")
            # Check if email exists
            if not wp_user.get('email', None):
                raise Exception("User email not found.")

            db_user_req = self.db.get("users", params={
                "filter[email][_eq]": wp_user.get('email'),
                # "fields": "id,first_name,last_name,email,wordpress_user_id,email_notifications,language,role",
            })

            if db_user_req.status_code != 200 :
                raise Exception("Error connecting to database.")

            db_data = db_user_req.json()
            db_data = db_data.get('data', [])

            if db_data:
                # Update user with wordpress_user_id and other data
                update = {
                    "wordpress_user_id": wp_user.get('id', None),
                    "first_name": wp_user.get('firstName', ''),
                    "last_name": wp_user.get('lastName', ''),
                    "password": password,
                }
                res = self.db.patch(f"users/{db_data[0]['id']}", data=update)

            if not db_data:
                # New user
                log.debug("User not found in Directus. Creating new user.")
                # Create user in Directus
                res = self.db.post('uers', data={
                    "first_name": wp_user.get('firstName', ''),
                    "last_name": wp_user.get('lastName', ''),
                    "email": wp_user.get('email', ''),
                    "password": password,
                    "wordpress_user_id": wp_user.get('id', None),
                })
                log.debug(res.text)
                if res.status_code != 200:
                    raise Exception("Failed to create user in Directus.")
                db_data = res.json()['data']

        # User exists.
        log.debug("User exists in Directus. Returning a new token of user ID's on both platforms.")
        db_user = db_data[0]

        # Create a JWT token
        token = self.wp.jwt.create({"uid": db_user['id'], "wpid": wp_user.get('id', None)})

        # auth_cache[f"{username}:{password}"] = token
        _expire = utc_now() + timedelta(minutes=self.config_get('jwt_expiry_minutes', 10))
        return {"token": token, "uid": db_user['id'], "wpid": wp_user.get('id', None), "expires": int(_expire.timestamp()) }
