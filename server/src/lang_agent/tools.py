from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
import pickle
from util import get_google_search, get_openai_model


def search_api(query : str) -> str:
    """useful for when you need to answer questions about current events""" 
    search = get_google_search()
    result = search.run(query)
    return result


def calc_num(a:int, b:int, c:str) -> int:
    temp = -1
    if c == "+":
        temp = a + b
    elif c == "-":
        temp = a - b
    elif c == "*":
        temp = a * b
    elif c == "/":
        temp = a / b
    else:
        print(f"error symbol: {c}")

    return temp


def save_html(summary: str):
    """Get url in query and extract to html data."""
    #구조: 1. url을 받으면 파싱해서 내용만 추출한 뒤, 요약을 시킴
    # 2. 요약된 내용을 임베딩하여 url과 저장 (embedd_summary, url)
    # 3. 탐색할 때는 요청쿼리와 임베딩 요약내용을 비교하여 찾고 url을 가져온다음 webbrowser로 열기
    pass

#html 탐색할 때
def get_html(url: str):
    loader = WebBaseLoader(url)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    splite_docs = text_splitter.split_documents(documents)

    return splite_docs

def summarize_html(content: str):
    summarize_chain = load_summarize_chain(llm=get_openai_model(),chain_type="map_reduce",verbose=True)

    AI_response = summarize_chain.run(content)

    return AI_response

class SaveHTMLInput(BaseModel):
    summary: str = Field(description="get summarize content")

class SummarizeInput(BaseModel):
    content: str = Field(description="content for summarize.")

class GetHTMLInput(BaseModel):
    url: str = Field(description="extract url in query.")


class CalculatorInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")
    c: str = Field(description="a calculation symbol. If it comes in word form, convert it into a symbol accordingly.")

save_html_tool = StructuredTool.from_function(
    func=save_html,
    name="save content",
    description="Save Summarized html content",
    args_schema=SaveHTMLInput,
    return_direct=True
)

calc_num_tool = StructuredTool.from_function(
    func=calc_num,
    name="Calculator",
    description="calcurate numbers",
    args_schema=CalculatorInput,
    return_direct=True
)

summarize_html_tool = StructuredTool.from_function(
    func=summarize_html,
    name="summarize_html_content",
    description="After parse the html content, summarize content.",
    args_schema=SummarizeInput,
    return_direct=True,
    
)

get_html_tool = StructuredTool.from_function(
    func=get_html,
    name="get_html_content",
    description="If there is a url in the query, parse the html content of url.",
    args_schema=GetHTMLInput,
    return_direct=True #나중에 검색할 것
)

__tools = [calc_num_tool, get_html_tool, summarize_html_tool, save_html_tool]

def get_tools():
    return __tools