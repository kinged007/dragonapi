from beanie import Document
from utils.datetime import datetime, utc_now
from typing import Optional

class CronExecutor(Document):
    
    module: str
    last_executed: Optional[datetime] = utc_now()
    next_execution: Optional[datetime] = utc_now()
    # interval: int = 5 # minutes
    active: bool = True
    log: list = []
    
    class Settings:
        name = "cron_executor"
