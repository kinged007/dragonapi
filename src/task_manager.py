### Redis Queue Manager
from typing import Any, Dict
from beanie import init_beanie
from beanie.odm.documents import Document
from datetime import datetime, timezone
from pymongo import MongoClient
import asyncio
from os import getenv
from loguru import logger as log

from tables.task import Task
from vars import USING_DOCKER

# NOTE: Maybe migrate to RQ instead of handling this ourselves? RQ does not support async functions though...
# https://python-rq.org/
# Redis Queue
from rq import Queue
from redis import Redis

if USING_DOCKER: # Use the Redis container
    redis_conn = Redis(host="rq_redis")
else:
    redis_conn = Redis(host=getenv('REDIS_HOST', 'localhost'), port=getenv('REDIS_PORT', 6379), db=0, password=getenv('REDIS_PASSWORD', None))

_is_async = True if getenv('REDIS_RQ_ASYNC', 'false').lower() == 'true' else False
if _is_async:
    task_manager = Queue('task_manager', connection=redis_conn)
else:
    task_manager = Queue('task_manager', is_async=False)

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
class TaskManager:
    @staticmethod
    def enqueue(func, *args, **kwargs):
        """
        Enqueue a function to be processed by the RQ worker.

        :param func: The function to be enqueued.
        :param args: Arguments to pass to the function.
        :param kwargs: Keyword arguments to pass to the function.
        :return: Job instance representing the enqueued job.
        """
        job = task_manager.enqueue(func, *args, **kwargs)
        return job
