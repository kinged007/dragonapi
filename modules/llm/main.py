# This file houses the main class for the module. It is responsible for handling the module's data and business logic and shared resources
# Acts as a Controller
from loguru import logger as log
from src.basemodule import BaseModuleClass
import requests
from os import path, environ
import json
from typing import List, Optional, Union 
import litellm
from litellm import Router
from litellm.utils import trim_messages

# Import the module's schema
from .schema import OpenAiChatRequestBody, Models
from vars import DEBUG, ENVIRONMENT
from utils.ui import remove_ui_params

from .src.chat import chat_completion

# Import the module's config

# Import the module's database model

# TODO Rename module to LLM and implement LiteLLM with Athina for monitoring and logging
# https://github.com/BerriAI/litellm/tree/main
# https://docs.litellm.ai/docs/observability/athina_integration
# Caching: https://docs.litellm.ai/docs/caching/redis_cache

"""
https://docs.litellm.ai/docs/completion/input

def completion(
    model: str,
    messages: List = [],
    # Optional OpenAI params
    timeout: Optional[Union[float, int]] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    n: Optional[int] = None,
    stream: Optional[bool] = None,
    stop=None,
    max_tokens: Optional[float] = None,
    presence_penalty: Optional[float] = None,
    frequency_penalty: Optional[float] = None,
    logit_bias: Optional[dict] = None,
    user: Optional[str] = None,
    # openai v1.0+ new params
    response_format: Optional[dict] = None,
    seed: Optional[int] = None,
    tools: Optional[List] = None,
    tool_choice: Optional[str] = None,
    logprobs: Optional[bool] = None,
    top_logprobs: Optional[int] = None,
    deployment_id=None,
    # soon to be deprecated params by OpenAI
    functions: Optional[List] = None,
    function_call: Optional[str] = None,
    # set api_base, api_version, api_key
    base_url: Optional[str] = None,
    api_version: Optional[str] = None,
    api_key: Optional[str] = None,
    model_list: Optional[list] = None,  # pass in a list of api_base,keys, etc.
    # Optional liteLLM function params
    **kwargs,

) -> ModelResponse:


"""

class Module(BaseModuleClass):
    
    model: str = None
    timeout: str = None
    temperature: str = None
    top_p: str = None
    n: str = None
    presence_penalty: str = None
    frequency_penalty: str = None
    logit_bias: str = None
    base_url: str = None
    api_key: str = None
    
    async def init(self):
        # Initialized after config has been loaded.
        
        # Load API Keys into environment
        environ["ATHINA_API_KEY"] = self.config_get("athina", {}).get("api_key", "")

        # Compatible providers
        providers = ['openai', 'anthropic', 'groq', 'gemini', 'mistral', 'huggingface', 'replicate', 'athina']
        
        # Save API keys to environment
        for p in providers:
            c = self.config_get(p, {})
            if c:
                for k, v in c.items():
                    if v: 
                        environ[f"{p.upper()}_{k.upper()}"] = v
                        log.debug("Set environment variable: "+f"{p.upper()}_{k.upper()}")
        
        
    
    # config is autoloaded from the database, using config.py as a base.
    # module config is callable from self.config_get(key,fallback) or self.config_set(key,value)
    # global config is callable from self.global_config(key,fallback)
    
    # Correct permission format is: "module_name.permission_name"
    # callable via self.permission("permission_name")
    
    def completion(self, *args, **kwargs):
        return chat_completion(self, *args, **kwargs)
    
    # async def completion(self, body: OpenAiChatRequestBody, simple_response: bool = True):
        
    #     # log.debug("OpenAI Router")
    #     log.debug(f"Using OpenAI Model: {body.model}")
        
    #     self.api_key = self.config_get("openai_api_key", "")
    #     self.base_url = self.config_get("openai_base_url", "")
    #     # print(openai_api_key, openai_base_url)
    #     if not self.api_key:
    #         raise  Exception("OpenAI API key not set.")
        
    #     url = f"{self.base_url.strip('/')}/chat/completions"
    #     headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
    #     data = {key:value for key, value in body.model_dump(exclude_unset=True).items() if value is not None}
        
    #     try:
            
    #         response = requests.post(url, headers=headers, data=json.dumps(data)).json()
    #         if 'error' in response:
    #             return f"ERROR: {response.get('error',{}).get('message','(unknown)')}" if simple_response else response
            
    #         log.info("OpenAI Usage: "+str(response.get("usage",{})))
            
    #         # TODO Count usage and costs
    #         """<class 'requests.models.Response'> {'id': 'chatcmpl-8hcmPU3uVYZyyjK4iYvY7ivPZ8MPk', 'object': 'chat.completion', 'created': 1705407865, 'model': 'gpt-3.5-turbo-0613', 'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': 'Hello! How can I assist you today?'}, 'logprobs': None, 'finish_reason': 'stop'}], 'usage': {'prompt_tokens': 8, 'completion_tokens': 9, 'total_tokens': 17}, 'system_fingerprint': None}"""
            
    #         # return choices
    #         if response.get("choices", None):
    #             return response.get("choices",[])[0].get("message", {}).get("content","") if simple_response else response
            
    #     except Exception as e:
    #         log.error(e)
    #         return {"error":str(e)}
        
    #     # Something went wrong
    #     return None