# This file houses the main class for the module. It is responsible for handling the module's data and business logic and shared resources
# Acts as a Controller
from loguru import logger as log
from src.basemodule import BaseModuleClass
import requests
from os import path


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
    

    token:str = None
    chat_id:str = None
    url: str = ""
    
    def __init__(self, token = None):
        
        super().__init__()
        
    def connect(self, token = None):

        if not token:
            log.debug("Telegram Module: Using module config token")
            self.token = self.config_get('telegram_bot_token', None)
        elif token:
            log.debug("Telegram Module: Using provided token")
            self.token = token
        
        if not self.token:
            raise Exception("No Telegram Bot Token provided")
        
        self.url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, chat_id, message, parse_mode="Markdown"):
        # TODO move this to a task handler, such as RQ
        log.debug("Sending message to Telegram...")
        
        try:
            
            url = f"{self.url}/sendMessage"

            payload = {
                "text": message,
                "parse_mode": parse_mode,
                "disable_web_page_preview": False,
                "disable_notification": False,
                "reply_to_message_id": None,
                "chat_id": chat_id,
            }
            headers = {
                "accept": "application/json",
                "User-Agent": "MetaTrader Trade Monitor",
                "content-type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers)

            if response.status_code != 200:
                raise Exception(f"Error: {response.status_code} - {response.text}")
            
        except Exception as e:
        
            raise Exception(f"Error: {e}")
        
        
    
    def send_image(self, chat_id, file, caption=None, parse_mode="Markdown"):
        
        log.debug("Sending image to Telegram...")

        try:
            
            url = f"{self.url}/sendPhoto"

            payload = {
                "chat_id": chat_id,
                "caption": caption,
            }
            
            files = {}

            # Send photo
            if isinstance(file, bytes):
                # Upload photo
                files = {
                    "photo": file
                }
            elif 'http' in file:
                # Send URL
                payload['photo'] = file
            elif path.exists(file):
                # Upload photo
                files = {
                    "photo": open(file, 'rb')
                }
            else:
                # Try sending file id
                payload['photo'] = file
                
            # if not files:
            #     raise Exception("Cannot interpret file provided")
            
            headers = {
                "accept": "application/json",
                "User-Agent": "APP-API-CLIENT",
                # "Content-Type": "multipart/form-data",
            }
            
            response = requests.post(url, data=payload, headers=headers, files=files)
            
            if response.status_code != 200:
                raise Exception(f"Error: {response.status_code} - {response.text}")
            
            # print(response.json())
            
        except Exception as e:
        
            raise Exception(f"Error: {e}")