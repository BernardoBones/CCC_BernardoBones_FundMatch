from datetime import datetime
from sqlalchemy.orm import Session
from . import models
from .auth import hash_password
from decimal import Decimal

# Users
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, name: str, email: str, password: str):
    hashed = hash_password(password)
    db_user = models.User(name=name, email=email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def list_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def update_user(db: Session, user: models.User, name: str = None, email: str = None):
    if name:
        user.name = name
    if email:
        user.email = email
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user: models.User):
    db.delete(user)
    db.commit()
    return True

# Investor profile
def get_profile_by_user(db: Session, user_id: int):
    return db.query(models.InvestorProfile).filter(models.InvestorProfile.user_id == user_id).first()

def create_or_update_profile(db: Session, user_id: int, risk_profile, amount_available):
    prof = get_profile_by_user(db, user_id)
    if not prof:
        prof = models.InvestorProfile(user_id=user_id, risk_profile=risk_profile, amount_available=Decimal(amount_available))
        db.add(prof)
    else:
        prof.risk_profile = risk_profile
        prof.amount_available = Decimal(amount_available)
    db.commit()
    db.refresh(prof)
    return prof

def upsert_fund(db: Session, cnpj: str, name: str, class_name: str, rentability: float, risk: float, sharpe: float):
    fund = db.query(models.Fund).filter(models.Fund.cnpj == cnpj).first()
    if not fund:
        fund = models.Fund(cnpj=cnpj, name=name, class_name=class_name, rentability=rentability, risk=risk, sharpe=sharpe)
        db.add(fund)
    else:
        fund.name = name
        fund.class_name = class_name
        fund.rentability = rentability
        fund.risk = risk
        fund.sharpe = sharpe
        fund.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(fund)
    return fund

def list_funds(db: Session, skip=0, limit=100):
    return db.query(models.Fund).offset(skip).limit(limit).all()