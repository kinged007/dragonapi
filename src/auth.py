# TODO Authentication class
# Used with FastAPI 'depends' parameter to authenticate users using API Token, App password, or JWT.
# TODO make this a singleton class? 
# TODO add type hints
# TODO add logging
# TODO add error handling

# from pydantic import BaseModel


class Authentication:
    """
    Authentication class
    """
    pass
    # def __init__(self, db: Database, log: Logger, jwt: JWT, api_key: ApiKey, app_password: AppPassword, jwt_secret: str, jwt_algorithm: str, jwt_expires: int):
    
    # get_bearer_token(self, request: Request, verify:list|str = ['api_key','pass','jwt']) -> str: # verify is a list in order of priority
    
    # verify_jwt(self, token: str) -> bool:
    
    # verify_api_key(self, api_key: str) -> bool:
    
    # verify_app_password(self, app_password: str) -> bool:
    
    # create_jwt(self, data: dict, expires: int = 3600) -> str: