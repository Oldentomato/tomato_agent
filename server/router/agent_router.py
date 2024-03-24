from util import ThreadGenerator
from fastapi import APIRouter,UploadFile,Form,Depends
from pydantic import BaseModel
from src import LangAgent
import threading
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from fastapi.responses import StreamingResponse
import json
from langchain.schema import messages_from_dict

agent_route = APIRouter()


def get_lang_agent(g: ThreadGenerator = Depends()):
    return LangAgent(g)

def agent_streaming(query, agent, g, history_url):
    #None일 경우 새로만들어주는 로직을 추가하고 아래 명령들을 실행할 것
    threading.Thread(target=agent.run, args=(query,history_url)).start()
    return g

#채팅방 누르는 순간에 호출
#여기에 memory변수 할당하는 부분까지 쓰게하자 (get_chat_history())
@agent_route.post("/getchat")
async def get_chat(chatroom_url: str = Form(...)):
    try:
        with open(chatroom_url) as f:
            retreive_from_db = json.load(f)
        retrieved_messages = messages_from_dict(retreive_from_db)
        retrieved_chat_history = ChatMessageHistory(messages=retrieved_messages)
    except Exception as e:
        return {'success': False, 'message': e}

    return {'success':True, 'item':retrieved_chat_history}


@agent_route.post("/chat")
async def agent(query: str = Form(...), history_url: str = Form(...), agent: LangAgent = Depends(get_lang_agent), g: ThreadGenerator = Depends()):
    return StreamingResponse(agent_streaming(query, agent, g, history_url), media_type='text/event-stream')

# @agent_route.post("/createchat")
# async def create_chat(query: str = Form(...), token: str = Form(...)):
#     pass
    