from utils.datetime import datetime, timedelta, utc_now
from time import sleep
from loguru import logger as log
from models.mongodb import MongoDB
from pydantic import BaseModel
import json

# Get global cache
from utils.cache import global_cache

class Tips(BaseModel):
    
    yesterday_tips:list = []
    today_tips:list = []
    last_tips:dict = {}
    mongodb_url: str = ""
    mongodb_database: str = ""

    def __init__(self, mongodb_url:str, mongodb_database:str):
        super().__init__()
        self.mongodb_url = mongodb_url
        self.mongodb_database = mongodb_database
        if not self.mongodb_url or not self.mongodb_database:
            raise Exception("MongoDB URL and Database not set.")
    
    @global_cache.async_cache(ttl=300, namespace="hunch_club_tips", key='fetch_all_tips')
    async def fetch_all_tips(self) -> list:
        # Get all the tips
        
        results = []
        
        async with MongoDB().url(self.mongodb_url).connect() as mongo:
            mongo.database(self.mongodb_database).collection('daily_tips')
            results = await mongo.query({
                # 'datetime': {
                #     '$gte': midnight, 
                #     '$lt': tomorrow
                #     }
                # "event_name" : 'England Championship'
                })
            if results:
                results = json.loads(json.dumps(results, default=str))
                
        return results

    @global_cache.async_cache(ttl=300, namespace="hunch_club_tips", key='fetch_tips')
    async def fetch_tips(self, date:datetime = utc_now(), day_delta: int = 0) -> list:
        log.warning("Fetching tips. "+str(date))
        today = date #utc_now() #datetime(year=2024, month=1, day=10) #utc_now()
        if day_delta >= 0:
            from_date = datetime(date.year, date.month, date.day)
            future_date = from_date + timedelta(days=1+day_delta) 
        else:
            from_date = datetime(date.year, date.month, date.day) + timedelta(days=day_delta)
            future_date = datetime(date.year, date.month, date.day) + timedelta(days=1)
        
        log.debug(f"Getting Tips data from {from_date} to {future_date}")
        
        results = []
        
        async with MongoDB().url(self.mongodb_url).connect() as mongo:
            mongo.database(self.mongodb_database).collection('daily_tips')
            results = await mongo.query({
                'datetime': {
                    '$gte': from_date, 
                    '$lt': future_date
                    }
                # "event_name" : 'England Championship'
                })
            if results:
                for x in results:
                    x['id'] = str(x['_id'])
                    del x['_id']
                    # for key, value in x.items():
                    #     if isinstance(value, datetime):
                    #         x[key] = value.isoformat()

        return results
    

    async def update_tip(self, id, data:dict):
        async with MongoDB().url(self.mongodb_url).connect() as mongo:
            mongo.database(self.mongodb_database).collection('daily_tips')
            results = await mongo.update(id, data)
            log.debug("Clearing tips caches")
            global_cache.clear(namespace='hunch_club_tips')
        return results

    @global_cache.async_cache(ttl=300, namespace="hunch_club_platforms", key='fetch_publish_platforms')
    async def fetch_publish_platforms(self, query = {}):

        async with MongoDB().url(self.mongodb_url).connect() as mongo:
            mongo.database(self.mongodb_database).collection("hunch_club_publish_platforms")
            results = await mongo.query(query)
            if results:
                for x in results:
                    x['id'] = str(x['_id'])
                    del x['_id']
                    for key, value in x.items():
                        if isinstance(value, datetime):
                            x[key] = value.isoformat()

        return results
    
    async def find_one_platform(self, id:str):
        
        async with MongoDB().url(self.mongodb_url).connect() as mongo:
            mongo.database(self.mongodb_database).collection("hunch_club_publish_platforms")
            results = await mongo.find_one_by_id(id)
            if results:
                if isinstance(results, dict):
                    results['id'] = str(results['_id'])
                    del results['_id']
                    for key, value in results.items():
                        if isinstance(value, datetime):
                            results[key] = value.isoformat()
                
                else:
                    
                    for x in results:
                        x['id'] = str(x['_id'])
                        del x['_id']
                        for key, value in x.items():
                            if isinstance(value, datetime):
                                x[key] = value.isoformat()

        return results
    
    
    async def update_publish_platform(self, id:str, platform:dict):
        async with MongoDB().url(self.mongodb_url).connect() as mongo:
            mongo.database(self.mongodb_database).collection("hunch_club_publish_platforms")
            results = await mongo.update(id, platform)
            log.debug("Clearing platform caches")
            global_cache.clear(namespace='hunch_club_platforms')
        return results

    async def delete_publish_platform(self, id:str):
        async with MongoDB().url(self.mongodb_url).connect() as mongo:
            mongo.database(self.mongodb_database).collection("hunch_club_publish_platforms")
            results = await mongo.delete_by_id(id)
            log.debug("Clearing platform caches")
            global_cache.clear(namespace='hunch_club_platforms')
        return results

    async def add_publish_platform(self, platform:dict):
        async with MongoDB().url(self.mongodb_url).connect() as mongo:
            mongo.database(self.mongodb_database).collection("hunch_club_publish_platforms")
            results = await mongo.insert(platform)
            log.debug("Clearing platform caches")
            global_cache.clear(namespace='hunch_club_platforms')
            
        return results