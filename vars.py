from os import path, getenv

BASE_DIR = path.dirname(path.abspath(__file__))
DEBUG = True if str(getenv("DEBUG","false")).lower() == "true" else False
LOGGING_LEVEL = "DEBUG" if DEBUG else getenv("LOGGING_LEVEL", "INFO").upper()
ENVIRONMENT = getenv("ENVIRONMENT", "development").lower()
APP_VERSION = "0.0.4"
BETTER_STACK_TOKEN = getenv("BETTER_STACK_TOKEN", None)
SENTRY_DSN = getenv("SENTRY_DSN", None)

def log_level(level:str = None):
    """
    Returns log level as numeric value. If no parameter is passed, returns the log level of the LOGGING_LEVEL environment variable.
    """
    _levels = {
        "DEBUG" : 0,
        "INFO" : 1,
        "WARNING" : 2,
        "ERROR" : 3,
    }
    
    if level:
        return _levels.get(level.upper(), 1)
    return _levels.get(LOGGING_LEVEL, 1)