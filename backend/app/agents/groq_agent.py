import os
import json
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent
from langchain.tools.requests.tool import RequestsGetTool, RequestsPostTool, RequestsDeleteTool
from langchain.tools import tool

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv('GROQ_API_KEY'),
    model="openai/gpt-oss-120b",
    temperature=0.3,
    max_retries=3,
    timeout=None,
)

# Tools
# Pomodoro tools
# Start a pomodoro
@tool
def create_pomodoro(input: dict) -> str:
    '''Create a pomodoro. Expected input:
    {
        'timer': 10,
        'rest_time': 5,
        'task_name': "math lesson"m
        'token': "user_token"
    }
    '''
    try:
        timer = input['timer']
        rest_time = input['rest_time']
        task_name = input['task_name']
        token = input['token']
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        payload = {
            "timer" : timer,
            "rest_time": rest_time,
            "task_name": task_name
        }
        response = requests.post("http://localhost:8000/pomodoro/", json=payload, headers=headers)
        response.raise_for_status()
        return f"👍🏼 Pomodoro created: {response.json()}"
    except Exception as e:
        return f"😔Error while creating pomodoro: {str(e)}"

tools = [create_pomodoro]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent='zero-shot-react-description',
    verbose=True
)

def process_user_message(msg: str, token: str) -> str:
    return agent.invoke({"prompt": msg, "token": token})
#for chunk in llm.stream(messages): # ? "stream" AI response
    #print(chunk.text(), end="")