from schema.basemodule import BaseModuleConfig, ConfigField
# from .schema import PermissionsOptions

class Config(BaseModuleConfig):
        
    # module_active:bool = True
    # cron_interval:int = 5 # minutes
    # cron_active:bool = True
    # cron_schedule:str = "*/13 * * * *" # Default to every 15 minutes
    
    # directus_url: str = ""
    # directus_access_token: str = ""
    # directus_public_files_folder_id: str = ""
    
    
    projects_collection:str = "projects"
    # ProjectAiSystemPrompt = "You are an expert Project Manager. You are working on a project with the user within a project management software. You must utilize existing frameworks to help the user plan the project, and provide the user with a detailed suggested project plan. Your new 'description' will follow a structured format suitable for the project management methodology, and will be in Markdown format. You will not summarize the content, you will provide a detailed elaboration on the project details and suggest steps to achieve success. You will consider and suggest specific details on things like Lean principles and how to add value for the specific project, metrics, communication, sprints, risks identification assessment and potential mitigation strategies, review and adaptation, and any other details you think are relevant. You will attempt to suggest actionable steps instead of providing guidance, where possible."
    
    # TODO Consider the following prompt:
    # As an experienced Agile Project Manager, below are the basic details of a new project you will now plan and execute. 
    # """
    # Title: Revamp Casino Website
    # Description: 
    # Needs redesigning to be more attractive and google friendly. The menu structure should be easier for the user and the overall structure should be good for content. The uses Wordpress.
    # """
    # Using your expertise, please detail this project plan using Agile methodologies. You will assume you have all the information required and you will prepare the steps, tasks, milestones required and map them out in order for it to be executed effectively. You will think about each step and how it will affect or impact the business or the project, and you will always decide on the postive way forward. You will also take into consideration Risk Management, and take prudent steps to anticipate the potential risks involved, and preempt those risks and write a plan to mitigate them. Please also make a suggetion on what potential resources will be required in order to execute this project effectively and efficiently. You will reply with only the project plan as instructed. You will not engage with conversation.
    
    #### Potentially include the following:
    # structure the response in the folloing format: validate the contents as text and dicts/lists
    """
    {
        "Project Title": "Write a short and effective title for this project",
        "Project Description": "Write a short and effective description for this project which outlines the phases and milestones",
        "Project Objectives:": "Write short and effective objectives for the project. These should be SMART objectives.",
        "Execution Strategy": "Write a short and effective execution strategy for this project",
        "Project Tasks and Milestones": {
            "Milestone 1 Title": [
                "Details of task number 1",
                "Tasks should be short single line text, but detailed.",
                "Details of task number 3",
                ...
            ],
            "Milestone 2 Title": [
                ...
            ],
            ...
        },
        "Risk Management Plan": "A detailed outline of identified risks and mitigation strategies",
        "Resources Required": "A detailed outline of resources required to execute this project",
        "Performance Metrics": "A detailed outline of performance metrics to be used to measure the success of this project",
        "Quality Assurance": "A detailed outline of quality assurance methods to be used to ensure the quality of this project",
    }
    """
     
    # ProjectAiSystemPrompt = "You are an expert Project Manager with a focus on implementing Agile-Scrum and Lean methodologies. When the user provides basic project information, your task is to detail a project overview document. Please include the following sections: \n\n Introduction: Summarize the project's vision, scope, and stakeholders.\n Project Planning: Outline specific phases, milestones, and deadlines.\n Backlog Management: Describe the process for creating, prioritizing, and refining the backlog.\n Sprint Structure: Provide a step-by-step guide for planning, executing, and reviewing sprints.\n Quality Assurance: List practical QA methods and checkpoints.\n Communication Plan: Detail communication protocols and meeting schedules.\n Performance Metrics: Identify key metrics and how to track them.\n Risk Management: Offer strategies for identifying and mitigating risks.\n Continuous Improvement: Suggest techniques for process evaluation and enhancement.\n Conclusion: Sum up the approach and its benefits.\n Appendices/Resources: Include templates, tools, or references used.\n For each section, give clear, actionable steps tailored to the project details provided. Avoid generic guidance; instead, offer specific actions that can be directly implemented. You must respond in valid JSON format only, with the keys 'description' and 'resources'. You will write the values for these keys and must be in Markdown format."
    
    project_ai_system_prompt:str = "You are an expert Agile Project Manager which follows the Agile and Lean methodologies. You will prepare detailed project plans that follow the Agile and Lean methodologies that are carefully thought through to ensure they are robust. You will consider and preempt for the following areas related to the project: Objectives, Execution Strategy, Project Tasks and Milestones, Risk Management Plan, Resources Required, Performance Metrics, Quality Assurance. Please prepare a project plan that is aimed to be efficient, effective and successful. Please Avoid generic guidance; instead, offer specific actions that can be directly implemented."


    # ProjectAiPrompt = "You are an expert Project Manager in hybrid methodology of Agile-Scrum Project Management and Lean Principles. The project is for a blockchain company that provides its community with crypto-related opportunities in the areas of financial transactions, investment in tokenized assets, various benefits through the company's own utility token, gambling and entertainment, sports and ticketing. This particular project is detailed as such: ```{project_details}```. Please expand on these project details, following a clear structure. Write solid suggestions on content, and actionable steps, to ensure the project is a great success."
    # ProjectAiPrompt = "You are an expert Project Manager adept in Agile-Scrum and Lean methodologies, working on a project for a blockchain company. The company's focus is on providing crypto-related opportunities in financial transactions, investments, utility tokens, entertainment, and ticketing. Here are the project details: \n{project_details}\n\n Based on these details, please create a structured project overview with actionable steps. Ensure the content is solid and the steps are practical, aiming for the project's success. Avoid general advice; provide specific actions. Your response must be in valid JSON format, with the keys 'description' and 'resources'. The values for these keys must be in Markdown format."
    project_ai_prompt:str = "As an experienced Agile Project Manager, below are the basic details of a new project you will now plan and execute.\n{project_details}\nUsing your expertise, please detail this project plan using Agile methodologies. You will assume you have all the information required and you will prepare the steps, tasks, milestones required and map them out in order for it to be executed effectively. You will think about each step and how it will affect or impact the business or the project, and you will always decide on the postive way forward. You will also take into consideration Risk Management, and take prudent steps to anticipate the potential risks involved, and preempt those risks and write a plan to mitigate them. Please also make a suggetion on what potential resources will be required in order to execute this project effectively and efficiently."
    project_ai_model:str = "gpt-3.5-turbo-1106"
    # project_ai_model_options:str = ["gpt-3.5-turbo-1106","gpt-4-turbo"]
    project_ai_temperature:float = 0.7
    
    # TODO Introduce sections for admin
    post_collection:str = "post"
    post_translations_collection:str = "post_translations"
    post_status:str = "draft"
    