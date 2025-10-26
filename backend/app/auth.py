from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import crud
from .db import get_db
import os


# Define o esquema OAuth2 (tokenUrl deve apontar para /auth/login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# security settings
SECRET_KEY = os.getenv("JWT_SECRET", "CHANGE_THIS_SECRET_FOR_PROD")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 dia

# usa argon2 (mais seguro e sem limite de 72 bytes)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Gera o hash seguro de uma senha usando o algoritmo Argon2.

    Args:
        password (str): Senha em texto plano.

    Returns:
        str: Hash criptografado da senha.
    """
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """
    Verifica se uma senha corresponde ao seu hash.

    Args:
        password (str): Senha em texto plano.
        hashed (str): Hash previamente armazenado.

    Returns:
        bool: True se a senha for válida, False caso contrário.
    """
    return pwd_context.verify(password, hashed)

# JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Cria um token JWT com os dados fornecidos e tempo de expiração.

    Args:
        data (dict): Dados a serem codificados no token (ex: sub, email).
        expires_delta (Optional[timedelta]): Tempo até expiração do token.

    Returns:
        str: Token JWT assinado.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    """
    Decodifica um token JWT e retorna seu payload.

    Args:
        token (str): Token JWT a ser decodificado.

    Returns:
        dict | None: Payload decodificado se válido, ou None se inválido.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
    
def get_current_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Extrai e valida o token JWT enviado no header Authorization: Bearer <token>,
    retornando o usuário autenticado.

    Args:
        token (str): Token JWT extraído do cabeçalho Authorization.
        db (Session): Sessão do banco de dados.

    Returns:
        models.User: Instância do usuário autenticado.

    Raises:
        HTTPException: Se o token for inválido, expirado ou o usuário não existir.
    """
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(payload["sub"])
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")

    return user
