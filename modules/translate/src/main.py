
from modules.translate import Config
import requests
from os import path
from loguru import logger as log
from time import time


class Translate:
    
        # This dictionary will store the created instances
    __instances = {}
    __initialised = 0
    # __config = {}

    def __new__(cls, *args, **kwargs):
        # Check if an instance already exists
        if cls not in cls.__instances:
            # Create a new instance and store it in the dictionary
            cls.__instances[cls] = super().__new__(cls)
            log.debug(f"A new instance of {cls.__name__} has been created")
        return cls.__instances[cls]
    
    def __init__(self):
        # This code will be executed each time a new instance is created 
        if self.__initialised > time() - 15 :
            return
        
        log.info(f"The instance of ':{self.__class__.__name__}' is initializing.")
        
        # Initialize module config 
        self.__initialised = time()
        
        
        self.config = Config() 
        self.tool = self.config.get('TRANSLATE_TOOL', 'google')
        self.api_key = self.config.get('API_KEY', '')
        if self.tool == 'deepl':
            self.url = "https://api.deepl.com/v2/translate"
        elif self.tool == 'google':
            self.url = "https://translation.googleapis.com/language/translate/v2"
        
        
    def translate(self, text, target_lang, source_lang = None):
        
        # print("Translating '", text, "' to '", target_lang, "' using tool", self.tool) # DEBUG
        
        if self.tool == 'google-free':
            from modules.translate.src.google import google_free_translate
            return google_free_translate(text, target_lang, source_lang)
        if self.tool == 'deepl':
            # return self.deepl_translate(text, target_lang, source_lang)
            pass
        if self.tool == 'google':
            # API version
            # if self.api_key:
            #     return self.google_translate_api(text, target_lang, source_lang)
            pass