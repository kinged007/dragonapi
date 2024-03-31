import asyncio
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from vars import LOGGING_LEVEL

# Initialize MongoDB client
# client = AsyncIOMotorClient('mongodb://localhost:27017')
# db = client['log_database']
# collection = db['log_collection']

class DatabaseHandler:
    @staticmethod
    def write(msg):
        # await collection.insert_one({"message": msg})
        print("LOGGING:", msg)
        # print(type(msg['record']), str(msg['record'].__dict__))
        pass

    def __call__(self, message):
        # asyncio.create_task(self.write(message["record"]["message"]))
        self.write(message)

# Remove default handler
logger.remove()
# Add custom handler
logger.add(DatabaseHandler(), level=LOGGING_LEVEL)