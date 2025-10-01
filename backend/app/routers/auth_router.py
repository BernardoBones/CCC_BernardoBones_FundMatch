from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from .. import crud, schemas, auth
from ..db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserOut)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db, name=payload.name, email=payload.email, password=payload.password)
    return user

@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, payload.email)
    if not user or not auth.verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token_data = {"sub": str(user.id), "email": user.email}
    access_token = auth.create_access_token(token_data, expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/reset-password")
def password_reset_request(payload: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, payload.email)
    if not user:
        # não revelar se email existe
        raise HTTPException(status_code=200, detail="If the email exists, a reset token was sent.")
    # gerar token JWT curto para reset
    reset_token = auth.create_access_token({"sub": str(user.id), "purpose": "reset"}, expires_delta=timedelta(minutes=30))
    # Em produção: enviar por e-mail. Aqui, retornamos token para testes.
    return {"msg": "Password reset token (for demo only)", "reset_token": reset_token}

@router.post("/confirm-reset")
def password_reset_confirm(payload: schemas.PasswordResetConfirm, db: Session = Depends(get_db)):
    decoded = auth.decode_token(payload.token)
    if not decoded or decoded.get("purpose") != "reset":
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user_id = int(decoded.get("sub"))
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # sobrescreve senha
    user.hashed_password = auth.hash_password(payload.new_password)
    db.add(user)
    db.commit()
    return {"msg": "Password updated successfully"}
