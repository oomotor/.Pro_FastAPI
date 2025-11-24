from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ベースクラスの作成
Base = declarative_base()

# ユーザーテーブルの作成
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    hobby = Column(String)

# SQLiteデータベースの接続設定
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# テーブルを作成
Base.metadata.create_all(bind=engine)

# セッションの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)