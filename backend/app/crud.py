from datetime import datetime
from sqlalchemy.orm import Session
from . import models
from .auth import hash_password
from .metrics import calculate_returns, calculate_volatility, calculate_sharpe, total_return
from decimal import Decimal
from .models import Favorite, Fund
from sqlalchemy import func


def get_user_by_email(db: Session, email: str):
    """
    Busca um usuário pelo e-mail.

    Args:
        db (Session): Sessão do banco de dados.
        email (str): E-mail do usuário.

    Returns:
        models.User | None: Usuário encontrado ou None.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def get_user(db: Session, user_id: int):
    """
    Busca um usuário pelo ID.

    Args:
        db (Session): Sessão do banco de dados.
        user_id (int): ID do usuário.

    Returns:
        models.User | None: Usuário encontrado ou None.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, name: str, email: str, password: str):
    """
    Cria um novo usuário com senha criptografada.

    Args:
        db (Session): Sessão do banco de dados.
        name (str): Nome do usuário.
        email (str): E-mail do usuário.
        password (str): Senha em texto plano.

    Returns:
        models.User: Usuário criado.
    """
    hashed = hash_password(password)
    db_user = models.User(name=name, email=email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def list_users(db: Session, skip: int = 0, limit: int = 100):
    """
    Lista usuários com suporte a paginação.

    Args:
        db (Session): Sessão do banco de dados.
        skip (int): Quantidade de registros a pular.
        limit (int): Quantidade máxima de registros a retornar.

    Returns:
        List[models.User]: Lista de usuários.
    """
    return db.query(models.User).offset(skip).limit(limit).all()

def update_user(db: Session, user: models.User, name: str = None, email: str = None):
    """
    Atualiza nome e/ou e-mail de um usuário.

    Args:
        db (Session): Sessão do banco de dados.
        user (models.User): Instância do usuário.
        name (str): Novo nome (opcional).
        email (str): Novo e-mail (opcional).

    Returns:
        models.User: Usuário atualizado.
    """
    if name:
        user.name = name
    if email:
        user.email = email
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user: models.User):
    """
    Exclui um usuário do banco de dados.

    Args:
        db (Session): Sessão do banco de dados.
        user (models.User): Instância do usuário.

    Returns:
        bool: True se excluído com sucesso.
    """
    db.delete(user)
    db.commit()
    return True

def get_profile_by_user(db: Session, user_id: int):
    """
    Busca o perfil de investidor de um usuário.

    Args:
        db (Session): Sessão do banco de dados.
        user_id (int): ID do usuário.

    Returns:
        models.InvestorProfile | None: Perfil encontrado ou None.
    """
    return db.query(models.InvestorProfile).filter(models.InvestorProfile.user_id == user_id).first()

def create_or_update_profile(db: Session, user_id: int, risk_profile, amount_available):
    """
    Cria ou atualiza o perfil de investidor de um usuário.

    Args:
        db (Session): Sessão do banco de dados.
        user_id (int): ID do usuário.
        risk_profile: Perfil de risco.
        amount_available: Valor disponível para investir.

    Returns:
        models.InvestorProfile: Perfil atualizado ou criado.
    """
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
    """
    Cria ou atualiza um fundo com base no CNPJ.

    Args:
        db (Session): Sessão do banco de dados.
        cnpj (str): CNPJ do fundo.
        name (str): Nome do fundo.
        class_name (str): Classe do fundo.
        rentability (float): Rentabilidade.
        risk (float): Risco.
        sharpe (float): Índice de Sharpe.

    Returns:
        models.Fund: Fundo atualizado ou criado.
    """
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
    """
    Lista os fundos disponíveis com paginação.

    Args:
        db (Session): Sessão do banco de dados.
        skip (int): Quantidade de registros a pular.
        limit (int): Quantidade máxima de registros a retornar.

    Returns:
        List[models.Fund]: Lista de fundos.
    """
    return db.query(models.Fund).offset(skip).limit(limit).all()

def get_fund_by_cnpj(db: Session, cnpj: str):
    """
    Busca um fundo pelo CNPJ.

    Args:
        db (Session): Sessão do banco de dados.
        cnpj (str): CNPJ do fundo.

    Returns:
        models.Fund | None: Fundo encontrado ou None.
    """
    return db.query(models.Fund).filter(models.Fund.cnpj == str(cnpj)).first()

def list_history_for_fund(db: Session, fund_id: int, limit: int = 100):
    """
    Lista o histórico de cotas (NAV) de um fundo.

    Args:
        db (Session): Sessão do banco de dados.
        fund_id (int): ID do fundo.
        limit (int): Número máximo de registros.

    Returns:
        List[models.FundHistory]: Histórico de cotas.
    """
    return db.query(models.FundHistory).filter(models.FundHistory.fund_id == fund_id).order_by(models.FundHistory.date).limit(limit).all()

def add_history_entry(db: Session, fund_id: int, date: datetime, nav: float):
    """
    Adiciona uma entrada ao histórico de cotas de um fundo.

    Args:
        db (Session): Sessão do banco de dados.
        fund_id (int): ID do fundo.
        date (datetime): Data da cota.
        nav (float): Valor da cota.

    Returns:
        models.FundHistory: Entrada criada.
    """
    entry = models.FundHistory(fund_id=fund_id, date=date, nav=nav)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def add_history_bulk(db: Session, fund_id: int, rows):
    """
    Adiciona múltiplas entradas ao histórico de cotas de um fundo.

    Args:
        db (Session): Sessão do banco de dados.
        fund_id (int): ID do fundo.
        rows (iterable): Tuplas (date, nav).
    """
    for date, nav in rows:
        entry = models.FundHistory(fund_id=fund_id, date=date, nav=nav)
        db.add(entry)
    db.commit()

def compute_metrics_from_history(db: Session, cnpj: str, risk_free: float = 0.0):
    """
    Calcula métricas financeiras com base no histórico de cotas de um fundo.

    Métricas incluem rentabilidade total, volatilidade e índice de Sharpe.

    Args:
        db (Session): Sessão do banco de dados.
        cnpj (str): CNPJ do fundo.
        risk_free (float): Taxa livre de risco.

    Returns:
        dict | None: Dicionário com métricas ou None se fundo não encontrado.
    """
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
    """
    Adiciona um fundo à lista de favoritos do usuário.

    Args:
        db (Session): Sessão do banco de dados.
        user_id (int): ID do usuário.
        fund_id (int): ID do fundo.

    Returns:
        models.Favorite: Favorito criado ou existente.
    """
    fav = db.query(Favorite).filter_by(user_id=user_id, fund_id=fund_id).first()
    if not fav:
        fav = Favorite(user_id=user_id, fund_id=fund_id)
        db.add(fav)
        db.commit()
        db.refresh(fav)
    return fav

def remove_favorite(db, user_id: int, fund_id: int):
    """
    Remove um fundo da lista de favoritos do usuário.

    Args:
        db (Session): Sessão do banco de dados.
        user_id (int): ID do usuário.
        fund_id (int): ID do fundo.

    Returns:
        bool: True se removido, False se não encontrado.
    """
    fav = db.query(Favorite).filter_by(user_id=user_id, fund_id=fund_id).first()
    if fav:
        db.delete(fav)
        db.commit()
        return True
    return False

def list_favorites(db, user_id: int):
    """
    Lista os fundos favoritados por um usuário.

    Args:
        db (Session): Sessão do banco de dados.
        user_id (int): ID do usuário.

    Returns:
        List[models.Fund]: Lista de fundos favoritados.
    """
    return (
        db.query(Fund)
        .join(Favorite, Favorite.fund_id == Fund.id)
        .filter(Favorite.user_id == user_id)
        .all()
    )

from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import Fund, Favorite

def get_recommendations(db: Session, user_id: int):
    """
    Retorna recomendações de fundos com base na classe mais favoritada pelo usuário.

    - Se o usuário tiver favoritos → identifica a classe mais favoritada.
    - Recomenda até 5 fundos dessa classe.
    - Evita recomendar fundos já favoritados.
    - Se o usuário não tiver favoritos → recomenda fundos genéricos.
    """

    # 1. Descobre qual classe o usuário favoritou mais
    top_class_row = (
        db.query(
            Fund.class_name,
            func.count(Fund.id).label("total")
        )
        .join(Favorite, Favorite.fund_id == Fund.id)
        .filter(Favorite.user_id == user_id)
        .group_by(Fund.class_name)
        .order_by(func.count(Fund.id).desc())
        .first()
    )

    # 2. Se não tiver favoritos → devolve fundos genéricos
    if not top_class_row:
        return db.query(Fund).limit(5).all()

    top_class = top_class_row.class_name

    # 3. Busca ids que já estão favoritados para evitar recomendar duplicado
    user_favorites_ids = (
        db.query(Favorite.fund_id)
        .filter(Favorite.user_id == user_id)
        .subquery()
    )

    # 4. Recomenda até 5 fundos dessa classe que não estão entre os favoritos
    recommendations = (
        db.query(Fund)
        .filter(Fund.class_name == top_class)
        .filter(Fund.id.not_in(user_favorites_ids))
        .limit(5)
        .all()
    )

    # 5. Se todos são favoritos → retorna genéricos para não ficar vazio
    if len(recommendations) == 0:
        return db.query(Fund).limit(5).all()

    return recommendations
