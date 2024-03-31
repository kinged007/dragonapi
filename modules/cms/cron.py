# from rich import print

from models.utils import log_time
from modules.directus import Directus
from models.cron import BaseCronManager

class CronManager(BaseCronManager):

    
    async def run(self):
        print("Running CMS Cron Job")
        # Run cron jobs here.
        
        ### Cron #1: Look for CMS content that needs to be published and publish it to the correct platform
        ### Cron #2: ??
        
        directus = Directus()
        
        # posts = directus.get("items/post", params={
        #     "filter[publish_date][_lte]": "$NOW", 
        #     "filter[status][_eq]": "scheduled", 
        #     # "fields": "id, title, publish_date, status"
        # })
        
        # print(posts.json())
        
        
        