from fastapi import APIRouter, Query, Request, Depends
# from fastapi.responses import JSONResponse
from os import path
# import json
# from loguru import logger as log
# import asyncio
# from pydantic import BaseModel
from enum import Enum
from gpt_researcher import GPTResearcher
# from rich import print

from auth.api_key import verify_permissions # Accepts Enum object (eg. Permissions.read), string (eg. "read"), or list (eg. [Permissions.read, Permissions.write])
from modules.researcher.config import Config

router = APIRouter(dependencies=[Depends(verify_permissions(Config.Permissions.ai))])

data_folder = path.join(path.dirname(__file__), 'data') # TODO fix to ./data/{module_name}

# print(data_folder, path.dirname(__file__))

class ReportType(Enum):
    research_report = "research_report"
    outline_report = "outline_report"
    
@router.get('/report/{report_type}')
async def get_report(request: Request, query: str = Query(), report_type: ReportType = ReportType.research_report):
    
    config = Config()
    print("[purple] >>> CONFIG", config.get("ModuleName"), config.get("Permissions"), config.get("CronInterval"), config.get("CronActive"))
    
    
    # report = asyncio.run(GPTResearcher(query, report_type).run())
    # return {"data":query} #report
    return config.__dict__

