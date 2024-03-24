import re
from typing import List, Union

from langchain.chains import LLMChain
from langchain.agents import (
    AgentExecutor,
    AgentOutputParser,
    LLMSingleActionAgent,
    Tool
)
from .tools import get_tools
from util import get_openai_model
from langchain_community.tools.convert_to_openai import format_tool_to_openai_function
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.prompts import BaseChatPromptTemplate
from langchain.schema import AgentAction, AgentFinish, HumanMessage, messages_to_dict, messages_from_dict
from util import MyAgentCallback
import json


# 구조화까지 끝나면 우선 html저장기능을 먼저 만들고 그 다음에 코드조각 저장기능을 만들어 놓자
# 만일 tool을 잘 찾지 못한다면 종이에 쓴 기법을 한번 활용해보자 (아직까지는 얘가 tool을 잘 고름)
# 근데 인터넷 검색결과성능이 너무 처참함 이것도 추후에 수정해볼것

# 에이전트가 무엇을 해야하는지 이 템플릿을 이용하여 지시합니다. 일반적으로 템플릿에는 다음이 포함되어야 합니다.

# tools : 에이전트가 액세스할 수 있는 도구와 언제 어떻게 호출해야 하는지 알 수 있습니다.
# intermediate_steps : 이전 (AgentAction, Observation) 쌍의 튜플입니다. 일반적으로 모델에 직접 전달되지는 않지만 프롬프트 템플릿에서 특정 방식으로 포맷을 정합니다.
# input : 일반적인 사용자 입력

_template = """Complete the objective as best you can. You have access to the following tools:

{tools}

and reference the previous conversation:
{chat_history}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question and translate to korean

These were previous tasks you completed:

Maybe just conversation don't follow format, just answer. and also can use previous conversation.

Begin!

Question: {input}
{agent_scratchpad}"""

class CustomOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={
                    "output": llm_output.split("Final Answer:")[-1].strip()
                },
                log=llm_output,
            )
        # Parse out the action and action input
        regex = (
            r"Action\s*\d*\s*:(.*?)\Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
            r"|https?://\S+"
        )
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)

        # Return the action and action input
        return AgentAction(
            tool=action,
            tool_input=action_input.strip(" ").strip('"'),
            log=llm_output,
        )

class CustomPromptTemplate(BaseChatPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]

    def format_messages(self, **kwargs) -> str:
        # 중간 단계 가져오기 (AgentAction, Observation tuples)
        # 특정방법으로 포맷
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\Observation: {observation}\Thought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join(
            [f"{tool.name}: {tool.description}" for tool in self.tools]
        )
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])

        formatted = self.template.format(**kwargs)
        return [HumanMessage(content=formatted)]

# Set up the base template

class LangAgent:
    def __init__(self,g):
        output_parser = CustomOutputParser()
        self.callback = MyAgentCallback(g)

        llm = get_openai_model()

        prompt = CustomPromptTemplate(
            template=_template,
            tools=get_tools(),
            # 이 변수는 동적으로 생성되므로 'agent_scratchpad', 'tools' 및 'tool_names' 변수가 생략됩니다.
            # 여기에는 'intermediate_steps' 변수가 포함됩니다. 이 변수는 필요하기 때문입니다
            input_variables=["input", "intermediate_steps", "chat_history"],
        )

        # LLM chain consisting of the LLM and a prompt
        llm_chain = LLMChain(llm=llm, prompt=prompt)

        tool_names = [tool.name for tool in get_tools()]
        self.agent = LLMSingleActionAgent(
            llm_chain=llm_chain, 
            output_parser=output_parser,
            stop=["\Observation:"], # 이 문자열이 발견되는 즉시 LLM이 생성 작업을 중단하도록 지시합니다.
            allowed_tools=tool_names # LLMOutput을 AgentAction이나 AgentFinish 객체로 파싱하는 방법을 결정합니다.
        )

        
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
            memory = ConversationBufferMemory(memory_key="chat_history")
        else:
            retrieved_chat_history = self._get_jsondata(history_url)
            memory = ConversationBufferMemory(chat_memory=retrieved_chat_history, memory_key="chat_history")
        # if history != None:
        #     retrieved_chat_history = ChatMessageHistory(messages=history)
        #     # memory = ConversationBufferMemory(memory_key="chat_history")
        #     memory = ConversationBufferMemory(chat_memory=retrieved_chat_history, memory_key="chat_history")
        # else:
        #     memory = ConversationBufferMemory(memory_key="chat_history")

        def _handle_error(error) -> str:
            return str(error)[:50]

        agent_executor = AgentExecutor(
            agent=self.agent, tools=get_tools(), verbose=True,
            handle_parsing_errors=_handle_error,
            memory=memory
        )   

        agent_executor.run({"input":query}, callbacks=[self.callback])

        # if(history == ""):
            #채팅이 새로운 시작일 경우 다른거는 추가할 필요없이
            #sql의 createchat을 호출하면 끝
        #공통부분에 json저장함수를 호출할것
        self._save_chats(memory.chat_memory.messages, history_url)
