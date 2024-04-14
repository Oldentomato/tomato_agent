from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool
import pickle
from .define_tools import *
# from util import get_google_search, get_openai_model

#define_tools의 함수들이 인식은 되는데 실제로 동작은 안되는 것으로 파악됨
class SaveHTMLInput(BaseModel):
    summary: str = Field(description="Get url in query and extract to html data.")


class GetHTMLInput(BaseModel):
    url: str = Field(description="extract url in query.")

class SearchInput(BaseModel):
    query: str = Field(description="get question.")


class CalculatorInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")
    c: str = Field(description="a calculation symbol. If it comes in word form, convert it into a symbol accordingly.")

class SearchWeather(BaseModel):
    region: str = Field(description="extract region name in query")

# save_html_tool = StructuredTool.from_function(
#     func=save_html(),
#     name="save content",
#     description="Save Summarized html content",
#     args_schema=SaveHTMLInput,
#     return_direct=True
# )

search_query_tool = StructuredTool.from_function(
    func=search_api,
    name="search in internet",
    description="useful for when you need to answer questions about current events",
    args_schema=SearchInput,
    return_direct=True
)

calc_num_tool = StructuredTool.from_function(
    func=calc_num,
    name="Calculator",
    description="calcurate numbers",
    args_schema=CalculatorInput,
    return_direct=True
)


get_html_tool = StructuredTool.from_function(
    func=get_html,
    name="get_html_content",
    description="If there is a url in the query, parse the html content of url.",
    args_schema=GetHTMLInput,
    return_direct=True #나중에 검색할 것
)

get_weather_tool = StructuredTool.from_function(
    func=get_weather,
    name="search weather info",
    description="search weather info to region",
    args_schema=SearchWeather,
    return_direct=True
)

__tools = [search_query_tool, calc_num_tool, get_weather_tool]

def get_tools():
    return __tools