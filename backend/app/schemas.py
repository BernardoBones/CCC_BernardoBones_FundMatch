from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum


class RiskProfile(str, Enum):
    """
    Enum que representa os perfis de risco disponíveis para o investidor.

    Valores:
        - conservador
        - moderado
        - arrojado
    """
    conservador = "conservador"
    moderado = "moderado"
    arrojado = "arrojado"

class UserCreate(BaseModel):
    """
    Schema para criação de um novo usuário.

    Campos:
        name (str): Nome do usuário.
        email (EmailStr): E-mail válido.
        password (str): Senha com no mínimo 6 caracteres.
    """
    name: str = Field(..., example="Bernardo")
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserOut(BaseModel):
    """
    Schema de saída com os dados públicos de um usuário.

    Campos:
        id (int): Identificador único.
        name (str): Nome do usuário.
        email (EmailStr): E-mail do usuário.
        created_at (datetime): Data de criação da conta.

    Config:
        orm_mode: Permite compatibilidade com objetos ORM.
    """
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    """
    Schema para autenticação de usuário.

    Campos:
        email (EmailStr): E-mail do usuário.
        password (str): Senha em texto plano.
    """
    email: EmailStr
    password: str

class Token(BaseModel):
    """
    Schema de resposta para autenticação JWT.

    Campos:
        access_token (str): Token JWT gerado.
        token_type (str): Tipo do token (default: "bearer").
    """
    access_token: str
    token_type: str = "bearer"

class InvestorProfileCreate(BaseModel):
    """
    Schema para criação ou atualização do perfil de investidor.

    Campos:
        risk_profile (RiskProfile): Perfil de risco do investidor.
        amount_available (Decimal): Valor disponível para investir.
    """
    risk_profile: RiskProfile
    amount_available: Decimal

class InvestorProfileOut(BaseModel):
    """
    Schema de saída para o perfil de investidor.

    Campos:
        id (int): Identificador do perfil.
        user_id (int): ID do usuário associado.
        risk_profile (RiskProfile): Perfil de risco.
        amount_available (Decimal): Valor disponível.
        notes (Optional[str]): Observações adicionais (opcional).

    Config:
        orm_mode: Permite compatibilidade com objetos ORM.
    """
    id: int
    user_id: int
    risk_profile: RiskProfile
    amount_available: Decimal
    notes: Optional[str] = None

    class Config:
        orm_mode = True

class PasswordResetRequest(BaseModel):
    """
    Schema para solicitação de redefinição de senha.

    Campos:
        email (EmailStr): E-mail do usuário.
    """
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """
    Schema para confirmação de redefinição de senha.

    Campos:
        token (str): Token JWT de redefinição.
        new_password (str): Nova senha (mínimo 6 caracteres).
    """
    token: str
    new_password: str = Field(..., min_length=6)
