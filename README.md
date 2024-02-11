<p align="center">
    <img src="./assets/logo.jpeg" width=30% height=30% />
</p>  

## TOMATO_AGENT (with Langchain Agent)     

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
```
## Enviorment  
### Client 
    - node 18.11.0
### Server
    - python 3.10.13
    - ubuntu 20.03


## How to use  
https://console.cloud.google.com/apis/dashboard?pli=1&project=shining-granite-299216

## Functions  
### Chat GPT
### Use Agent
- save & search html
- search to internet
- save & search a piece of code 
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

## License
MIT
## To-Do List
- 임베딩 일정시간 자동실행
- 특정 명령어 권한에 따라 실행가능하게 하기(보류)
- 로컬 모델기능 추가
- 챗봇시작할 때 도움말 나오게 하기
- url 이미지 혹은 영상을 diffusion으로 변환하여 제공
- url이 있을 경우 url에 대한 정보 보여주게 하기
- 임베딩 추가부분에서 마지막 채팅을 찾고 자동으로 추가시키기
- 임베딩 정보(마지막 저장 날짜, 임베딩 채팅갯수, 채널명) content.pkl에 저장하고 조회기능 만들기