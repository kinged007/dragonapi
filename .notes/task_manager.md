# Task Manager

Class object that handles the queuing of tasks and executing them. Tasks may be enqueued asyncrounously and syncronsouly. 
Task executions are maintained in a log, which via the admin UI may be re-executed at the click of a button.
We are trying to recreate RQ without the need for Redis.

## Notes for Improvements
- Tasks must be saved in Mongo, which currently must be done asyncrounsouly - change to PyMongo instead of beanie/motor
- TaskManager should be a single instance only
- TaskManager should manage the queue, executing ONLY the number of tasks according to configurations, no matter how many times check_execute function is called.
- Potentially use decorator method to register the task function, so we can call it later.
- Look at https://python-rq.org/ for inspiration.
- In general, it's a good practice to make your RQ tasks self-contained and independent of global state to avoid issues with missing context or dependencies when the tasks are executed. If a task needs data from your FastAPI application, consider passing that data as arguments to the task function.


## Structure

```
class TaskManager:
    
    def enqueue(self, func, args, kwargs)
    
    async def aenqueue(self,func, args, kwargs)
    
    async check_and_execute(self, num_tasks)
    
    async def execute_task(self, task_doc: Dict[str, Any]):
        # Dynamically call the function
        # use asyncio or not appropriately for async and non-async functions
```

## Use cases

#### Enqueue task

```
from utils.task_manager import task_manager


async def long_running_task(param1, param2):
    ...
    
@router.post('/do-long-task')
async def do_long_task(param1, body):
    ...
    task = await task_manager.enqueue('long_running_task', paran1, body)
    # OR
    task = task_manager.enqueue('long_running_task', paran1, body)
    # task.id contains row id. 
    ...
    
```