from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..auth import get_current_user_from_token
from .. import crud

router = APIRouter(prefix="/favorites", tags=["favorites"])

@router.post("/{fund_id}")
def add_to_favorites(fund_id: int, db: Session = Depends(get_db), user=Depends(get_current_user_from_token)):
    fav = crud.add_favorite(db, user.id, fund_id)
    return {"message": "Added to favorites", "favorite_id": fav.id}

@router.delete("/{fund_id}")
def remove_from_favorites(fund_id: int, db: Session = Depends(get_db), user=Depends(get_current_user_from_token)):
    removed = crud.remove_favorite(db, user.id, fund_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"message": "Removed from favorites"}

@router.get("/")
def list_user_favorites(db: Session = Depends(get_db), user=Depends(get_current_user_from_token)):
    favorites = crud.list_favorites(db, user.id)
    return favorites
