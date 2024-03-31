from schema.basemodule import BaseModuleConfig, ConfigField
from typing import Optional
from .schema import LiteLlm

class Config(BaseModuleConfig):
    
    # TODO This string is saved in the database. It should not be saved because it is a field of notice_X. Use a config dict where additional fields and what is saved in the database can be defined. OR.... use a Type to define what is saved and what is not. eg..
    # module_name: DatabaseField[str] = "LLM"
    # field_config: dict = {
    #    "module_name": ConfigFieldConfig(type=ConfigField.string, help="..."),
    # }
    
    notice_info: str = "You can use the following URL as an OpenAI API Base URL: https://XXXXXXXX"
    notice_info_field: ConfigField = ConfigField.notice_info
    
    # module_active:bool = True
    # cron_interval:int = 5 # minutes
    # cron_active:bool = True
    # cron_schedule:str = "*/13 * * * *" # Default to every 15 minutes
    
    
    # TODO LLM Model - compatible with LiteLLM
    # TODO LLM Model API Key - compatible with LiteLLM
    # test_model: LiteLlm = LiteLlm()
    chat_model: list = []
    chat_model_field: str = "multiselect"
    chat_model_help: str = "The first selected option will be the primary model. All models selected afterwards will act as backup models in case the primary model fails."
    chat_model_options: list = [
        "openai/gpt-4-0125-preview",
        "openai/gpt-4-turbo-preview",
        "openai/gpt-4-1106-preview",
        "openai/gpt-4-1106-vision-preview",
        "openai/gpt-4-vision-preview",
        "openai/gpt-4",
        "openai/gpt-4-32k",
        "openai/gpt-3.5-turbo-0125",
        "openai/gpt-3.5-turbo",
        "openai/gpt-3.5-turbo-1106",
        "openai/gpt-3.5-turbo-instruct",
        
        "mistral/mistral-tiny",
        "mistral/mistral-small",
        "mistral/mistral-medium",
        "mistral/mistral-large-latest",
        
        "anthropic/claude-3-opus-20240229",
        "anthropic/claude-3-sonnet-20240229",
        "anthropic/claude-3-haiku-20240307",
        "anthropic/claude-2",
        "anthropic/claude-2.1",
        "anthropic/claude-instant-1.2",
        
        "gemini/gemini-pro",
        "gemini/gemini-1.5-pro",
        "gemini/gemini-pro-vision",
        "gemini/gemini-1.5-pro-vision",
        
        "groq/llama2-70b-4096",
        "groq/mixtral-8x7b-32768",
        "groq/gemma-7b-it",
    ]
    
    embedding_model: list = []
    embedding_model_field: str = "multiselect"
    embedding_model_options: list = [
        "openai/text-embedding-ada-002",
        "huggingface/microsoft/codebert-base",
        "huggingface/BAAI/bge-large-zh",
        "huggingface/hf-embedding-model",
        "mistral/mistral-embed", 
    ]
    
    image_generation: list = []
    image_generation_field: str = "multiselect"
    image_generation_options: list = [
        "openai/dall-e-3",
        "openai/dall-e-2",
    ]
    
    # TODO Transcribe options and TTS options
    # TODO Allow for custom models for Replicate + huggingface for different usage types (chat, image, etc.)
    
    # https://docs.litellm.ai/docs/observability/athina_integration
    athina: dict = {
        "api_key": "",
        # "api_key_help": "Monitor LLM Logs at https://app.athina.ai/ and get your API key from the settings page."
    }
    # athina_api_key: str = "" # Deprecated
    athina_help: str = "Monitor LLM Logs at https://app.athina.ai/ and get your API key from the settings page."
    
    
    # Default LLM options
    llm_defaults: dict = {
        'temperature': 0.7,
        'max_tokens': 1000,
        'top_p': 1.0,
        'frequency_penalty': 0.0,
        'presence_penalty': 0.0,
        # 'stop': None,
        'n': 1,
    }
    llm_defaults_help: str = "Default settings for the LLM models. Setting 'max_tokens' to 0 will disable the token limit."
    
    # API Keys
    openai: dict = {
        "api_key": "",
        "api_base": "https://api.openai.com/v1",
        "organization": "",
    }
    gemini: dict = {
        "api_key": "",
    }
    mistral: dict = {
        "api_key": "",
    }
    anthropic: dict = {
        "api_key": "",
    }
    huggingface: dict = {
        "api_key": "",
        "api_base": "",
    }
    groq: dict = {
        "api_key": "",
    }
    replicate: dict = {
        "api_key": "",
    }
    azure: dict = {
        "api_key": "",
        "api_base": "",
        "api_version": "",
        "ad_token": "",
        "api_type": "",
    }
