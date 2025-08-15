import os
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.schema.runnable import RunnableParallel, RunnablePassthrough
from pydantic import BaseModel, Field
import json

load_dotenv()

class PomodoroInput(BaseModel):
    timer: float = Field(..., gt=0, le=1120, description="Work time in minutes"),
    rest_time: float = Field(None, description="Rest duration in minutes (default: half of work time)")
    task_name: str = Field(None, max_length=50, description="Task description for the pomodoro")

# Dual response prompt template
prompt_template = """You are Cronos, an expert time management AI assistant. Your role is to recognize and process requests for timed work sessions. 

**Timed session triggers:** 
- Synonyms: Pomodoro, Timer, Focus/focus session, Work session, Productive session/interval
- Explicit durations (e.g., "25min", "1 hour")

**When detected:**
1. Extract: 
   - `timer` (required, in minutes)
   - `rest_time` (optional, in minutes)
   - `task_name` (optional)
2. If missing core duration: DO NOT use tools, respond politely and continue conversation.

**Valid examples:**
- "25min math": {{"timer": 25, "rest_time": null, "task_name": "math"}}
- "50min Pomodoro with 10min break": {{"timer": 50, "rest_time": 10, "task_name": ""}}
- "No duration specified": {{"timer": null, "rest_time": null, "task_name": "", "response": "[answer politely.]"}}

**Available tools:**
{tools}
Tool names: {tool_names}

**Critical rules:**
1. **Only use tools when you have a numeric `timer`**
2. **Non-tool response format:**
Thought: I do not need to use tools
Final Answer: [direct response here]

**Tool usage format:**
Thought: [Parameter analysis]
Action: [tool_name]
Action Input: {{"timer": [value], "rest_time": [value|null], "task_name": "[text]"}}

**Current interaction**
Let's start:
Question: {input}
Thought: {agent_scratchpad}
"""

llm = ChatGroq(
    api_key=os.getenv('GROQ_API_KEY'),
    model="openai/gpt-oss-120b",
    temperature=0.4,
    max_retries=3,
    timeout=None,
)

# Tools
# Pomodoro tools
# Start a pomodoro
@tool
def create_pomodoro_tool(params: str) -> str:
    '''Create a pomodoro timer with parameters: timer (required in minutes), rest_time (optional), and task_name (optional).
    Always require explicit time duration. Example inputs:
    - "25 minute pomodoro for coding"
    - "Focus session: 50min work, 10min break"  
    '''
    try:
        # Parse the JSON string
        params_dict = json.loads(params)
        
        # Validate required fields
        timer = float(params_dict['timer'])
        if timer <= 0:
            return "Error: Invalid duration"
            
        rest_time = float(params_dict.get('rest_time', timer/2)) 
        task_name = params_dict.get('task_name', '')[:50]
        
        # Pomodoro endpoint call
        response = requests.post(
            "http://localhost:8000/pomodoro/",
            json={
                "timer": timer,
                "rest_time": rest_time,
                "task_name": task_name
            },
            headers={"Authorization": f"Bearer {'user_token'}"},
            timeout=10
        )
        
        return f"Created: {timer}min work, {rest_time}min break | {task_name or 'General'}"
    
    except json.JSONDecodeError:
        return "Error: Invalid parameters format"
    except KeyError:
        return "Error: Missing work_duration"
    except Exception as e:
        return f"Error: {str(e)[:100]}"

tools = [create_pomodoro_tool]

output_parser = JsonOutputParser()

agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=PromptTemplate.from_template(prompt_template)
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,#lambda _: "Oops, something went wrong, please rephrase your question.",
    max_iterations=2,
    #early_stopping_method="generate" # Force generate response even if reaches iteration threshold
)

def process_user_message(msg: str, token: str) -> str:
    return agent_executor.invoke({"input": msg, "token": token})["output"]

#for chunk in llm.stream(messages): # ? "stream" AI response
    #print(chunk.text(), end="")