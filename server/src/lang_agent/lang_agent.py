import re
from typing import List, Union

from langchain.agents import AgentExecutor
from .tools import get_tools
from util import get_openai_model,MyAgentCallback
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import MessagesPlaceholder
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.schema import messages_to_dict, messages_from_dict
import json


# Set up the base template

class LangAgent:
    def __init__(self,g):
        self.callback = MyAgentCallback(g)

        try:
            with open("./prompt/system.txt", "r") as f:
                template_file = f.read()
            with open("./prompt/weather_format.txt", "r") as f:
                weather_format_file = f.read()
            with open("./prompt/search_format.txt", "r") as f:
                search_format_file = f.read()
        except:
            raise "Can't read template file"

        template = template_file
        self.weather_format = weather_format_file
        self.search_format = search_format_file

        
        functions = [
            format_tool_to_openai_function(f) for f in get_tools()
        ]

        prompt = ChatPromptTemplate.from_messages([
            ("system", template),
            MessagesPlaceholder(variable_name='chat_history'),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name='agent_scratchpad')
        ])

        llm = get_openai_model(g).bind(functions=functions)

        self.retrieval_chain = RunnablePassthrough.assign(
            agent_scratchpad = lambda x: format_to_openai_functions(x["intermediate_steps"])
        ) | prompt | llm | OpenAIFunctionsAgentOutputParser()

        
    def _save_chats(self, chat_history, url):
        # extracted_messages = self.memory.chat_memory.messages
        # api에서 token도 받아오도록 해야함
        ingest_to_db = messages_to_dict(chat_history)
        with open(url, 'w+') as outfile:
            json.dump(ingest_to_db,outfile)


    def _get_jsondata(self, url):
        with open(url) as f:
            retreive_from_db = json.load(f)
        retrieved_messages = messages_from_dict(retreive_from_db)
        retrieved_chat_history = ChatMessageHistory(messages=retrieved_messages)
        return retrieved_chat_history

    def run(self,query,history_url,is_new):
        if is_new:
            memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, input_key='input')
        else:
            retrieved_chat_history = self._get_jsondata(history_url)
            memory = ConversationBufferMemory(chat_memory=retrieved_chat_history, memory_key="chat_history", return_messages=True, input_key='input')


        def _handle_error(error) -> str:
            return str(error)[:50]

        agent_executor = AgentExecutor(
            agent=self.retrieval_chain, tools=get_tools(), verbose=True,
            handle_parsing_errors=_handle_error,
            memory=memory,
            callbacks = [self.callback]
        )   

        agent_executor.invoke({"input":query, 
                                "weather_format":self.weather_format,
                                "search_format": self.search_format}
        )

        self._save_chats(memory.chat_memory.messages, history_url)
