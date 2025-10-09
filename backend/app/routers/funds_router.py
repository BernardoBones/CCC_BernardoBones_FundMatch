from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import crud
from ..db import get_db

router = APIRouter(prefix="/funds", tags=["funds"])

@router.get("/")
def get_funds(db: Session = Depends(get_db)):
    return crud.list_funds(db)