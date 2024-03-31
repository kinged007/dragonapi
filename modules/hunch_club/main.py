# This file houses the main class for the module. It is responsible for handling the module's data and business logic and shared resources
# Acts as a Controller
from loguru import logger as log
from utils.datetime import datetime, timedelta
import asyncio

from src.basemodule import BaseModuleClass

# Import the module's schema and models
from .schema import TipSchema, HunchClubPublishPlatform
from .src.publish_tips import PublishTips
from .src.model_tips import Tips
from src.cronmanager import CronManager
from models.mongodb import MongoDB
from utils.datetime import utc_datetime, utc_now

# Import the module's config

# Import the module's database model

class Module(BaseModuleClass):
    
    
    today: datetime = None
    yesterday: datetime = None
    today_tips: list = []
    yesterday_results: list = []
    tips_model: Tips = None    
    publish_model: PublishTips = None
    
    def __init__(self):
        super().__init__()
        # log.warning("CHILD MODULE (module controller) - Module Loaded: "+self.__class__.__name__)
        # self.tips_model = Tips(self.config_get('mongodb_url',None), self.config_get('mongodb_database',None))
    
    # config is autoloaded from the database, using config.py as a base.
    # module config is callable from self.config_get(key,fallback) or self.config_set(key,value)
    # global config is callable from self.global_config(key,fallback)
    
    # Correct permission format is: "module_name.permission_name"
    # callable via self.permission("permission_name")

    
    async def run_cron(self):
        """
        This method is called by the cron job at the interval defined in the module's config.
        """
        log.debug("Main cron job for module started.")
        
        self.tips_model = Tips(self.config_get('mongodb_url',None), self.config_get('mongodb_database',None))
        self.publish_model = PublishTips( )
        
        # Publishing Platforms
        platforms = await self.tips_model.fetch_publish_platforms({"active":True})
        # log.debug(platforms)
        
        if not platforms:
            await self.cron.log("No active publishing platforms found.", type="warning")
        
        if platforms:
            # Check if platform is ready
            
            # Moved task of searching for tips data to its own method.
            for platform in platforms:
                
                platform = HunchClubPublishPlatform(**platform)
                
                if self.publish_model.ready( platform=platform, force=False):
                    
                    log.debug(f"Platform: {platform.name} is Ready")
                    
                    try:
                        data = await self.fetch_tips(platform)
                        if not data and not platform.publish_if_no_tips:
                            raise Exception(f"No tips data found for platform {platform.name}.")
                        res = await self.publish_tips(data, platform, force=False)
                        if res == True: # Auto checks if time to publish
                            await self.cron.log(f"Filtered through {len(data)} {platform.publish_type.capitalize()} data and published to {platform.name}:{platform.channel}.", type="info")
                            log.debug(f"Publish Schedule: {platform.publish_schedule}")
                            if not len(platform.publish_schedule.split(" ")) >= 5:
                                platform.publish_schedule = "30 8 * * *"
                                await self.cron.log.warning(f"Publish Schedule for {platform.name} is invalid. Setting to default: 30 8 * * *", type="warning")
                            platform.next_publish = CronManager.next_iter(platform.publish_schedule)
                            await self.tips_model.update_publish_platform(platform.id, platform.model_dump())
                            await asyncio.sleep(1)
                            continue
                        
                        raise Exception(res)
                        
                    except Exception as e:
                        await self.cron.log(f"Error publishing to platform {platform.name}: {str(e)}", type="info")


                
                # # Dates
                # self.today = utc_now()
                # self.yesterday = utc_now() - timedelta(days=1)
                # self.today_tips = await self.tips_model.fetch_tips( self.today )
                # self.yesterday_results = await self.tips_model.fetch_tips( self.yesterday )
                # _update_platform = False
                
                # await asyncio.sleep(0.1)
                
                # # NOTE: In theory, if there were no tips to publish / an error, then the next_publish date should not be updated.
                # # This will cause an issue if an error occured that should not prevent the next publish date from being updated.
                # # TODO More sophisticated error handling. Return dict of errors and successes. Different codes and process seperately for each publish tips/results
                
                # # Publish results
                # if len(self.yesterday_results) > 0:
                #     # await self.cron.log(f"Found {len(self.yesterday_results)} results found for {self.yesterday}.")
                #     for platform in publish_platfoms:
                #         res = await self.publish_results(self.yesterday_results, platform)
                #         if res == True: # Auto checks if time to publish
                #             _update_platform = True
                #             await self.cron.log(f"Results published to {platform.name}.", type="info")
                #         else:
                #             await self.cron.log(f"Error publishing to platform {platform.name}: {res}")
                #         await asyncio.sleep(1)
                #     await asyncio.sleep(5)
                
                # # Publish Tips
                # if len(self.today_tips) > 0:
                #     # await self.cron.log(f"Found {len(self.yesterday_results)} results found for {self.yesterday}.")
                #     for platform in publish_platfoms:
                #         res = await self.publish_tips(self.today_tips, platform)
                #         if res == True:
                #             # Auto checks if time to publish
                #             _update_platform = True
                #             await self.cron.log(f"Tips published to {platform.name}.", type="info")
                #         else:
                #             # print(res)
                #             await self.cron.log(f"Error publishing to platform {platform.name}: {res}")
                            
                #         await asyncio.sleep(1)
                
                # if _update_platform:
                #     log.debug(f"Publish Schedule: {platform.publish_schedule}")
                #     if not len(platform.publish_schedule.split(" ")) >= 5:
                #         platform.publish_schedule = "30 8 * * *"
                #         log.warning(f"Publish Schedule for {platform.name} is invalid. Setting to default: 30 8 * * *", type="warning")
                #     platform.next_publish = CronManager.next_iter(platform.publish_schedule)
                #     await self.tips_model.update_publish_platform(platform.id, platform.model_dump())

        # Check if we should fix any last tips
        if utc_datetime(self.config_get("fix_tips_next_execution", utc_now() )) <= utc_now():
            await self.fixer_upper()
        
        # Save specific log entries. Not starting or stopping the cron job.
        # await self.cron.log("Some other info.", type="debug")
        
        pass

    @log.catch()
    async def fetch_tips(self, platform:HunchClubPublishPlatform):
            
            # TODO If no data is provided, then fetch it from the database, using filter criteria from the platform
            # platform.tips_days_delta # Days into the future to fetch tips. Use 0 for today only, 1 for today and tomorrow, 2 for today, tomorrow and the next day, etc.
            
            # Assuming readyd check has already been made.
            date = utc_now()
            delta = platform.tips_days_delta
            
            if platform.publish_type == "results": 
                date = utc_now() - timedelta(days=1)
                delta = -delta
            
            if not self.tips_model:
                self.tips_model = Tips(self.config_get('mongodb_url',None), self.config_get('mongodb_database',None))
                
            # Fetch tips
            data = await self.tips_model.fetch_tips( date, delta )
            
            log.info(f"Found {len(data)} {platform.publish_type.capitalize()} for {date.strftime('%Y.%m.%d')} and {platform.tips_days_delta} days into the {'past' if platform.publish_type == 'results' else 'future'}.")
            
            if data:
            
                # platform.tips_filter # (list) Filter criteria to fetch tips. tips_filter_options: list = ["unspecified","free","premium"] - multi select options
                filtered_data = []
                
                for tip in data:
                    tip = TipSchema(**tip)
                    if not platform.tips_filter: continue
                    log.debug(platform.tips_filter)
                    log.debug(tip)
                    # log.debug(tip.publish_free)
                    # log.debug(tip.publish_vip)
                    if tip.publish_free and "free" in platform.tips_filter:
                        filtered_data.append(tip)
                        continue
                    if tip.publish_vip and "premium" in platform.tips_filter:
                        filtered_data.append(tip)
                        continue
                    if "unspecified" in platform.tips_filter and not tip.publish_free and not tip.publish_vip:
                        filtered_data.append(tip)
            
                log.info(f"Filtered {len(data)} {platform.publish_type.capitalize()} for {platform.tips_filter} and found {len(filtered_data)} items.")
                
                return filtered_data
            
            return None


    async def fixer_upper(self):
        """
        This method is called by the cron job at the interval defined in the module's config.
        """
        fixed = []
        
        log.debug("Running fixer_upper")
        
        async with MongoDB().url(self.config_get('mongodb_url',None)).connect() as mongo:
            # Set database and collection together
            # mongo.database("test").collection("tests")
            mongo.database( self.config_get('mongodb_database',None)).collection("daily_tips")
            
            # Paginate results
            pageSize = 100
            last_id = None
            max_page = 0
            i = 0
            _search_by_date = {}
            if self.config_get('fix_tips_from_last_date', None):
                #datetime().utcnow() - timedelta(days=1)   
                _search_by_date = {
                    'datetime': {
                        '$gt': self.config_get('fix_tips_from_last_date')
                    }
                }
            
            while True:
                i+=1
                if max_page>0 and i > max_page:
                    # print("Hit max page")
                    break
                
                if last_id:
                    results = await mongo.get_collection().find({
                        '_id': {
                            '$gt': last_id
                        }, 
                        **_include_date
                    }).limit(pageSize).to_list(None)
                elif _search_by_date:
                    results = await mongo.get_collection().find({
                        **_search_by_date
                    }).limit(pageSize).to_list(None)
                else:
                    results = await mongo.get_collection().find().limit(pageSize).to_list(None)
                
                print("PAGE", i, "RESULTS", len(results))
                await asyncio.sleep(2)
                
                if not results:
                    break
                
                last_id = results[-1]['_id']
                _include_date = {} # remove date filter after initial search

                for res in results:
                    _to_update = False
                    # print(res)
                    if not isinstance(res['datetime'], datetime):
                        res['datetime'] = datetime.strptime(res['datetime'], "%Y-%m-%dT%H:%M:%S")
                        res['description'] = res['description'].strip("\n").strip()
                        _to_update = True
                        
                    if res['description'].endswith("\n"):
                        res['description'] = res['description'].strip("\n()").strip()
                        _to_update = True
                        
                    if _to_update:
                        # print("UPDATING", res)
                        update = await mongo.update( res['_id'], res)
                        # print(update)
                        fixed.append(res)
                        await asyncio.sleep(1)
            
        if fixed:
            await self.cron.log(f"FIXER_UPPER: Fixed {len(fixed)} rows")
        
        log.debug(f"Fix Tips Schedule: {self.config_get('fix_tips_schedule','<none>')}")
        # Set last date to today
        await self.config_set('fix_tips_from_last_date', utc_now())
        await self.config_set('fix_tips_next_execution', CronManager.next_iter(self.config_get('fix_tips_schedule', "0 0 * * *")))
        
        log.debug("Setting 'fix_tips_from_last_date' to " +  str(utc_now()))
        log.debug("Setting 'fix_tips_next_execution' to " +  str(CronManager.next_iter(self.config_get('fix_tips_schedule', "0 0 * * *"))))

    @log.catch()
    async def publish_tips(self, tips, platform, force=False):
        """
        Publishes tips to platform.
        """
        
        if not self.publish_model:
            self.publish_model = PublishTips( )
            
        try:
            if isinstance(platform, dict):
                platform = HunchClubPublishPlatform(**platform)
                
                            
            if await self.publish_model.publish(data=tips, platform=platform, force=force):
                
                log.info("Tips published successfully.")
                return True
            
            else:
                return "Error publishing tips. See module logs."
        
        except Exception as e:
            # log.error(e)
            return str(e)
        
        return False
    
    async def publish_results(self, tips, platform, force=False):
        """
        Publishes results to platform.
        """
        log.warning("publish_results is DEPRECATED. Please use publish_tips instead.")
        return await self.publish_tips(tips, platform, force)