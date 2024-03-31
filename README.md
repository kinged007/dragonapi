# API Server

API Server uses MongoDB for settings and some storage, and Directus for data and providing endpoints to interact with.

## Deployment guide

Deployment uses Docker. 

1. Once you have the files on the server, using git or copy and paste, ~~you need to rename `sample.env` to `.env` and set the parameters.~~ You need to set the environment variables in the `docker-compose.yml` file. 
2. Rename `sample.proxies.txt` to `.proxies.txt` and enter your proxies.
3. Run `docker compose up -d` on first run. This will build the docker image, install the required packages and launch the container.
4. To update, after the latest files have been updated, you need to rebuild the image using `docker compose build`, then `docker compose up -d` to launch it. Or you can use `docker-compose up -d --build` to do both actions at once.

You can view the terminal output by using `docker compose logs -f`.

## Documentation
Notes for the development of modules.

### Caching
Caching can be used in the following ways.

```
# Get global cache
from utils.cache import global_cache, SimpleCache
```

The global persistent caching object is defined in `global_cache`. You can create a new caching object using `new_cache = SimpleCache()`

Here are the following ways you can use the cache object:
```
# Directly
global_cache.set(key: str, value: Any, ttl: int = 300, namespace: str = 'default')
global_cache.get(key: str, namespace: str = 'default')

# As decorators
@global_cache.cache(ttl: int, key: Union[Callable[[Any], str], str] = None, namespace: str = 'default')
def sync_function(foo="bar"):
    ...
    
@global_cache.async_cache(ttl=10, key=lambda param: f"test_key_{param}", namespace: str = 'default')
async def async_function(foo="bar"):
    ...

# Clear a cache
global_cache.clear(key: str = None, namespace: str = 'default'):
    
```


