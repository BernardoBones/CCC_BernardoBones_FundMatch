from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.db import engine, Base
from backend.app.routers import auth_router, users_router, funds_router
from apscheduler.schedulers.background import BackgroundScheduler
from backend.app.cvm_ingest import run_cvm_ingestion
import atexit


Base.metadata.create_all(bind=engine)

app = FastAPI(title="FundMatch API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # durante desenvolvimento, libera tudo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui routers
app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(funds_router.router)

@app.get("/health")
def health():
    return {"status": "ok"}

# Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(run_cvm_ingestion, "interval", hours=6, id="cvm_ingestion")
scheduler.start()

atexit.register(lambda: scheduler.shutdown())
