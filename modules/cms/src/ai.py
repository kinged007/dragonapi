import json
import asyncio 
from loguru import logger as log

from modules.openai import router as openai
from modules.openai.config import OpenAiChatRequestBody, Models
from modules.cms.config import Config

# Project Assistant
async def project_assistant(project_text: str, additional_instructions:str = ""):
    """
    Project Assistant
    """
    # Get system prompt and parameters from config
    config = Config()
    prompt_template = config.get("ProjectAiPrompt")
    # find and replace variables in template in format {variable}
    prompt_template = prompt_template.replace("{project_details}",project_text.strip())
    if additional_instructions:
        prompt_template += "\nAdditional instructions: "+additional_instructions
    prompt_template += """\nGive me the valid JSON object with the values in a single Markdown string, correctly formatting line breaks and other charachters into Unicode. 
Please ensure you use the following JSON structure. Use the level 1 keys provdided, but change the values to your own. Remember to use Markdown format for the values.
``` 
{
    "name": "Write a short and effective title for this project",
    "description": "Write a short and effective description for this project which outlines the phases and milestones",
    "objectives:": "Write short and effective objectives for the project.\nThese should be **SMART** objectives.",
    "execution_strategy": "Write a short and effective execution strategy for this project as well as explain how you will manage and prioritize the backlog of tasks",
    "tasks": { # This is a dictionary detailing the milestones and tasks
        "Title for your own Milestone 1": [
            "Details of task number 1",
            "Tasks should be short single line text, but detailed.",
            "Details of task number 3",
            ...
        ],
        "Title for the next milestone 2": [
            ...
        ],
        ...
    },
    "risk_management_plan": "A detailed outline of identified risks and mitigation strategies",
    "resources": "A detailed outline of resources required to execute this project.\nUse lists",
    "performance_metrics": "A detailed outline of performance metrics to be used to measure the success of this project",
    "quality_assurance": "A detailed outline of quality assurance methods to be used to ensure the quality of this project",
    "budget" : "A detailed breakdown of budget and costs for this project",
    "communication_plan": "Outline how the team will communicate, including daily stand-ups, sprint reviews, and sprint retrospectives.",
    "key_stakeholders" : "A place to list key stakeholders and their roles in the project, with detail how you will keep stakeholders engaged and informed throughout the project.",
}
```
You will reply with only the project plan as instructed. You will not engage with conversation. Please remember to use correctly formatted Markdown for the values, with line breaks and lists.
"""
    # Prepare openai model
    # Run openai completion
    attempts = 3
    
    request_obj = OpenAiChatRequestBody(
        messages=[
            {"role": "system", "content": config.get("ProjectAiSystemPrompt")},
            {"role": "user", "content": prompt_template}
        ],
        model=config.get("ProjectAiModel", "gpt-3.5-turbo"),
        temperature=config.get("ProjectAiTemp", 0.7),
    )
        
    completion = await openai.completion( request_obj )
    
    if 'error' in completion.lower():
        return completion
    
    # try jsonify it
    while attempts > 0:
        if attempts <= 0: 
            log.error("Failed to read AI response in well formatted JSON.")
            return {"error":"Failed to read AI response in well formatted JSON."}

        try:
            # Return result
            # strip string from start to first { and from last } to end
            completion = completion[completion.find("{"):completion.rfind("}")+1]
            result = json.loads(completion)
            log.debug(f"Successfully jsonifyed AI response after {3-attempts} attempts.")
            return result

        except Exception as e:
            # could not jsonify it, try again.
            await asyncio.sleep(1)
            log.debug("Failed to read AI response in well formatted JSON. Trying again.")
            print("DEBUG>>>", type(completion),repr(completion))
            print("ERROR", str(e))
            log.debug(completion)
            completion = await openai.completion( OpenAiChatRequestBody(
                messages=[
                    # {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "The following is invalid JSON. When trying to json.loads() the text, it threw this error: '"+str(e)+"'. Please try again to return only valid JSON. Do not write anything else except the valid JSON string and ensuring all line breaks are correctly presented. ```"+completion+"```. Please try again to return only valid JSON. Do not write anything else except the valid JSON string and maintain the structure."}
                ],
                model=config.get("ProjectAiModel", "gpt-3.5-turbo"),
                temperature=config.get("ProjectAiTemp", 0.5),
            ) )
            attempts -= 1
            continue
            
    return None