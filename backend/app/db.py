from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+psycopg2://postgres:masterkey@localhost:5432/fundmatch"

# força client_encoding
engine = create_engine(
    DATABASE_URL,
    connect_args={"options": "-c client_encoding=UTF8"}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()  
    try:
        yield db  
    finally:
        db.close()  