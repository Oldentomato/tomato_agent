from langchain.utilities import GoogleSearchAPIWrapper
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from util.getapi import get_weather_api, get_google_search

def search_api(query : str) -> str:
    search = get_google_search()
    # search = GoogleSearchAPIWrapper()
    result = search.run(query)
    return result

# print(search_api("스트리머 괴물쥐"))

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
    #구조: 1. url을 받으면 파싱해서 내용만 추출한 뒤, 요약을 시킴
    # 2. 요약된 내용을 임베딩하여 url과 저장 (embedd_summary, url)
    # 3. 탐색할 때는 요청쿼리와 임베딩 요약내용을 비교하여 찾고 url을 가져온다음 webbrowser로 열기
    pass

#html 탐색할 때
def get_html(url: str):
    loader = WebBaseLoader(url)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    split_docs = text_splitter.split_documents(documents)

    return split_docs

def get_weather(region: str):
    data = pd.read_excel('./server/data/coordinate.xlsx')#나중에 환경변수로 빼놓을것
    now_time = 14
    base_date = '20240413'
    base_time = f'{now_time-1}30'
    apiKey = get_weather_api()
    result_template = ""


    searched_data = data.loc[(data['3단계'] == "영등포동"),['격자 X','격자 Y']].values[0]
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

    #여기도 환경변수로 빼놓을것
    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst'
    params = {'serviceKey': apiKey, 'pageNo' : '1', 'numOfRows' : '1000', 'dataType' : 'JSON',  'base_date' : base_date, 'base_time' : base_time, 'nx' : str(nx), 'ny' : str(ny) }

    response = requests.get(url, params=params, verify=False)
    res = json.loads(response.text)


    informations = dict()
    for items in res['response']['body']['items']['item'] :
        cate = items['category']
        fcstTime = items['fcstTime']
        fcstValue = items['fcstValue']
        temp = dict()
        temp[cate] = fcstValue
        
        if fcstTime not in informations.keys() :
            informations[fcstTime] = dict()
        informations[fcstTime][cate] = fcstValue


    for key, val in zip(informations.keys(), informations.values()) :
    #     print(key, val)
        # val['LGT'] -- 낙뢰 
        template = f"""{base_date[:4]}년 {base_date[4:6]}월 {base_date[-2:]}일 {key[:2]}시 {key[2:]}분 {(int(nx), int(ny))} ({region}) 지역의 날씨는 """ 
        
        # 맑음(1), 구름많음(3), 흐림(4)
        if val['SKY'] :
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

        result_template += template
        template = ""

    return result_template