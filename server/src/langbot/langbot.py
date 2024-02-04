from langchain import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.chains import LLMChain
from util import get_openai_model

## 이부분에서 streaming하게 나오는 기능과 thread의 g변수를 담아줄 코드도 작성해야함

sys_prompt = PromptTemplate(
    input_variables=["question"],
    template="""
    당신은 친근한 대화봇입니다.
    질문을 받으면 상세하고 자세히 설명해주세요. 질문은 아래와 같습니다.\n
    {question}
    반말을 해도 괜찮고, 가능한 상냥하게 대답해주세요.
    모르면 모른다고 대답해주세요.
    """
)

system_message_prompt = SystemMessagePromptTemplate(prompt=sys_prompt)

user_prompt = PromptTemplate(
    input_variables=["question"],
    template="""
    {question} 이 질문에 대답해주세요.
    """
)

user_message_prompt = HumanMessagePromptTemplate(prompt=user_prompt)

chat_prompt = ChatPromptTemplate.from_messages(
    [system_message_prompt, user_message_prompt]
)

class LangchainChatBot:
    def __init__(self):
        chat = get_openai_model()
        self.chain = LLMChain(llm=chat, prompt=chat_prompt)

    def chat(self, g, query):
        result = self.chain.run({"question": query})
        print(result)
        g.send(result)

if __name__ == "__main__":
    test = LangchainChatBot()
    test.chat("너는 누구야?")