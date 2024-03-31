# Authentication and Authorization module

Designed to simply handle all authentication protocols (Login, Passwordless login, SAML, OAuth, SSO, etc.) and all authorization checks (API Key, Admin Token, JWT Token, etc.)

See: https://fastapi.tiangolo.com/tutorial/security/

Module will make use of a single class object that will contain the methods to conduct the various checks. 


## Considerations
- Use 'scopes' instead of/in conjunction with Permissions ?
- User, like API_KEY, will contain allowed permissions list.


## Structure

We use `@staticmethod` decorator so we do not need to initialize the object. We can call the methods directly.

```
class Auth:
    
    @staticmethod
    def user(permission: str = None, token: Annotated[str, Header() ]):
        # Verify user is logged in by decoding 
        #   the token and checking permissions. 
        # If user exists (not None), verify user 
        #   is active and permissions are correct.
        # Allow { 'user_id' : None, ... } ??
        ...
    
    @staticmethod
    def api_key(permission: str, token: Annotated[str, Header() ]):
        # Verify API Key or Admin Token is being used. 
        # Then verify the correct permission requirements 
        ...
    
    # Utils
    def get_bearer_token():
        ...
    
    
        
```


## Usage examples

### API Key
`Auth.api_key()` will check the api key for the correct permissions as well as the Admin Token, which has universal access.
```
@router.get('/collection/items', dependencies=[Depends( Auth.api_key( permission= Module.permission.read ))])
```

### JWT Token
JWT Tokens are used to verify the user and is used by most login methods.
```
# No permission requirements still require the user to be logged in.
@router.get('/users/me', dependencies=[Depends( Auth.user( ) )])

# Defining permissions, require that the user be logged in and have the correct permission
@router.get('/users/me', dependencies=[Depends( Auth.user( Module.permission.read ) )])
```

### Requiring Multiple permissions
All permissions must be met before it will proceed.
```
@router.get('/users/{id}/update', dependencies=[
    Depends( Auth.user( Module.permission.read ) ), 
    Depends( Auth.user( Module.permission.admin ) )
])
```

### User requiring ANY of the specified permissions
```
@router.get('/items/{item_id}', dependencies=[Depends( 
    Auth.any( 
        Auth.user( Module.permission.read ), 
        Auth.user( Module.permission.super )
    )
)])
```

### User requiring specific permissions for module item
Gets url from Header to check for permissions
```
@router.get('/items/{item_id}', dependencies=[Depends( 
    Auth.any( 
        ...
        Auth.user( Module.permission.item() ) 
    )
)])
```