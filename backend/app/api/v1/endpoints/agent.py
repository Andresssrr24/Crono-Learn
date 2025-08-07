from fastapi import APIRouter, Header, HTTPException
from app.agents.groq_agent import PromptInput, agent
from pydantic import BaseModel

router = APIRouter()

class PromptInput(BaseModel):
    prompt: str

@router.post("/")
async def agent_endpoint(prompt_input: PromptInput, authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    token = authorization.split(" ")[1]

    try:
        ans = agent.run(prompt_input.prompt)
        return ans  
    except Exception as e:
        return {"error": str(e)}