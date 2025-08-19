import os
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
import json

load_dotenv()

class PomodoroInput(BaseModel):
    timer: float = Field(..., gt=0, le=1120, description="Work time in minutes"),
    rest_time: float = Field(None, description="Rest duration in minutes (default: half of work time)")
    task_name: str = Field(None, max_length=50, description="Task description for the pomodoro")

prompt_template = """You are Cronos, an expert time management AI assistant. Your role is to recognize and process requests for timed work sessions.
You will process this requests ONLY with the provided tools. 

**Timed session triggers:** 
- Synonyms: Pomodoro/pomodoro, Timer, Focus/focus session, Work session, Productive session/interval, timed session.
- Explicit durations (e.g., "25min", "1 hour")

**When detected:**
1. Extract: 
   - `timer` (required, in minutes)
   - `rest_time` (optional, in minutes)
   - `task_name` (optional)

2. If missing timer duration: DO NOT use tools, respond politely and continue conversation.

**Valid examples:**
- "25min math": {{"timer": 25, "rest_time": 12.5, "task_name": "math"}}
- "50min pomodoro with 10min break": {{"timer": 50, "rest_time": 10, "task_name": ""}}
- "No duration specified": {{"timer": null, "rest_time": null, "task_name": "", "response": "[answer politely.]"}}

**Available tools:**
{tools}
Tool names: {tool_names}

**Critical rules:**
1. **Only use tools when you have a timer duration**
2. **Non-tool response format:**
Thought: I do not need to use tools
Final Answer: [direct response here]

**Tool usage format:**
Thought: [Parameter analysis]
Action: [tool_name]
Action Input: {{"timer": [value], "rest_time": [value|timer/2   ], "task_name": "[text]"}}

**Current interaction**
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
def make_create_pomodoro_tool(token: str):
    @tool
    def create_pomodoro_tool(params: str) -> str:
        '''
        Create a pomodoro timer with parameters: timer (required, in minutes),
        rest_time (optional, in minutes), and task_name (optional). 
        '''
        try:
            # Parse the JSON string
            params_dict = json.loads(params)
            
            # Validate required fields
            timer = params_dict.get('timer')
            if timer is None:
                return "Error: Missing timer duration"
            
            timer = float(timer) * 60.0

            if timer <= 0:
                return "Error: Invalid duration"
                
            rest_time = params_dict.get('rest_time') 
            rest_time = float(rest_time * 60) if rest_time is not None else timer / 2.0
            task_name = params_dict.get('task_name', 'General')[:50]
            
            # Pomodoro endpoint call
            response = requests.post(
                "http://localhost:8000/pomodoro/",
                json={
                    "timer": timer,
                    "rest_time": rest_time,
                    "task_name": task_name
                },
                headers={"Authorization": f"Bearer {token}"},
                timeout=10 
            )
            
            response.raise_for_status()
            data = response.json()
            
            return f"Pomodoro started: {task_name} ({data.get('timer', timer)/60.0} min work, {data.get('rest_time', rest_time)/60.0} min rest)"
        
        except json.JSONDecodeError:
            return "Error: Invalid parameters format"
        except Exception as e:
            return f"Error: {str(e)[:100]}"

    return create_pomodoro_tool

async def process_user_message(msg: str, token: str) -> str:
    tools = [make_create_pomodoro_tool(token)]
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=PromptTemplate(template=prompt_template, input_variables=["input", "agent_scratchpad", "tools", "tool_names"])
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=lambda _: "Oops, something went wrong, please rephrase your question.",
        max_iterations=2,
        early_stopping_method="generate" # Force generate response even if reaches iteration threshold
    )

    result = await agent_executor.ainvoke({"input": msg, "token": token})
    # Ensure answer is text
    if isinstance(result, dict):
        if "output" in result:
            return result["output"]
        else:
            return str(result)
    elif isinstance(result, str):
        return result
    else:
        return str(result)

#for chunk in llm.stream(messages): # ? "stream" AI response
    #print(chunk.text(), end="")