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
from rq.decorators import job as rq_job

class TaskManager:
    

    @staticmethod
    def job(queue_name, *args, **kwargs):
        """
        Decorator that adds a function to the specified RQ queue.
        This replicates the @job decorator from RQ, but uses the predefined connection.

        :param queue_name: The name of the queue.
        :param args: Additional arguments for the decorator.
        :param kwargs: Additional keyword arguments for the decorator.
        :return: Decorated function.
        """
        def decorator(func):
            return rq_job(queue_name, connection=task_manager.connection, *args, **kwargs)(func)
        return decorator

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
