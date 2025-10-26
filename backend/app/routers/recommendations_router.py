from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..auth import get_current_user_from_token
from .. import crud

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/")
def get_user_recommendations(db: Session = Depends(get_db), user=Depends(get_current_user_from_token)):
    recs = crud.get_recommendations(db, user.id)
    return recs
