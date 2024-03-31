from loguru import logger as log
from typing import List, Optional, Union 
import litellm
from litellm import Router
from litellm.utils import trim_messages

# Import the module's schema
from vars import DEBUG, ENVIRONMENT
from utils.ui import remove_ui_params

def chat_completion(self,
    model: str = None,
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
    # set api_base, api_version, api_key
    # model_list: Optional[list] = None,  # pass in a list of api_base,keys, etc.
    # Optional liteLLM function params
    fallbacks: Optional[List] = None,
    metadata: Optional[dict] = None,
    **kwargs,
):
    log.warning("LLM Completion")
    
    # Store variables into a dict
    params = {
        "model": model, 
        "messages": messages,
        "timeout": timeout,
        "temperature": temperature,
        "top_p": top_p,
        "n": n,
        "stream": stream,
        "stop": stop,
        "max_tokens": max_tokens,
        "presence_penalty": presence_penalty,
        "frequency_penalty": frequency_penalty,
        "logit_bias": logit_bias,
        "user": user,
        "response_format": response_format,
        "seed": seed,
        "tools": tools,
        "tool_choice": tool_choice,
        "logprobs": logprobs,
        "top_logprobs": top_logprobs,
        "deployment_id": deployment_id,
        "fallbacks": fallbacks,

    }
    print(self, self.config_get("chat_model", []))
    # Get config default models
    if model is None:
        use_models = self.config_get("chat_model", [])
        if not use_models:
            raise Exception("No model selected.")
        model = use_models
    # Use models as list
    if isinstance(model, str):
        model = [model]
    # Set primary model
    params['model'] = model.pop(0)
    # Set fallbacks
    params['fallbacks'] = model
    
    # Merge metadata
    """
    Following are the allowed fields in metadata, their types, and their descriptions:

        environment: Optional[str] - Environment your app is running in (ex: production, staging, etc). This is useful for segmenting inference calls by environment.
        prompt_slug: Optional[str] - Identifier for the prompt used for inference. This is useful for segmenting inference calls by prompt.
        customer_id: Optional[str] - This is your customer ID. This is useful for segmenting inference calls by customer.
        customer_user_id: Optional[str] - This is the end user ID. This is useful for segmenting inference calls by the end user.
        session_id: Optional[str] - is the session or conversation ID. This is used for grouping different inferences into a conversation or chain. [Read more].(https://docs.athina.ai/logging/grouping_inferences)
        external_reference_id: Optional[str] - This is useful if you want to associate your own internal identifier with the inference logged to Athina.
        context: Optional[Union[dict, str]] - This is the context used as information for the prompt. For RAG applications, this is the "retrieved" data. You may log context as a string or as an object (dictionary).
        expected_response: Optional[str] - This is the reference response to compare against for evaluation purposes. This is useful for segmenting inference calls by expected response.
        user_query: Optional[str] - This is the user's query. For conversational applications, this is the user's last message.

    """
    if not metadata: metadata = {}
    metadata = {
        "environment": ENVIRONMENT,
        # "customer_id": "", # DragonAPI API Key from user who made request
        **metadata,
    }
    if user and not metadata.get('customer_user_id', None):
        metadata['customer_user_id'] = user
    if not metadata.get('user_query', None):
        # Get last message
        metadata['user_query'] = messages[-1].get('content', "")
    params['metadata'] = metadata
    
    # Set LLM defaults if not set.
    defaults = remove_ui_params(self.config_get("llm_defaults", {}))
    for k, v in defaults.items():
        if params.get(k, None) is None:
            params[k] = v
                    
    # Trim messages so max_tokens/model limit is not reached
    if params['max_tokens'] and params['max_tokens'] > 0:
        params['messages'] = trim_messages(messages, max_tokens=params['max_tokens'])
    else:
        params['messages'] = trim_messages(messages, params['model'])
        
        
    if DEBUG:
        litellm.set_verbose=True
    else:
        # set callbacks if not debug mode.
        litellm.success_callback = ["athina"] # log input/output to Athina platform
    
    # Drop unsupported params for different LLM's
    litellm.drop_params=True
    
    try: 
        # TODO implement model_list: https://docs.litellm.ai/docs/completion/multiple_deployments#quick-start
        # then we can implement Router for caching and retries
        # ... https://docs.litellm.ai/docs/routing#caching
        # router = Router(model_list=model_list)
        log.debug(params)
        log.debug(kwargs)
        response = litellm.completion(
            **params,
            # model_list=[], # pass in a list of api_base,keys, etc.
            **kwargs
        )
        log.debug(response)
        return response
    except Exception as e:
        print("[red]ERROR", e)



# TODO create async completion similiar to the above, async def acompletion()...
