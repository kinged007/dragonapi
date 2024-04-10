from fastapi import APIRouter, Query, Request, Depends, Body
from fastapi.responses import JSONResponse
from loguru import logger as log
from importlib import import_module
from bson import ObjectId
from importlib import import_module, util
from beanie import Document
from os import path
import inspect
from time import time
# from rich import print

# Import module main class
from .. import Module
from ..schema import TokenBearer, PermissionsOptions

# Customized token bearer for direct admin access to this app
access_token_bearer = TokenBearer()

# Import module config
# from modules._template.config import Config
from tables.config import ModuleConfig
from tables.cron import CronExecutor
from tables.api_keys import ApiKeys
from src.configmanager import ConfigManager
config_manager = ConfigManager()

from vars import DEBUG
from models.utils import get_module_folders_list
from models.permissions import list_permissions
from auth.api_key import generate_api_key, verify_permissions

from utils.cache import global_cache

# Load router and define permissions at module level if required.
# Only show in schema is working in DEBUG mode
router = APIRouter( include_in_schema=DEBUG )
module = Module()

@router.get('/queues')
async def get_queues():
    """
    Get a list of all queues.
    """
    queues = [queue.name for queue in queue.connection.queues]
    return JSONResponse(content={"queues": queues})

@router.get('/queues/{queue_name}/jobs')
async def get_jobs(queue_name: str):
    """
    Get a list of jobs in a specific queue.
    """
    rq_queue = queue.connection.get_queue(queue_name)
    jobs = rq_queue.job_ids  # Getting job IDs for demonstration purposes
    return JSONResponse(content={"jobs": jobs})

@router.get('/workers')
async def get_workers():
    """
    Get a list of all workers.
    """
    workers = [worker.name for worker in queue.connection.workers]
    return JSONResponse(content={"workers": workers})

@router.put('/jobs/{job_id}/reschedule')
async def reschedule_job(job_id: str, new_time: int):
    """
    Reschedule a job to a new time.
    """
    job = queue.fetch_job(job_id)
    if job:
        job.reschedule(new_time)
        return JSONResponse(content={"message": "Job rescheduled"})
    else:
        return JSONResponse(content={"message": "Job not found"}, status_code=404)

@router.delete('/jobs/{job_id}')
async def delete_job(job_id: str):
    """
    Delete a job.
    """
    job = queue.fetch_job(job_id)
    if job:
        job.delete()
        return JSONResponse(content={"message": "Job deleted"})
    else:
        return JSONResponse(content={"message": "Job not found"}, status_code=404)

from src.task_manager import TaskManager
queue = TaskManager.queue # gets the rq.Queue object
