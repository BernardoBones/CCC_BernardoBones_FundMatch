from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .db import Base

class RiskProfileEnum(str, enum.Enum):
    CONSERVADOR = "conservador"
    MODERADO = "moderado"
    ARROJADO = "arrojado"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("InvestorProfile", back_populates="user", uselist=False)
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")

class InvestorProfile(Base):
    __tablename__ = "investor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    risk_profile = Column(Enum(RiskProfileEnum), default=RiskProfileEnum.MODERADO)
    amount_available = Column(Numeric(18, 2), default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="profile")

class Fund(Base):
    __tablename__ = "funds"

    id = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String(20), unique=True, index=True)
    name = Column(String(255), nullable=False)
    class_name = Column(String(100), nullable=True)
    rentability = Column(Float, nullable=True)
    risk = Column(Float, nullable=True)
    sharpe = Column(Float, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

    history = relationship("FundHistory", back_populates="fund", cascade="all, delete-orphan")

class FundHistory(Base):
    __tablename__ = "fund_history"

    id = Column(Integer, primary_key=True, index=True)
    fund_id = Column(Integer, ForeignKey("funds.id", ondelete="CASCADE"), index=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    nav = Column(Float, nullable=False)  # NAV / valor da cota

    fund = relationship("Fund", back_populates="history")

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    fund_id = Column(Integer, ForeignKey("funds.id", ondelete="CASCADE"))

    user = relationship("User", back_populates="favorites")
    fund = relationship("Fund")
