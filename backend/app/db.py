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
    """
    Fornece uma sessão de banco de dados para uso com dependências do FastAPI.

    Garante que a sessão seja fechada corretamente após o uso.

    Yields:
        Session: Sessão ativa do banco de dados.
    """
    db = SessionLocal()  
    try:
        yield db  
    finally:
        db.close()  