from util import ThreadGenerator
from fastapi import APIRouter,UploadFile,Form
from pydantic import BaseModel
from src import LangAgent
import threading
from fastapi.responses import StreamingResponse

agent_route = APIRouter()
agent = LangAgent()

def agent_streaming(query):
    g = ThreadGenerator()
    threading.Thread(target=agent.run, args=(g,query)).start()
    return g

@agnet_route.post("/agent")
async def agent(query: str = Form(...)):
    return StreamingResponse(agent_streaming(query,), media_type='text/event-stream')
    