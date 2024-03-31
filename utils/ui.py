


def remove_ui_params(dict_obj:dict):
    """
    Remove UI parameters from a dictionary object.
    """
    return {k: v for k, v in dict_obj.items() if not any([k.endswith(suffix) for suffix in ["_field", "_options", "_help","_disabled","_repeatable","_required","_placeholder","_type"]])}