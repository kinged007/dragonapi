import os
from redis import Redis
from rq import Queue

# Load environment variables for Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

# Establish a connection to the Redis server
redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

# Define the queue by the given name
queue = Queue('task_manager', connection=redis_conn)

# Define a few test functions to enqueue
def test_func_one():
    print("Test function one is running.")

def test_func_two(arg):
    print(f"Test function two received argument: {arg}")

def test_func_three(arg1, arg2):
    print(f"Test function three received arguments: {arg1} and {arg2}")

# Enqueue the functions to the Redis queue
queue.enqueue(test_func_one)
queue.enqueue(test_func_two, 'example_arg')
queue.enqueue(test_func_three, 'first_arg', 'second_arg')

# Print a message to indicate that the functions have been enqueued
print("Test functions have been enqueued to 'task_manager'.")
