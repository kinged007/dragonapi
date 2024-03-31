# This file houses the main class for the module. It is responsible for handling the module's data and business logic and shared resources
# Acts as a Controller
from loguru import logger as log
from src.basemodule import BaseModuleClass

# Import the module's schema

# Import the module's config

# Import the module's database model

# TODO Introduce caching for the translation results to avoid unnecessary API calls

class Module(BaseModuleClass):
    
    # config is autoloaded from the database, using config.py as a base.
    # module config is callable from self.config_get(key,fallback) or self.config_set(key,value)
    # global config is callable from self.global_config(key,fallback)
    
    # Correct permission format is: "module_name.permission_name"
    # callable via self.permission("permission_name")
    
    def translate(self, text, target_lang, source_lang = None):
        
        _tool = self.config_get("translate_tool", "google")
        
        log.debug(f"Translating '{text}' to '{target_lang}' using tool '{_tool}") 
        
        if source_lang: source_lang = source_lang.lower()
        
        if _tool == 'google-free':
            from modules.translate.src.google import google_free_translate
            return google_free_translate(text, target_lang.lower(), source_lang)
        if _tool == 'deepl':
            # return self.deepl_translate(text, target_lang, source_lang)
            pass
        if _tool == 'google':
            # API version
            # if self.api_key:
            #     return self.google_translate_api(text, target_lang, source_lang)
            pass
        
        return text