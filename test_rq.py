import os
from redis import Redis
from rq import Queue
from test_tasks import test_func_one, test_func_two, test_func_three
from rq.job import Job
import time

from dotenv import load_dotenv
load_dotenv()

# Load environment variables for Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

# Establish a connection to the Redis server
redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

# Define the queue by the given name
queue = Queue('task_manager', connection=redis_conn)

# Enqueue the functions to the Redis queue
queue.enqueue(test_func_one)
queue.enqueue(test_func_two, 'example_arg')
queue.enqueue(test_func_three, 'first_arg', 'second_arg')

# Store job instances to check their status later
job1 = queue.enqueue(test_func_one)
job2 = queue.enqueue(test_func_two, 'example_arg')
job3 = queue.enqueue(test_func_three, 'first_arg', 'second_arg')

# Wait for the jobs to finish with a maximum execution time of 30 seconds
start_time = time.time()
max_execution_time = 30
while True:
    if (time.time() - start_time) > max_execution_time:
        print("Maximum execution time reached. Exiting.")
        break
    if all(job.is_finished for job in [job1, job2, job3]):
        print("All jobs have been completed.")
        break
    time.sleep(0.1)  # Sleep for a short interval to avoid busy waiting

# Report the final status of each job
for job in [job1, job2, job3]:
    print(f"Job {job.id} finished with result: {job.result} and status: {job.get_status()}")

# Print a message to indicate that the functions have been enqueued
print("Test functions have been enqueued to 'task_manager'.")
