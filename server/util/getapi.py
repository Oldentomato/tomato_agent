from dotenv import load_dotenv
import os 
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

load_dotenv(verbose=True)

def get_google_search():
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    search = GoogleSearchAPIWrapper(google_api_key=GOOGLE_API_KEY)
    return search

def get_openai_model():
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    return ChatOpenAI(model_name="gpt-3.5-turbo",openai_api_key=OPENAI_API_KEY, streaming=True,
                        callbacks=[StreamingStdOutCallbackHandler()])