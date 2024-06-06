from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

MYSQL_DATABASE_URL = 'mysql+pymysql://root:root1234@127.0.0.1:3306/fast_api_todo'

engine = create_engine(MYSQL_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# sqlite

# SQLALCHEMY_DATABASE_URL = 'sqlite:///./todos.db'
#
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
#
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
