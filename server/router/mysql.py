from fastapi import APIRouter,HTTPException
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.orm import sessionmaker, declarative_base

mysql = APIRouter()

# MySQL 연결 정보
DATABASE_URL = "mysql+mysqlconnector://your_mysql_username:your_mysql_password@mysql_db:3306/your_database_name"

# SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL)

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 모델 정의
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, index=True)
    user_pass = Column(String)
    token = Column(String, primary_key=True)

# 테이블이 생성되었는지 확인하기 위함
metadata = MetaData()
your_table = Table("users", metadata, autoload=True, autoload_with=engine)


@mysql.post("/login")
async def login(name: str, password: str, token: str):
    db = SessionLocal()
    item = db.query(User).filter(Item.user_name == name and Item.user_pass == password).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    else:
        item.token = token
        db.commit()
        db.refresh(item)
    return {"item": item}

# @mysql.get("/getuserinfo")
# async def getuser_info(token: str):
#     db = SessionLocal()
#     item = db.query(User).filter(Item.token == token).first()
#     if item is None:
#         raise HTTPException(status_code=404, detail="Item not found")
#     else:
