from langchain.tools import tool
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from app.schemas.pomodoro import PomodoroCreate
from datetime import datetime
import requests

class AgentPomodoroInput(BaseModel):
    timer: float = Field(..., gt=0, le=720, description="Work time in minutes"),
    rest_time: float | None = Field(None, description="Rest duration in minutes (default: half of work time)")
    task_name: str | None = Field(None, max_length=50, description="Task description for the pomodoro")

def pomodoro_to_db_schema(agent_input: AgentPomodoroInput) -> PomodoroCreate:
    return PomodoroCreate(
        timer=agent_input.timer,
        rest_time=agent_input.rest_time or agent_input.timer / 2,
        task_name=agent_input.task_name or "Focus Time",
        start_time=datetime.now()
    )

@tool
def create_pomodoro_tool(params: dict, token: str = None) -> str:
    '''Create a pomodoro with parameters: timer (required in minutes), rest_time (optional), and task_name (optional). 
    Always require explicit time duration. Example inputs:
    - "25 minute pomodoro for coding"
    - "Focus session: 50min work, 10min break"  
    ''' 
    if not token:
        return "Error: Authentication token missing"

    # Extract structured data from user prompt
    extraction_prompt =  PromptTemplate("""
        Extract pomodoro parameters from: {input}
        
        Return STRICT JSON with:
        - timer: number (minutes, required)
        - rest_time: number (minutes, required)
        - task_name: string
        - Must follow this format: Action Input: {"key": "value"}
        
        Rules:
        1. Default rest_time = timer/2
        2. If timer not found, return null for all fields
        3. Clean task_name (remove time references)
                                                        
        Examples:
        - "25min math" → {{"timer": 10, "rest_time": 5, "task_name": "math"}}
        - "No time specified" → {{"timer": null, "rest_time": null, "task_name": ""}}
    """)
    
    extraction_chain = (
        extraction_prompt
        | ChatGroq(temperature=0) # Cold model for accurate extraction
        | JsonOutputParser()
    )

    try:
        validated_input = AgentPomodoroInput(**params) 
        extraction = extraction_chain.invoke({"input": validated_input})
        
        if not extraction or extraction.get("timer") is None:
            return "Please provide working time duration"
        
        timer = float(extraction['timer'])
        if timer <= 0:
            return "Please provide a valid working time duration"
        
        rest_time = float(extraction.get('rest_time', timer/2))
        task_name = extraction.get("task_name", "").strip()[:50] # Lenght limit
        
        # Call backend
        response = requests.post(
            "http://localhost:8000/pomodoro/", 
            json={
                "timer": timer,
                "rest_time": rest_time,
                "task_name": task_name
            },
            headers = {"Authorization": f"Bearer {token}"},
            timeout=10
        )

        if response.status_code == 200:
            return f"Pomodoro created:  {timer}min work, {rest_time}min rest | {task_name or 'General'}"
        else:
            return f"Error while creating pomodoro: {response.text[:150]}"
        
    except requests.exceptions.RequestException as e:
        return "Connection error: Couldn't contact server."
    except ValueError as e:
        return "Format error: Times must be numbers."
    except Exception as e:
        return f"Unexpected error: {str(e)[:100]}"