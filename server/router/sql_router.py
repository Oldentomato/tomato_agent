from fastapi import APIRouter,HTTPException, Form
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel

sqlroute = APIRouter()

# MySQL 연결 정보
DATABASE_URL = "mysql+mysqlconnector://my_user:qwer1234@localhost:3306/tomatodb"

# SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL)

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 모델 정의
class User(Base):
    __tablename__ = "users"

    # id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String)
    user_password = Column(String)
    token = Column(String, primary_key=True)

# 테이블이 생성되었는지 확인하기 위함
# metadata = MetaData()
# your_table = Table("users", metadata, autoload=True, autoload_with=engine)


@sqlroute.post("/login")
async def login(name:str=Form(...), password:str=Form(...), token:str=Form(...)):
    db = SessionLocal()
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

@sqlroute.post("/getuser")
async def getuser(token: str=Form(...)):
    db = SessionLocal()
    item = db.query(User).filter(User.token == token).first()
    if item is None:
        # raise HTTPException(status_code=404, detail="Item not found")
        return {"success": False}
    else:
        return {"success": True}

@sqlroute.post("/logout")
async def logout(token: str=Form(...)):
    db = SessionLocal()
    item = db.query(User).filter(User.token == token).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    else:
        item.token = ""
        db.commit()
        return {"success": True}
