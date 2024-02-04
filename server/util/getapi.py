from dotenv import load_dotenv
import os 
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler

class MyStreamingCallback(BaseCallbackHandler):
    def __init__(self, g):
        self.content = ""
        self.final_answer = False
        self.g = g

    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.content += token
        self.g.send(token)
        if "." in token:
            self.content += '\n'
            self.g.send('\n')
        if "final_answer" in self.content:
            self.final_answer = True 
            self.content = ""
        if self.final_answer:
            print(token)
            agent.callbacks = MyStreamingCallback()

    def on_llm_end(self, response, **kwargs) -> None:
        self.g.close()

load_dotenv(verbose=True)

def get_google_search():
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    search = GoogleSearchAPIWrapper(google_api_key=GOOGLE_API_KEY)
    return search

def get_openai_model(g):
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    return ChatOpenAI(model_name="gpt-3.5-turbo",openai_api_key=OPENAI_API_KEY, streaming=True,
                        callbacks=[MyStreamingCallback(g)])