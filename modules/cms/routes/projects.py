from fastapi import APIRouter, Query, Request, Depends
# from fastapi.responses import JSONResponse
# from loguru import logger as log
from os import path
from enum import Enum
from loguru import logger as log
# from rich import print

# Import Permission checking function
# Accepts Enum object (eg. Permissions.read), string (eg. "read"), or list (eg. [Permissions.read, Permissions.write])
from auth.api_key import verify_permissions 

# Import app models
from models.utils import html_to_markdown, markdown_to_html, markdownify

# Import self module config
from modules.cms import Config
from modules.cms.src.directus import Directus
from modules.cms.src import ai


router = APIRouter()

# Project Manager endpoints
@router.get('/ai_assistant/{project_id}', dependencies=[Depends(verify_permissions(Config.permission('write')))])
async def project_ai_assistant(request: Request, project_id: str, additional_instructions: str = Query(default=""), create_tasks: bool = Query(default="")):
    """
    AI Assistant for Project related tasks
    """
    if not project_id:
        return {"error":"No project ID provided."}
    
    directus = Directus()
    
    # 1. TODO Try to get project object from database
    project = directus.fetch_project(project_id)
    
    # 2. If exists, process AI assistant sequence
    if not project:
        return {"error":"Project Not Found."}

    if project:
        if project.get("error", None):
            log.error(project.get("error"))
            return {"error":project.get("error")}
        if 'data' in project: project = project.get("data")
        
        print(project)
        # print(project.get("name", ""), project.get("description", ""))
        
        
        if not project.get("name", "") or not project.get("description", ""):
            return {"error":"Project name and description are required."}
            
        log.debug("Project exists. Running AI assistant sequence.")
        
        additional_instructions = additional_instructions if additional_instructions and additional_instructions.lower() != 'undefined' else None
        create_tasks = True if str(create_tasks).lower() == 'true' else False
        
        project_text = f"""Project Name: {project.get("name", "")}
Project Start Date: {project.get("start_date", "")}
Project End Date: {project.get("end_date", "")}
Project Lead: { (", ".join([f"{directus.user_name(user)}" for user in project.get("project_lead", []) ])) }
Project Users Involved: { (", ".join([f"{directus.user_name(user)}" for user in project.get("users_involved", [])])) }
Project Department: { (", ".join([department.get('department_id', {}).get('name', '') for department in project.get("department", []) if department.get('department_id', {}).get('name', '')])) if project.get("department", []) else "" }
Project Resources: {html_to_markdown(project.get("resources", ""))}
Project Description: {html_to_markdown(project.get("description", ""))}        
Project Objectives: {html_to_markdown(project.get("project_objectives", ""))}
Project Execution Strategy: {html_to_markdown(project.get("execution_strategy", ""))}
Project Risk Management Plan: {html_to_markdown(project.get("risk_management_plan", ""))}
Project Performance Metrics: {html_to_markdown(project.get("performance_metrics", ""))}
Project Quality Assurance: {html_to_markdown(project.get("quality_assurance", ""))}
Project Budget: {html_to_markdown(project.get("budget", ""))}
Project Communication Plan: {html_to_markdown(project.get("communication_plan", ""))}
Project Key Stakeholders: {html_to_markdown(project.get("key_stakeholders", ""))}
Project Tasks and Milestones: {html_to_markdown(project.get("milestones", ""))}
        """
        
        # Now we send this to the AI Assistant model
        ai_assistant = await ai.project_assistant(project_text, additional_instructions)
        
        # print(project_text)
        print(type(ai_assistant), ai_assistant)
        
        # 3. Save project object to database
        if ai_assistant and 'error' not in ai_assistant:
            # valid response
            """ Expecting a response object like this:
            {
                "name": "Write a short and effective title for this project",
                "description": "Write a short and effective description for this project which outlines the phases and milestones",
                "project_objectives:": "Write short and effective objectives for the project. These should be SMART objectives.",
                "execution_strategy": "Write a short and effective execution strategy for this project as well as explain how you will manage and prioritize the backlog of tasks",
                "milestones": "A detailed outline of the key milestones for this project, with some direction on the tasks required.",
                "tasks": {
                    "Use your own Milestone 1 Title": [
                        "Details of task number 1",
                        "Tasks should be short single line text, but detailed.",
                        "Details of task number 3",
                        ...
                    ],
                    "Use your own Milestone 2 Title": [
                        ...
                    ],
                    ...
                },
                "risk_management_plan": "A detailed outline of identified risks and mitigation strategies",
                "resources": "A detailed outline of resources required to execute this project",
                "performance_metrics": "A detailed outline of performance metrics to be used to measure the success of this project",
                "quality_assurance": "A detailed outline of quality assurance methods to be used to ensure the quality of this project",
                "budget" : "A detailed breakdown of budget and costs for this project",
                "communication_plan": "Outline how the team will communicate, including daily stand-ups, sprint reviews, and sprint retrospectives.",
                "key_stakeholders" : "A place to list key stakeholders and their roles in the project, with detail how you will keep stakeholders engaged and informed throughout the project.",
            }
            """
            save_to_directus = {}
            # convert text to markdown
            for key, value in ai_assistant.items():
                if value:
                    
                    print(key)
                    _k = key
                    
                    if _k not in project.keys():
                        log.warning(f"Key not found in project object: {_k}")

                    if key in ["tasks"]:
                        _k = "milestones" 
                    
                    _old_content = project.get(_k,"") if project.get(_k,"") else ""
                    
                    # Skip tasks
                    if _k in ["tasks","name"]:
                        # TODO Create tasks and subtasks if create_tasks is True
                        continue
                        
                    value = markdownify(value)
                    save_to_directus[_k] = str(_old_content) + "<br/><code>- - - - - - - - - - - AI Assistant - - - - - - - - - - -</code><br/>" + markdown_to_html(value).strip()
                    
            # Add tasks to milestones section
            # ai_assistant["milestones"] = str(_old_content) + "<br/><code>- - - - - - - - - - - AI Assistant - - - - - - - - - - -</code><br/>" + markdown_to_html(markdownify(ai_assistant["tasks"])).strip()
            
            print(save_to_directus)
            update = directus.update_project(project_id, save_to_directus)
            print(update)
            
            if 'data' in update:
                return {"data":"Project updated successfully."}
            
            
    
    # 4. Return
    
    return {"data":"Something went wrong."}