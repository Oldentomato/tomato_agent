from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging

from router.agent_router import agent_route
from router.llm_router import llm_route

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 모든 origin에 대해 액세스 허용
    allow_credentials=True,
    allow_methods=["*"], #모든 HTTP 메서드에 대해 액세스 허용
    allow_headers=["*"]
)

# app.add_middleware(
#     TrustedHostMiddleware, allow_hosts=["localhost"]
# )

logging.basicConfig(level=logging.INFO)

app.include_router(agent_route, prefix="/agent")
app.include_router(llm_route, prefix="/llm")

@app.get('/')
def health_check():
    return {'success': True}