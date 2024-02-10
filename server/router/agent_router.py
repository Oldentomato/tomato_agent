from util import ThreadGenerator
from fastapi import APIRouter,UploadFile,Form
from pydantic import BaseModel
from src import LangAgent
import threading
from fastapi.responses import StreamingResponse

agent_route = APIRouter()


def agent_streaming(query):
    g = ThreadGenerator()
    agent = LangAgent(g)
    threading.Thread(target=agent.run, args=(query,)).start()
    return g

@agent_route.post("/chat")
async def agent(query: str = Form(...)):
    return StreamingResponse(agent_streaming(query), media_type='text/event-stream')
    