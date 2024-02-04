from langchain.prompts import BaseChatPromptTemplate
from langchain.schema import AgentAction, AgentFinish, HumanMessage



template = """Complete the objective as best you can. You have access to the following tools:

{tools}

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

Begin!

Question: {input}
{agent_scratchpad}"""

# Set up a prompt template
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


################

        output_parser = CustomOutputParser()


        llm = get_openai_model()


        prompt = CustomPromptTemplate(
            template=template,
            tools=get_tools(),
            # 이 변수는 동적으로 생성되므로 'agent_scratchpad', 'tools' 및 'tool_names' 변수가 생략됩니다.
            # 여기에는 'intermediate_steps' 변수가 포함됩니다. 이 변수는 필요하기 때문입니다
            input_variables=["input", "intermediate_steps"],
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