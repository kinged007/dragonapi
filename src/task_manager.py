
### Redis Queue Manager
from typing import Any, Dict
from beanie import init_beanie
from beanie.odm.documents import Document
from datetime import datetime, timezone
from pymongo import MongoClient
import asyncio
from loguru import logger as log

from tables.task import Task

# NOTE: Maybe migrate to RQ instead of handling this ourselves? RQ does not support async functions though...
# https://python-rq.org/


class TaskManager:
    def __init__(self):
        # # Initialize MongoDB connection
        # self.client = MongoClient(mongo_uri)
        # self.db = self.client[db_name]
        # # init_beanie(database=self.db)
        # # Initialize RQ queue
        # self.queue = Queue(connection="redis://default:1xC1TvKg4AXAjJ8gOrz3blEPjFi8Wprc@redis-10440.c3.eu-west-1-2.ec2.cloud.redislabs.com:10440") #Queue(connection=self.client)
        # # Get the tasks collection
        # self.tasks_collection = Job #self.db.tasks
        pass

    def enqueue_task(self, func_name: str, args: Any = None, kwargs: Dict[str, Any] = {}):
        
        # Save task details to MongoDB
        log.debug(f"Enqueuing task: {func_name}")
        task_doc = {
            "func_name": func_name,
            "args": args,
            "kwargs": kwargs,
            "status": "queued",
            "created_at": datetime.utcnow()
        }
        task = Task(**task_doc)
        task.save()
        
        return True

    def fetch_and_execute_tasks(self, num_tasks: int = 5):
        # Fetch num_tasks tasks from MongoDB
        tasks = self.tasks_collection.find({"status": "queued"}).limit(num_tasks)
        async_tasks = [ self.execute_task(task_doc) for task_doc in tasks ]
        # Execute tasks asynchronously
        asyncio.run(asyncio.gather(*async_tasks))

    async def execute_task(self, task_doc: Dict[str, Any]):
        # Execute task
        func_name = task_doc["func_name"]
        args = task_doc.get("args", ())
        kwargs = task_doc.get("kwargs", {})
        # Dynamically import and call the function
        module_name, func_name = func_name.rsplit('.', 1)
        module = __import__(module_name, fromlist=[func_name])
        func = getattr(module, func_name)
        func(*args, **kwargs)
        # Update task status in MongoDB
        await self.tasks_collection.update_one({"_id": task_doc["_id"]}, {"$set": {"status": "completed"}})

