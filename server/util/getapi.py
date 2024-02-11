# from dotenv import load_dotenv
import os 
from langchain.chat_models import ChatOpenAI
from langchain_community.utilities import GoogleSearchAPIWrapper
from .callbacks import MyStreamingCallback

# load_dotenv(verbose=True)

def get_google_search():
    # GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    search = GoogleSearchAPIWrapper()
    return search

def get_openai_model(g=None):
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    if g == None:
        return ChatOpenAI(model_name="gpt-3.5-turbo",openai_api_key=OPENAI_API_KEY, streaming=True)
    else:     
        return ChatOpenAI(model_name="gpt-3.5-turbo",openai_api_key=OPENAI_API_KEY, streaming=True,
                        callbacks=[MyStreamingCallback(g)])

# if __name__ == "__main__":
#     tool = get_google_search()
#     result = tool.run("젤다의 전설 왕국의 눈물 출시일")
#     print(result)