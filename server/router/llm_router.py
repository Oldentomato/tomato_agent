from util import ThreadGenerator
from fastapi import APIRouter, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src import LangchainChatBot
import threading

llm_route = APIRouter()


def chat_streaming(query):
    g = ThreadGenerator()
    llm = LangchainChatBot(g)
    threading.Thread(target=llm.chat, args=(query,)).start()
    return g



@llm_route.post("/chat")
async def chat(query: str = Form(...)):
    return StreamingResponse(chat_streaming(query=query), media_type='text/event-stream')


