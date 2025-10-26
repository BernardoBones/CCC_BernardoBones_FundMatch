from datetime import datetime
from sqlalchemy.orm import Session
from . import models
from .auth import hash_password
from .metrics import calculate_returns, calculate_volatility, calculate_sharpe, total_return
from decimal import Decimal
from .models import Favorite, Fund
from sqlalchemy import func

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

def get_fund_by_cnpj(db: Session, cnpj: str):
    return db.query(models.Fund).filter(models.Fund.cnpj == str(cnpj)).first()

def list_history_for_fund(db: Session, fund_id: int, limit: int = 100):
    return db.query(models.FundHistory).filter(models.FundHistory.fund_id == fund_id).order_by(models.FundHistory.date).limit(limit).all()

def add_history_entry(db: Session, fund_id: int, date: datetime, nav: float):
    entry = models.FundHistory(fund_id=fund_id, date=date, nav=nav)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def add_history_bulk(db: Session, fund_id: int, rows):
    """rows: iterable de tuples (date, nav)"""
    for date, nav in rows:
        entry = models.FundHistory(fund_id=fund_id, date=date, nav=nav)
        db.add(entry)
    db.commit()

def compute_metrics_from_history(db: Session, cnpj: str, risk_free: float = 0.0):
    fund = get_fund_by_cnpj(db, cnpj)
    if not fund:
        return None

    history = list_history_for_fund(db, fund.id, limit=1000)
    prices = [h.nav for h in history]
    if len(prices) < 2:
        # sem histórico suficiente, retorna zeros
        return {"rentability": 0.0, "volatility": 0.0, "sharpe": 0.0, "n": len(prices)}

    returns = calculate_returns(prices)
    vol = calculate_volatility(returns)
    sharpe = calculate_sharpe(returns, risk_free)
    rent = total_return(prices)

    # opcional: atualizar os campos do Fund
    fund.rentability = rent
    fund.volatility = vol
    fund.sharpe = sharpe
    fund.updated_at = datetime.utcnow()
    db.add(fund)
    db.commit()
    db.refresh(fund)

    return {"rentability": rent, "volatility": vol, "sharpe": sharpe, "n": len(prices)}

def add_favorite(db, user_id: int, fund_id: int):
    fav = db.query(Favorite).filter_by(user_id=user_id, fund_id=fund_id).first()
    if not fav:
        fav = Favorite(user_id=user_id, fund_id=fund_id)
        db.add(fav)
        db.commit()
        db.refresh(fav)
    return fav

def remove_favorite(db, user_id: int, fund_id: int):
    fav = db.query(Favorite).filter_by(user_id=user_id, fund_id=fund_id).first()
    if fav:
        db.delete(fav)
        db.commit()
        return True
    return False

def list_favorites(db, user_id: int):
    return (
        db.query(Fund)
        .join(Favorite, Favorite.fund_id == Fund.id)
        .filter(Favorite.user_id == user_id)
        .all()
    )

def get_recommendations(db, user_id: int):
    """Simples: recomenda fundos da classe mais favoritada."""

    # Conta quantos fundos de cada classe o usuário favoritou
    subq = (
        db.query(Fund.class_name, func.count(Fund.id).label("total"))
        .join(Favorite, Favorite.fund_id == Fund.id)
        .filter(Favorite.user_id == user_id)
        .group_by(Fund.class_name)
        .order_by(func.count(Fund.id).desc())
        .limit(1)
        .first()
    )
    if not subq:
        return db.query(Fund).limit(5).all()

    top_class = subq[0]
    return db.query(Fund).filter(Fund.class_name == top_class).limit(5).all()