from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .db import Base

class RiskProfileEnum(str, enum.Enum):
    """
    Enum que representa os perfis de risco possíveis para um investidor.

    Valores:
        - CONSERVADOR
        - MODERADO
        - ARROJADO
    """
    CONSERVADOR = "conservador"
    MODERADO = "moderado"
    ARROJADO = "arrojado"

class User(Base):
    """
    Modelo de usuário da plataforma.

    Campos:
        id (int): Identificador único.
        name (str): Nome completo do usuário.
        email (str): E-mail único.
        hashed_password (str): Senha criptografada.
        created_at (datetime): Data de criação do registro.

    Relacionamentos:
        profile: Perfil de investidor associado.
        favorites: Lista de fundos favoritados.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("InvestorProfile", back_populates="user", uselist=False)
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")

class InvestorProfile(Base):
    """
    Perfil de investidor associado a um usuário.

    Campos:
        id (int): Identificador único.
        user_id (int): ID do usuário (chave estrangeira).
        risk_profile (RiskProfileEnum): Perfil de risco.
        amount_available (Decimal): Valor disponível para investir.
        updated_at (datetime): Última atualização.

    Relacionamentos:
        user: Referência ao usuário dono do perfil.
    """
    __tablename__ = "investor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    risk_profile = Column(Enum(RiskProfileEnum), default=RiskProfileEnum.MODERADO)
    amount_available = Column(Numeric(18, 2), default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="profile")

class Fund(Base):
    """
    Modelo que representa um fundo de investimento.

    Campos:
        id (int): Identificador único.
        cnpj (str): CNPJ do fundo.
        name (str): Nome do fundo.
        class_name (str): Classe do fundo (ex: renda fixa, multimercado).
        rentability (float): Rentabilidade calculada.
        risk (float): Risco calculado.
        sharpe (float): Índice de Sharpe calculado.
        updated_at (datetime): Última atualização.

    Relacionamentos:
        history: Histórico de cotas (NAVs).
    """
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
    """
    Histórico de cotas (NAV) de um fundo.

    Campos:
        id (int): Identificador único.
        fund_id (int): ID do fundo (chave estrangeira).
        date (datetime): Data da cota.
        nav (float): Valor da cota (NAV).

    Relacionamentos:
        fund: Referência ao fundo associado.
    """
    __tablename__ = "fund_history"

    id = Column(Integer, primary_key=True, index=True)
    fund_id = Column(Integer, ForeignKey("funds.id", ondelete="CASCADE"), index=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    nav = Column(Float, nullable=False)  # NAV / valor da cota

    fund = relationship("Fund", back_populates="history")

class Favorite(Base):
    """
    Associação entre usuário e fundo favoritado.

    Campos:
        id (int): Identificador único.
        user_id (int): ID do usuário (chave estrangeira).
        fund_id (int): ID do fundo (chave estrangeira).

    Relacionamentos:
        user: Referência ao usuário.
        fund: Referência ao fundo.
    """
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    fund_id = Column(Integer, ForeignKey("funds.id", ondelete="CASCADE"))

    user = relationship("User", back_populates="favorites")
    fund = relationship("Fund")
