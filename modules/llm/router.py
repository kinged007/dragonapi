from fastapi import APIRouter, Query, Request, Depends, Body
from fastapi.responses import JSONResponse
from loguru import logger as log
from vars import DEBUG

# Import Permission checking function
# Accepts Enum object (eg. Permissions.read), string (eg. "read"), or list (eg. [Permissions.read, Permissions.write])
from auth.api_key import verify_permissions 

# Import app models
from .main import Module

# Schema
from .schema import PermissionsOptions

# Load router and define permissions at module level if required.
router = APIRouter()

# TODO Prepare endpoints to act as a OpenAI API proxy
# https://docs.litellm.ai/docs/providers/custom_openai_proxy#required-endpoints

@router.post('/chat/completions', dependencies=[Depends(verify_permissions(Module.permission(PermissionsOptions.chat)))])
async def chat_completions(request: Request, body: dict = Body(...)):
    """
    Chat Completions, OpenAI Proxy
    """
    return JSONResponse(content={"message": "Chat Completions."})

@router.post('/embeddings', dependencies=[Depends(verify_permissions(Module.permission(PermissionsOptions.chat)))])
async def embeddings(request: Request, body: dict = Body(...)):
    """
    Embeddings, OpenAI Proxy
    """
    return JSONResponse(content={"message": "Embeddings."})

@router.get('/models')
async def models(request: Request):
    """
    Models, OpenAI Proxy
    """
    return JSONResponse(content={"message": "Models."})

if DEBUG:
    @router.get('/test-llm', tags=["Debug"])
    async def test_module(request: Request, message:str = Query(None)):
        
        module = Module()
        
        if not message: message = "Hello"
        
        log.debug( module.temp_module_config )
        try:
            
            chat = [
                    {
                        "role": "system",
                        "content": "Hello! How can I assist you today?"
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            
            
            response = module.completion(
                messages=chat, 
                # mock_response="Mocked response.",
                metadata={
                    "prompt_slug": "test-llm",
                },
                # temperature=0.2,
            )
            
            print(chat)
            # jsonify response
            # print(response.__annotations__)
            # return JSONResponse(content={"message": { k:str(response.__dict__[k]) for k in response.__annotations__.keys() if not k.startswith("_") }})
            
            
        except Exception as e:
            log.error(f"Error: {e}")
            return JSONResponse(status_code=500, content={"error": str(e)})
        
        return JSONResponse(content={"message": "Test successful."})