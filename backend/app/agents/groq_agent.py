import os
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate
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
    data_extraction =  ChatPromptTemplate.from_template("""
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

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent='zero-shot-react-description',
    verbose=True
)

def process_user_message(msg: str, token: str) -> str:
    return agent.invoke({"input": msg, "token": token})["output"]
#for chunk in llm.stream(messages): # ? "stream" AI response
    #print(chunk.text(), end="")