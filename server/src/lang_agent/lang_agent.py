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
        except:
            raise "Can't read system template file"

        template = template_file
        self.weather_format = """
            Please explain the results in detail by organizing them by time.
            - <Answer>
            - <Results>
            - <Greetings>
            ***ANSWER IN KOREAN!!***
        """
        self.search_format = """
            - <Answer>
            ***ASWER IN KOREAN!!***
        """

        
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

        # prompt = CustomPromptTemplate(
        #     template=_template,
        #     tools=get_tools(),
        #     # 이 변수는 동적으로 생성되므로 'agent_scratchpad', 'tools' 및 'tool_names' 변수가 생략됩니다.
        #     # 여기에는 'intermediate_steps' 변수가 포함됩니다. 이 변수는 필요하기 때문입니다
        #     input_variables=["input", "intermediate_steps", "chat_history"],
        # )


        # prompt = PromptTemplate(input_variables=['input'], template=template)


        # LLM chain consisting of the LLM and a prompt
        

        # tool_names = [tool.name for tool in get_tools()]
        # self.agent = LLMSingleActionAgent(
        #     llm_chain=llm_chain, 
        #     output_parser=output_parser,
        #     stop=["\Observation:"], # 이 문자열이 발견되는 즉시 LLM이 생성 작업을 중단하도록 지시합니다.
        #     allowed_tools=tool_names # LLMOutput을 AgentAction이나 AgentFinish 객체로 파싱하는 방법을 결정합니다.
        # )

        
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
        """
            1. 사용자 입력이나 모든 이전단계를 LLMAgent에 전달합니다.
            2. 에이전트가 AgentFinish를 반환하면 바로 사용자에게 결과를 반환합니다.
            3. 에이전트가 AgentAction을 반환하면 이를 사용하여 도구를 호출하고 Observation을 가져옵니다.
            4. AgentAction과 Observation을 AgentFinish가 등장할 때까지 다시 에이전트에 전달하는 일을 반복합니다.
        """
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

        # if(history == ""):
            #채팅이 새로운 시작일 경우 다른거는 추가할 필요없이
            #sql의 createchat을 호출하면 끝
        #공통부분에 json저장함수를 호출할것
        self._save_chats(memory.chat_memory.messages, history_url)
