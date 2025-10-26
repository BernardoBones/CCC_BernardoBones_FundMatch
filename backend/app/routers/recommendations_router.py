from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..auth import get_current_user_from_token
from .. import crud

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/")
def get_user_recommendations(db: Session = Depends(get_db), user=Depends(get_current_user_from_token)):
    """
    Retorna recomendações personalizadas de fundos para o usuário autenticado.

    As recomendações são geradas com base no perfil e histórico do usuário.

    Args:
        db (Session): Sessão do banco de dados.
        user: Usuário autenticado extraído do token JWT.

    Returns:
        list: Lista de fundos recomendados para o usuário.
    """
    recs = crud.get_recommendations(db, user.id)
    return recs
