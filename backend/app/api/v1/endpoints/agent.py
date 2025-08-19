from fastapi import APIRouter, Header, HTTPException
from app.agents.pomodoro_agent import process_user_message
from pydantic import BaseModel

router = APIRouter()

class PromptInput(BaseModel):
    prompt: str

@router.post("/")
async def agent_endpoint(data: PromptInput, authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    token = authorization.split(" ")[1]

    try:
        ans = await process_user_message(data.prompt, token)

        if ans is None or ans == "":
            return {"output": "Sorry, I couldn't generate an answer in this moment"}
        
        return {"output": ans}  
    except Exception as e:
        return {"output": f'An error ocurred whille processing your message: {str(e)}'}