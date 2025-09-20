from fastapi import FastAPI
from fastapi import Depends
from sqlalchemy.orm import Session
from backend.app import db
from backend.app.models.user import User

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/users/test")
def create_user(database: Session = Depends(db.get_db)):
    new_user = User(name="Teste", email="teste@fundmatch.com")
    database.add(new_user)
    database.commit()
    database.refresh(new_user)
    return {"id": new_user.id, "name": new_user.name}