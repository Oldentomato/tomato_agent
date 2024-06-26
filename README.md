<p align="center">
    <img src="./assets/logo.jpeg" width=30% height=30% />
</p>  

## TOMATO_AGENT (with Langchain Agent)   
> This project is still in the development stage.  

This is a project where you can command chatgpt to act.  
You can use the "agent" in "langchain" to carry out the commands you want.  
I used mysql database to store user information and chat history.  
In addition to openai's model, you can also utilize Huggingface's local model.  
The front end is made up of react and the back end is fastapi, and the docker file is also created so that all configurations can be built at once.  
## Libraries  
### python  
```bash
Package             Version
------------------- ----------

konlpy              0.6.0
llama_cpp_python    0.2.26
langchain           0.0.353
langchain-community 0.0.7
langchain-core      0.1.4
numpy               1.26.2
openai              1.6.1
rank-bm25           0.2.2
regex               2023.12.25
soylemma            0.2.0
bs4
langchain[docarray]
tiktoken            0.5.1
google-api-python-client    2.100.0
scikit-learn
uvicorn             0.27.0.post1
python-multipart    0.0.6
SQLAlchemy          2.0.24
mysql-connector-python  8.3.0
python-dotenv       0.21.1
pandas              2.2.2
openpyxl
```
### node  
```json
"@testing-library/jest-dom": "^5.17.0",
"@testing-library/react": "^13.4.0",
"@testing-library/user-event": "^13.5.0",
"antd": "^5.14.0",
"framer-motion": "^11.0.3",
"react": "^18.2.0",
"react-dom": "^18.2.0",
"react-scripts": "5.0.1",
"web-vitals": "^2.1.4"
"prismjs": "^1.29.0",
```
## Enviorment  
### Client 
    - node 18.11.0
### Server
    - python 3.10.13
    - ubuntu 20.03
### DB
    - MySQL


## How to use  
- customize your db structure like ./example_db/init.sql
- set environment variables (dotenv)
- run "docker compose up -d"  


## Functions  
### Use Agent
- search real-time weather info  
![image_1](https://github.com/Oldentomato/tomato_agent/blob/main/assets/search_weather.gif)  
- search to internet  
![image_1](https://github.com/Oldentomato/tomato_agent/blob/main/assets/search_google.gif)  
- chat memory  
![image_1](https://github.com/Oldentomato/tomato_agent/blob/main/assets/memory.gif)  
### Use Mixtral Local Model


## References
- install docker-compose  
```bash
pip install "cython<3.0.0" wheel && pip3 install pyyaml==5.4.1 --no-build-isolation
pip install docker-compose
pip install docker==6.1.3
```
- build docker 
```
docker compose up -d
#do not use docker-compose
```
- design ref from
    - [CSSOnlineTutorial](https://www.youtube.com/@OnlineTutorialsYT)
    - [GPT Style CSS](https://www.youtube.com/watch?v=EzkWAviyYgg)
## to-do  
- 프론트부분에서 fetch요청함수를 모듈화하여 반복정의를 최소화할것  
- 대화내역을 다시 불러올때 도구사용내용이 누락됨
- front에서 shift+enter로 줄넘김 기능 추가
- 실시간 교통상황 도구 개발
- reAct 계획구상
- docker 빌드 테스트중

## License
MIT
