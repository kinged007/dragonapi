# from beanie import Document
from mongoengine import Document, StringField, DateTimeField, BooleanField, ListField
from utils.datetime import datetime, utc_now
from typing import Optional

class CronExecutor(Document):
    module = StringField(required=True)
    last_executed = DateTimeField(default=utc_now)
    next_execution = DateTimeField(default=utc_now)
    active = BooleanField(default=True)
    log = ListField(default=list)

    meta = {
        'collection': 'cron_executor'
    }
