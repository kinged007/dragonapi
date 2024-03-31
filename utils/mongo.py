from bson import ObjectId
from mongoengine import Document


def mongo_to_dict(obj):
    if isinstance(obj, str):
        return obj

    return_data = []

    if isinstance(obj, Document):
        return_data.append(("id", str(obj.id)))
    
    for field_name in obj:
        if field_name == "id":
            continue

        data = obj[field_name]

        if isinstance(data, ObjectId):
            return_data.append((field_name, str(data)))
        elif isinstance(data, list):
            return_data.append((field_name, [mongo_to_dict(item) for item in data]))
        elif isinstance(data, dict):
            return_data.append((field_name, mongo_to_dict(data)))
        else:
            return_data.append((field_name, data))

    return dict(return_data)