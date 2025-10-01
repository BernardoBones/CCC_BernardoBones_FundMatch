from fastapi import FastAPI
from .db import engine, Base
from .routers import auth_router, users_router
import os

# cria tabelas (apenas para dev; em produção use alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FundMatch API", version="0.1.0")

# inclui routers
app.include_router(auth_router.router)
app.include_router(users_router.router)

@app.get("/health")
def health():
    return {"status": "ok"}
