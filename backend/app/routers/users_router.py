from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud, models, auth
from ..db import get_db

router = APIRouter(prefix="/users", tags=["users"])

# define esquema Bearer
bearer_scheme = HTTPBearer()

# agora extrai o token diretamente do header Authorization
def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials  # só o token sem "Bearer "
    payload = auth.decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = int(payload["sub"])
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

# Public health-check
@router.get("/health")
def health():
    return {"status": "ok"}

# list users (protected)
@router.get("/", response_model=List[schemas.UserOut])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user_from_token)):
    return crud.list_users(db, skip=skip, limit=limit)

# get single user (protected)
@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user_from_token)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# update logged-in user's name/email
@router.put("/me", response_model=schemas.UserOut)
def update_me(payload: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user_from_token)):
    # payload reuses UserCreate (name/email/password) — we will only update name/email here
    updated = crud.update_user(db, current_user, name=payload.name, email=payload.email)
    return updated

# delete logged-in user
@router.delete("/me")
def delete_me(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user_from_token)):
    crud.delete_user(db, current_user)
    return {"msg": "deleted"}

# Profile endpoints (create/update and read)
@router.get("/me/profile", response_model=schemas.InvestorProfileOut)
def get_my_profile(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user_from_token)):
    prof = crud.get_profile_by_user(db, current_user.id)
    if not prof:
        raise HTTPException(status_code=404, detail="Profile not found")
    return prof

@router.post("/me/profile", response_model=schemas.InvestorProfileOut)
def create_or_update_profile(payload: schemas.InvestorProfileCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user_from_token)):
    prof = crud.create_or_update_profile(db, user_id=current_user.id, risk_profile=payload.risk_profile.value, amount_available=payload.amount_available)
    return prof
