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
    """
    Extrai e valida o usuário autenticado a partir do token Bearer.

    Decodifica o token JWT, verifica se é válido e retorna o usuário correspondente.

    Args:
        credentials (HTTPAuthorizationCredentials): Credenciais extraídas do cabeçalho Authorization.
        db (Session): Sessão do banco de dados.

    Returns:
        models.User: Instância do usuário autenticado.

    Raises:
        HTTPException: Se o token for inválido ou o usuário não for encontrado.
    """
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
    """
    Endpoint público de verificação de saúde da API.

    Returns:
        dict: Status de funcionamento da API.
    """
    return {"status": "ok"}

# list users (protected)
@router.get("/", response_model=List[schemas.UserOut])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user_from_token)):
    """
    Lista todos os usuários cadastrados (requer autenticação).

    Args:
        skip (int): Número de registros a pular (para paginação).
        limit (int): Número máximo de registros a retornar.
        db (Session): Sessão do banco de dados.
        current_user (models.User): Usuário autenticado.

    Returns:
        List[schemas.UserOut]: Lista de usuários.
    """
    return crud.list_users(db, skip=skip, limit=limit)

# get single user (protected)
@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user_from_token)):
    """
    Retorna os dados de um usuário específico pelo ID (requer autenticação).

    Args:
        user_id (int): ID do usuário.
        db (Session): Sessão do banco de dados.
        current_user (models.User): Usuário autenticado.

    Returns:
        schemas.UserOut: Dados do usuário solicitado.

    Raises:
        HTTPException: Se o usuário não for encontrado.
    """
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# update logged-in user's name/email
@router.put("/me", response_model=schemas.UserOut)
def update_me(payload: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user_from_token)):
    """
    Atualiza nome e e-mail do usuário autenticado.

    Args:
        payload (schemas.UserCreate): Dados com nome e e-mail atualizados.
        db (Session): Sessão do banco de dados.
        current_user (models.User): Usuário autenticado.

    Returns:
        schemas.UserOut: Dados atualizados do usuário.
    """
    # payload reuses UserCreate (name/email/password) — we will only update name/email here
    updated = crud.update_user(db, current_user, name=payload.name, email=payload.email)
    return updated

# delete logged-in user
@router.delete("/me")
def delete_me(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user_from_token)):
    """
    Exclui o usuário autenticado da base de dados.

    Args:
        db (Session): Sessão do banco de dados.
        current_user (models.User): Usuário autenticado.

    Returns:
        dict: Mensagem de confirmação da exclusão.
    """
    crud.delete_user(db, current_user)
    return {"msg": "deleted"}

# Profile endpoints (create/update and read)
@router.get("/me/profile", response_model=schemas.InvestorProfileOut)
def get_my_profile(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user_from_token)):
    """
    Retorna o perfil de investidor do usuário autenticado.

    Args:
        db (Session): Sessão do banco de dados.
        current_user (models.User): Usuário autenticado.

    Returns:
        schemas.InvestorProfileOut: Perfil de investidor do usuário.

    Raises:
        HTTPException: Se o perfil não for encontrado.
    """
    prof = crud.get_profile_by_user(db, current_user.id)
    if not prof:
        raise HTTPException(status_code=404, detail="Profile not found")
    return prof

@router.post("/me/profile", response_model=schemas.InvestorProfileOut)
def create_or_update_profile(payload: schemas.InvestorProfileCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user_from_token)):
    """
    Cria ou atualiza o perfil de investidor do usuário autenticado.

    Args:
        payload (schemas.InvestorProfileCreate): Dados do perfil (perfil de risco e valor disponível).
        db (Session): Sessão do banco de dados.
        current_user (models.User): Usuário autenticado.

    Returns:
        schemas.InvestorProfileOut: Perfil atualizado ou recém-criado.
    """
    prof = crud.create_or_update_profile(db, user_id=current_user.id, risk_profile=payload.risk_profile.value, amount_available=payload.amount_available)
    return prof
