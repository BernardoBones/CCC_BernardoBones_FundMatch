from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..auth import get_current_user_from_token
from .. import crud

router = APIRouter(prefix="/favorites", tags=["favorites"])

@router.post("/{fund_id}")
def add_to_favorites(fund_id: int, db: Session = Depends(get_db), user=Depends(get_current_user_from_token)):
    """
    Adiciona um fundo à lista de favoritos do usuário autenticado.

    Args:
        fund_id (int): ID do fundo a ser adicionado aos favoritos.
        db (Session): Sessão do banco de dados.
        user: Usuário autenticado extraído do token JWT.

    Returns:
        dict: Mensagem de confirmação e ID do favorito criado.
    """
    fav = crud.add_favorite(db, user.id, fund_id)
    return {"message": "Added to favorites", "favorite_id": fav.id}

@router.delete("/{fund_id}")
def remove_from_favorites(fund_id: int, db: Session = Depends(get_db), user=Depends(get_current_user_from_token)):
    """
    Remove um fundo da lista de favoritos do usuário autenticado.

    Args:
        fund_id (int): ID do fundo a ser removido dos favoritos.
        db (Session): Sessão do banco de dados.
        user: Usuário autenticado extraído do token JWT.

    Returns:
        dict: Mensagem de confirmação da remoção.

    Raises:
        HTTPException: Se o favorito não for encontrado.
    """
    removed = crud.remove_favorite(db, user.id, fund_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"message": "Removed from favorites"}

@router.get("/")
def list_user_favorites(db: Session = Depends(get_db), user=Depends(get_current_user_from_token)):
    """
    Lista todos os fundos favoritos do usuário autenticado.

    Args:
        db (Session): Sessão do banco de dados.
        user: Usuário autenticado extraído do token JWT.

    Returns:
        list: Lista de fundos marcados como favoritos pelo usuário.
    """
    favorites = crud.list_favorites(db, user.id)
    return favorites
