from models.utils import log_time
from time import sleep
from asyncio import sleep as async_sleep
from models.cron import BaseCronManager

class CronManager(BaseCronManager):

    async def run(self):
        
        print("RESEARCHER = Running Cron Job")
        # Run cron jobs here.
    