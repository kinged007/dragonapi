import time
from typing import Dict

import jwt, os

# from config.config import Settings


def token_response(token: str):
    return {
        "access_token": token
    }


SECRET_KEY = os.environ['SECRET_KEY']


def sign_jwt(user_id: str) -> Dict[str, str]:
    # Set the expiry time.
    payload = {
        'user_id': user_id,
        'expires': time.time() + (60*60*24) # 1 day expiry
    }
    return token_response(jwt.encode(payload, SECRET_KEY, algorithm="HS256"))


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token.encode(), SECRET_KEY, algorithms=["HS256"])
        return decoded_token if decoded_token['expires'] >= time.time() else {}
    except:
        pass
    return {}
