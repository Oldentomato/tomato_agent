from pydantic.v1 import BaseModel, Field
from langchain.agents import tool
import requests
from dotenv import load_dotenv
import os
from datetime import datetime,timedelta
import json
from datetime import datetime
import pandas as pd
from util.getapi import get_google_search

load_dotenv(verbose=True)
__excel_dir = os.getenv("REGION_EXCEL_DIR")
data = pd.read_excel(__excel_dir)

# Define the input schema
class Weather_Input(BaseModel):
    region: str = Field(..., description="extract region name in query")

class GoogleSearch_Input(BaseModel):
    keyword: str = Field(..., description="search for keyword")

@tool(args_schema=GoogleSearch_Input)
def __get_googlesearch_tool(keyword: str) -> str:
    """search at google to keyword"""
    search = get_google_search()
    result = search.run(keyword)
    return result


@tool(args_schema=Weather_Input)
def __get_weather_tool(region: str) -> str:
    """search weather info to region"""

    now = datetime.now()
    now_time = now.hour

    apiKey = os.getenv("WEATHER_API_KEY")

    if now.month < 10:
        month = f"0{now.month}"
    else:
        month = str(now.month)
    if now.day < 10:
        day = f"0{now.day}"
    else:
        day = str(now.day)
    base_date = f'{str(now.year)}{month}{str(day)}'
    base_time = f'{now_time-1}30'

    def check_contains(row):
        # 행의 주소열 문자열
        row_str = row['3단계']
        # 검색어가 행의 주소열에 포함되는지 확인
        return region in row_str

    # region = '영등포동'
    # nx = '62'
    # ny = '123'
    try:
        searched_data = data.loc[data['3단계'].str.contains(region, na=False),['격자 X','격자 Y']].values[0]
    except:
        return "해당 지역명은 없습니다."
    else:
        nx, ny = searched_data


    deg_code = {0 : 'N', 360 : 'N', 180 : 'S', 270 : 'W', 90 : 'E', 22.5 :'NNE',
            45 : 'NE', 67.5 : 'ENE', 112.5 : 'ESE', 135 : 'SE', 157.5 : 'SSE',
            202.5 : 'SSW', 225 : 'SW', 247.5 : 'WSW', 292.5 : 'WNW', 315 : 'NW',
            337.5 : 'NNW'}

    pyt_code = {0 : '강수 없음', 1 : '비', 2 : '비/눈', 3 : '눈', 5 : '빗방울', 6 : '진눈깨비', 7 : '눈날림'}
    sky_code = {1 : '맑음', 3 : '구름많음', 4 : '흐림'}


    def deg_to_dir(deg) :
        close_dir = ''
        min_abs = 360
        if deg not in deg_code.keys() :
            for key in deg_code.keys() :
                if abs(key - deg) < min_abs :
                    min_abs = abs(key - deg)
                    close_dir = deg_code[key]
        else : 
            close_dir = deg_code[deg]
        return close_dir


    #알고 싶은 시간
    input_d = datetime.strptime(base_date + base_time, '%Y%m%d%H%M')
    print(input_d)

    #실제 입력 시간
    input_d = datetime.strptime(base_date + base_time, '%Y%m%d%H%M') - timedelta(hours=1)
    print(input_d)

    input_datetime = datetime.strftime(input_d, '%Y%m%d%H%M')
    input_date = input_datetime[:-4]
    input_time = input_datetime[-4:]

    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst'
    params = {'serviceKey': apiKey, 'pageNo' : '1', 'numOfRows' : '1000', 'dataType' : 'JSON',  'base_date' : base_date, 'base_time' : base_time, 'nx' : str(nx), 'ny' : str(ny) }

    response = requests.get(url, params=params, verify=False)
    res = json.loads(response.text)
    
    template = ""
    #추후 수정해야함
    # if res['resultMsg'] == "NO_DATA":
    #     return "데이터를 찾을 수 없습니다."

    informations = dict()
    for items in res['response']['body']['items']['item'] :
        cate = items['category']
        fcstTime = items['fcstTime']
        fcstValue = items['fcstValue']
        temp = dict()
        temp[cate] = fcstValue
        
        if fcstTime not in informations.keys() :
            informations[fcstTime] = dict()
    #     print(items['category'], items['fcstTime'], items['fcstValue'])
    #     print(informations[fcstTime])
        informations[fcstTime][cate] = fcstValue


    for key, val in zip(informations.keys(), informations.values()) :
    #     print(key, val)
        # val['LGT'] -- 낙뢰 
        template += f"""{base_date[:4]}년 {base_date[4:6]}월 {base_date[-2:]}일 {key[:2]}시 {key[2:]}분 {(int(nx), int(ny))} ({region}) 지역의 날씨는 """ 
        
        if val['SKY'] :
            # skycode = int(val['SKY'])
            sky_temp = sky_code[int(val['SKY'])]
            template += sky_temp + " "
        
        # (초단기) 없음(0), 비(1), 비/눈(2), 눈(3), 빗방울(5), 빗방울눈날림(6), 눈날림(7)
        if val['PTY'] :
            pty_temp = pyt_code[int(val['PTY'])]
    #         print("강수 여부 :",pty_temp)
            template += pty_temp
            # 강수 있는 경우
            if val['RN1'] != '강수없음' :
                # RN1 1시간 강수량 
                rn1_temp = val['RN1']
    #             print("강수량(1시간당) :",rn1_temp)
                template += f"시간당 {rn1_temp}mm "
        
        # 기온
        if val['T1H'] :
            t1h_temp = float(val['T1H'])
    #         print(f"기온 : {t1h_temp}℃")
            template += f" 기온 {t1h_temp}℃ "
        # 습도
        if val['REH'] :
            reh_temp = float(val['REH'])
    #         print(f"습도 : {reh_temp}%")
            template += f"습도 {reh_temp}% "
        # val['UUU'] -- 바람
        
        # val['VVV'] -- 바람
        
        # 풍향/ 풍속
        if val['VEC'] and val['WSD']:
            vec_temp = deg_to_dir(float(val['VEC']))
            wsd_temp = val['WSD']
    #         print(f"풍속 :{vec_temp} 방향 {wsd_temp}m/s")
            
        template += f"풍속 {vec_temp} 방향 {wsd_temp}m/s \n"

    # print(template)
    return template

__tools = [__get_weather_tool,__get_googlesearch_tool]
def get_tools():
    return __tools
