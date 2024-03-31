from loguru import logger as log
from pydantic import BaseModel

# from .wordpress import WordPress

class WooCommerce(BaseModel):
    
    base_url:str = ""
    consumer_key:str = ""
    consumer_secret:str = ""
    
    def __init__(self, base_url:str, consumer_key:str, consumer_secret:str):
        super().__init__()
        
        self.base_url = base_url
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
    
    def test(self, **kwargs):
        log.debug("TESTING")
        log.debug(self.base_url)
        log.debug(self.consumer_key)
        log.debug(self.consumer_secret)
        return "test"
    