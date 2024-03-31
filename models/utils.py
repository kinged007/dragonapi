# from utils.datetime import datetime, timezone
from os import path, listdir
from vars import BASE_DIR
from utils.datetime import utc_now

def to_snake_case(snake_case_string:str):
    words = snake_case_string.split('_')
    return ' '.join(word.capitalize() for word in words)

def log_time():
    # UTC Time
    return utc_now().strftime("%Y-%m-%d %H:%M:%S")

def merge_dicts(d1, d2):
    for key in d2:
        if key in d1 and isinstance(d1[key], dict) and isinstance(d2[key], dict):
            merge_dicts(d1[key], d2[key])
        else:
            d1[key] = d2[key]
            
            
def filter_dict(data, filter_substrings, exclude=True):
    if isinstance(filter_substrings, str):
        filter_substrings = [filter_substrings]

    new_dict = {}
    for key, value in data.items():
        if any(substring in key for substring in filter_substrings):
            match = True
        else:
            match = False
            
            
        if (exclude and not match) or (not exclude and match):
            if isinstance(value, dict):
                new_dict[key] = filter_dict(value, filter_substrings, exclude)
            else:
                new_dict[key] = value
        elif not exclude and isinstance(value, dict):
            new_dict[key] = filter_dict(value, filter_substrings, exclude)
            
    return new_dict

        
def get_module_folders_generator():
    """
    Generator to get all module folders in the modules directory.
    Yields the full path and the name of the module.
    """
    modules_folder = path.join(BASE_DIR, 'modules')

    module_folders = [f for f in listdir(modules_folder) if path.isdir(path.join(modules_folder, f)) and not f.startswith('_') and not f.startswith('.')]

    for module_folder in module_folders:
        if not all([path.exists(path.join(modules_folder, module_folder, p)) for p in ['config.py', 'main.py', 'router.py']]):
            continue
        
        yield path.join(modules_folder, module_folder), module_folder

def get_module_folders_list():
    """
    Returns a list of all module folders in the modules directory.
    Each item in the list is a tuple containing the full path and the name of the module.
    """
    return list(get_module_folders_generator())