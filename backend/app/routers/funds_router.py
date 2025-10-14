from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import random

from .. import crud, models
from ..db import get_db

router = APIRouter(prefix="/funds", tags=["funds"])

@router.get("/", summary="List all funds")
def get_funds(db: Session = Depends(get_db)):
    return crud.list_funds(db)

@router.get("/{cnpj:path}/history", summary="Get fund history")
def get_history(cnpj: str, db: Session = Depends(get_db)):
    fund = crud.get_fund_by_cnpj(db, cnpj)
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")
    history = crud.list_history_for_fund(db, fund.id, limit=1000)
    # serializar history simples
    return [{"date": h.date.isoformat(), "nav": h.nav} for h in history]

@router.post("/{cnpj:path}/history-test", summary="Add simulated history (dev only)")
def add_history_test(cnpj: str, db: Session = Depends(get_db)):
    """
    Endpoint de desenvolvimento para popular histórico de um fundo com dados simulados.
    Usa 30 dias de cotas com pequenas variações.
    """
    fund = crud.get_fund_by_cnpj(db, cnpj)
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")

    # Simula 30 dias de NAVs a partir de um valor base
    base = 100.0
    rows = []
    start_date = datetime.utcnow() - timedelta(days=29)
    nav = base
    for i in range(30):
        # variação diária aleatória pequena -0.02 .. +0.02
        change = random.uniform(-0.02, 0.02)
        nav = max(0.01, nav * (1 + change))
        date = start_date + timedelta(days=i)
        rows.append((date, nav))

    crud.add_history_bulk(db, fund.id, rows)
    return {"msg": f"Added {len(rows)} simulated history rows for fund {cnpj}"}

@router.get("/{cnpj:path}/metrics", summary="Compute and return metrics for a fund")
def get_metrics(cnpj: str, risk_free: float = 0.0, db: Session = Depends(get_db)):
    metrics = crud.compute_metrics_from_history(db, cnpj, risk_free=risk_free)
    if metrics is None:
        raise HTTPException(status_code=404, detail="Fund not found")
    return metrics
