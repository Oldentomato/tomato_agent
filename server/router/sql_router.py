from fastapi import APIRouter,HTTPException, Form
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv(verbose=True)
sqlroute = APIRouter()

# MySQL 연결 정보
DATABASE_URL = os.getenv('DATABASE_URL')

# SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL)

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

db = SessionLocal()

# 모델 정의
class User(Base):
    __tablename__ = "users"

    # id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, primary_key=True)
    user_password = Column(String)
    token = Column(String)

    chats = relationship("Chats", back_populates="user")

class Chats(Base):
    __tablename__ = "chats"

    chat_id = Column(String, primary_key=True)
    user_name = Column(String, ForeignKey('users.user_name'))
    chat_path = Column(String)

    user = relationship("User", back_populates="chats")

# 테이블이 생성되었는지 확인하기 위함
# metadata = MetaData()
# your_table = Table("users", metadata, autoload=True, autoload_with=engine)


@sqlroute.post("/login")
async def login(name:str=Form(...), password:str=Form(...), token:str=Form(...)):
    item = db.query(User).filter(User.user_name == name , User.user_password == password).first()
    if item is None:
        # raise HTTPException(status_code=404, detail="Item not found")
        return {"success":False, "error":"not found user"}
    else:
        if item.token != "":
            return {"success": False, "error":"auth error"}
        else:
            item.token = token
            db.commit()
            db.refresh(item)
    return {"success":True, "item": item}

# INSERT INTO users (id, name) VALUES (1105, '테스트');
# mysql> update users set token = '' where user_name = 'woosung';

@sqlroute.post("/getuser")
async def getuser(token: str=Form(...)):
    item = db.query(User).filter(User.token == token).first()
    if item is None:
        # raise HTTPException(status_code=404, detail="Item not found")
        return {"success": False}
    else:
        return {"success": True}

@sqlroute.post("/logout")
async def logout(token: str=Form(...)):
    item = db.query(User).filter(User.token == token).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    else:
        item.token = ""
        db.commit()
        return {"success": True}

@sqlroute.post("/getchats")
async def get_chats(token: str=Form(...)):
    item = db.query(User).filter(User.token == token).first()
    item = db.query(Chats).filter(Chats.user_name == item.user_name).all()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    else:
        return {"success": True, "item":item}

@sqlroute.post("/createchat")
async def create_chat(token: str=Form(...)):
    item = db.query(User).filter(User.token == token).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    else:
        add_chat = Chats(user_id=item.user_name, chat_path=f"./store/{token}.json")
        db.add(add_chat)
        db.commit()