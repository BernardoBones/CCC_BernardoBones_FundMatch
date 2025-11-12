import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from .. import crud, schemas, auth
from ..db import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

# Dicionário simples para guardar tentativas falhas em memória
failed_attempts = {}
BLOCK_TIME = 60  # segundos
MAX_ATTEMPTS = 3


@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Autentica um usuário e retorna um token JWT.
    Agora inclui controle de tentativas falhas e mede tempo de resposta.
    """
    start_time = time.time()
    email = payload.email.lower()
    user = crud.get_user_by_email(db, email)

    # Bloqueio temporário
    if email in failed_attempts:
        info = failed_attempts[email]
        if info["count"] >= MAX_ATTEMPTS and (time.time() - info["last"]) < BLOCK_TIME:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Conta temporariamente bloqueada. Tente novamente em {int(BLOCK_TIME - (time.time() - info['last']))}s.",
            )

    # Verifica credenciais
    if not user or not auth.verify_password(payload.password, user.hashed_password):
        if email not in failed_attempts:
            failed_attempts[email] = {"count": 1, "last": time.time()}
        else:
            failed_attempts[email]["count"] += 1
            failed_attempts[email]["last"] = time.time()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

    # Reset tentativas no sucesso
    if email in failed_attempts:
        failed_attempts[email]["count"] = 0

    token_data = {"sub": str(user.id), "email": user.email}
    access_token = auth.create_access_token(
        token_data,
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    duration = round(time.time() - start_time, 3)
    print(f"[RNF] Login executado em {duration}s")

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.UserOut)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Registra um novo usuário.

    Verifica se o e-mail já está cadastrado. Se não estiver, cria um novo usuário
    com os dados fornecidos.

    Args:
        payload (schemas.UserCreate): Dados do usuário (nome, e-mail, senha).
        db (Session): Sessão do banco de dados.

    Returns:
        schemas.UserOut: Dados do usuário recém-criado.

    Raises:
        HTTPException: Se o e-mail já estiver registrado.
    """
    existing = crud.get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db, name=payload.name, email=payload.email, password=payload.password)
    return user


@router.post("/reset-password")
def password_reset_request(payload: schemas.PasswordResetRequest, db: Session = Depends(get_db)):
    """
    Solicita redefinição de senha.

    Gera um token de redefinição de senha com validade curta. Por segurança,
    a resposta é sempre a mesma, independentemente da existência do e-mail.

    Args:
        payload (schemas.PasswordResetRequest): E-mail do usuário.
        db (Session): Sessão do banco de dados.

    Returns:
        dict: Mensagem de confirmação e token de redefinição (apenas para testes).

    Raises:
        HTTPException: Sempre retorna status 200, mesmo se o e-mail não existir.
    """
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
    """
    Confirma a redefinição de senha com um token válido.

    Decodifica o token de redefinição, valida seu propósito e atualiza a senha
    do usuário correspondente.

    Args:
        payload (schemas.PasswordResetConfirm): Token de redefinição e nova senha.
        db (Session): Sessão do banco de dados.

    Returns:
        dict: Mensagem de sucesso.

    Raises:
        HTTPException: Se o token for inválido ou expirado, ou se o usuário não for encontrado.
    """
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
