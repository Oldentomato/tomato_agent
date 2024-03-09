from util import ThreadGenerator
from fastapi import APIRouter,UploadFile,Form,Depends
from pydantic import BaseModel
from src import LangAgent
import threading
from fastapi.responses import StreamingResponse

agent_route = APIRouter()


def get_lang_agent(g: ThreadGenerator = Depends(), chat_id: str = Form(...)):
    return LangAgent(g, chat_id)

def agent_streaming(query, agent, g, chatroom_url):
    threading.Thread(target=agent.run, args=(query,chatroom_url)).start()
    return g

@agent_route.post("/chat")
async def agent(query: str = Form(...), chatroom_url: str = Form(...), agent: LangAgent = Depends(get_lang_agent), g: ThreadGenerator = Depends()):
    return StreamingResponse(agent_streaming(query, agent, g, chatroom_url), media_type='text/event-stream')

@agent_route.post("/createchat")
async def create_chat(query: str = Form(...), token: str = Form(...)):
    return StreamingResponse(agent_streaming(query, _agent, _g), media_type='text/event-stream')
    