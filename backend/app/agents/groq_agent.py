import os
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.schema.runnable import RunnableParallel, RunnablePassthrough

load_dotenv()
llm = ChatGroq(
    api_key=os.getenv('GROQ_API_KEY'),
    model="openai/gpt-oss-120b",
    temperature=0.6,
    max_retries=3,
    timeout=None,
)

# Tools
# Pomodoro tools
# Start a pomodoro
@tool
def create_pomodoro_tool(params: dict) -> str:
    '''Create a pomodoro for user on backend '''
    user_input = params.get("input", "")
    token = params.get("token", "")

    if not token:
        return "Error: Authentication token missing"

    # Extract structured data from user prompt
    data_extraction =  PromptTemplate.from_template("""
         Extract pomodoro parameters from this input: {input}
        Return ONLY JSON with these keys:
        - timer: number (in minutes, required)
        - rest_time: number (in minutes, optional)
        - task_name: string (optional)
        
        Rules:
        1. If rest_time missing, calculate as half of timer
        2. If timer missing, return null
        3. Keep task_name empty if not specified
                                                        
        Example outputs:
        Good input: "25min work on math" -> {{"timer": 30, "rest_time": 15, "task_name": "Math lessons"}}
        Bad input: "Start pomodoro:" -> {{"timer": null, "rest_time": null, task_name: ""}}
    """)
    
    extraction_chain = (
        RunnableParallel({"input": RunnablePassthrough})
        | data_extraction
        | JsonOutputParser
    )

    try:
        extraction = extraction_chain.invoke(user_input)
        
        # Call backend
        if not extraction.get("timer"):
            return "Please provide working rime duration"
        
        timer = float(extraction['timer'])
        rest_time = float(extraction.get('rest_time', timer/2))
        task_name = extraction.get("task_name", "")

        response = requests.post(
            "http://localhost:8000/pomodoro/", 
            json={
                "timer": timer,
                "rest_time": rest_time,
                "task_name": task_name
            },
            headers = {"Authorization": f"Bearer {token}"}
        )

        if response.status_code == 200:
            return f"👍🏼 Pomodoro created:  {timer}min work, {rest_time}min rest | {task_name or 'Unnamed'}"
        else:
            return f"Error while creating pomodoro: {response.text}"
    except Exception as e:
        return f"Error while creating pomodoro: {str(e)}"

tools = [create_pomodoro_tool]

# Agent initial prompt #! When adding more tools, this prompt has to change.
initial_prompt_template = """You are Cronos, an agent who has acces to the following tools:

{tools}

The available tools are: {tool_names}

After you use a tool, an observation will be provided to you:
'''
Observation: Result of the tool
'''

You will use a thought-action-observation cycle until you have enough information to respond to the user's request directly.
When you have the final answer, respond in this format:
'''
Thought: I know the answer
Final answer: The final answer to the original query.
'''

IMPORTANT:
- If you DO NOT need tools, answer EXACTLY like this:
'''
Thought: I do not need to use tools
Final Answer: [your response directly here]
'''

- If you need tools, use the standard format thought-action-observation.

Let's start:
Question: {input}
{agent_scratchpad}
"""

initial_prompt = PromptTemplate.from_template(initial_prompt_template, partial_variables={"tool_names": ", ".join([t.name for t in tools])})

agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=initial_prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=1, #! Change to 2 when agent works well
    early_stopping_method="generate" # Force generate response even if reaches iteration threshold
)

def process_user_message(msg: str, token: str) -> str:
    return agent_executor.invoke({"input": msg, "token": token})["output"]
#for chunk in llm.stream(messages): # ? "stream" AI response
    #print(chunk.text(), end="")