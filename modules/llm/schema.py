from enum import Enum
from typing import List, Optional, Union, Dict
from pydantic import BaseModel, Field
    

class PermissionsOptions(Enum):
    
    # read: str = "read"
    write: str = "write"
    chat: str = "chat"

class LiteLlm(BaseModel):
    model: str = "gpt-3.5-turbo-1106"
    # frequency_penalty: Optional[float] = Field(0, ge=-2.0, le=2.0)
    # function_call: Optional[Union[str, Dict[str, str]]] = None
    # functions: Optional[List[str]] = None
    # logit_bias: Optional[Dict[str, float]] = None
    # max_tokens: Optional[int] = None
    # n: Optional[int] = Field(1, ge=1)
    # presence_penalty: Optional[float] = Field(0, ge=-2.0, le=2.0)
    # stop: Optional[Union[str, List[str]]] = None
    # stream: Optional[bool] = False
    # temperature: Optional[float] = Field(0.7, ge=0, le=2)
    # top_p: Optional[float] = Field(1, ge=0, le=1)
    # user: Optional[str] = None

## TODO DEPRECATE

# Updated 16-01-2024
class Models:
        
    TOKEN_COSTS = { # Per 1000 tokens!!
        "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002},
        "gpt-3.5-turbo-0301": {"prompt": 0.0015, "completion": 0.002},
        "gpt-3.5-turbo-0613": {"prompt": 0.0015, "completion": 0.002},
        "gpt-3.5-turbo-16k": {"prompt": 0.003, "completion": 0.004},
        "gpt-3.5-turbo-16k-0613": {"prompt": 0.003, "completion": 0.004},
        "gpt-3.5-turbo-1106": {"prompt": 0.001, "completion": 0.002},
        "gpt-4-0314": {"prompt": 0.03, "completion": 0.06},
        "gpt-4": {"prompt": 0.03, "completion": 0.06},
        "gpt-4-32k": {"prompt": 0.06, "completion": 0.12},
        "gpt-4-32k-0314": {"prompt": 0.06, "completion": 0.12},
        "gpt-4-0613": {"prompt": 0.06, "completion": 0.12},
        "gpt-4-1106-preview": {"prompt": 0.01, "completion": 0.03},
        "text-embedding-ada-002": {"prompt": 0.0004, "completion": 0.0},
    }
    TOKEN_MAX = {
        "gpt-3.5-turbo": 4096,
        "gpt-3.5-turbo-0301": 4096,
        "gpt-3.5-turbo-0613": 4096,
        "gpt-3.5-turbo-1106": 16385,
        "gpt-3.5-turbo-16k": 16384,
        "gpt-3.5-turbo-16k-0613": 16384,
        "gpt-4-0314": 8192,
        "gpt-4": 8192,
        "gpt-4-32k": 32768,
        "gpt-4-32k-0314": 32768,
        "gpt-4-0613": 8192,
        "gpt-4-1106-preview": 128000,
        "text-embedding-ada-002": 8192,
    }
    
    def list_models(self):
        return list(self.TOKEN_COSTS.keys())
    def get_token_cost(self, model):
        return self.TOKEN_COSTS.get(model, None)
    def get_token_max(self, model):
        return self.TOKEN_MAX.get(model, None)

class Message(BaseModel):
    role: str
    content: str
    name: Optional[str] = None
    
class OpenAiChatRequestBody(BaseModel):
    messages: List[Message]
    model: str = "gpt-3.5-turbo-1106"
    frequency_penalty: Optional[float] = Field(0, ge=-2.0, le=2.0)
    function_call: Optional[Union[str, Dict[str, str]]] = None
    functions: Optional[List[str]] = None
    logit_bias: Optional[Dict[str, float]] = None
    max_tokens: Optional[int] = None
    n: Optional[int] = Field(1, ge=1)
    presence_penalty: Optional[float] = Field(0, ge=-2.0, le=2.0)
    stop: Optional[Union[str, List[str]]] = None
    stream: Optional[bool] = False
    temperature: Optional[float] = Field(0.7, ge=0, le=2)
    top_p: Optional[float] = Field(1, ge=0, le=1)
    user: Optional[str] = None
    
    
    
    
    