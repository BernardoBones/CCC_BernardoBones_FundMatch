from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum

# Request/response schemas

class RiskProfile(str, Enum):
    conservador = "conservador"
    moderado = "moderado"
    arrojado = "arrojado"

class UserCreate(BaseModel):
    name: str = Field(..., example="Bernardo")
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class InvestorProfileCreate(BaseModel):
    risk_profile: RiskProfile
    amount_available: Decimal

class InvestorProfileOut(BaseModel):
    id: int
    user_id: int
    risk_profile: RiskProfile
    amount_available: Decimal
    notes: Optional[str] = None

    class Config:
        orm_mode = True

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)
