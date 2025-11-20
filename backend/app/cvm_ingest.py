import requests
from backend.app.db import SessionLocal
from sqlalchemy.orm import Session
from backend.app.crud import upsert_fund, get_fund_by_cnpj, add_history_bulk
import logging
import csv
import io
from datetime import datetime, timedelta
import random

#from backend.app.cvm_ingest import run_cvm_ingestion
logging.basicConfig(level=logging.INFO)

CVM_CSV_URL = "https://dados.cvm.gov.br/dados/FI/CAD/DADOS/cad_fi.csv"


def fetch_cvm_data(limit=50):
    try:
        resp = requests.get(CVM_CSV_URL, timeout=30)
        resp.raise_for_status()

        content = resp.content.decode("latin1")
        reader = csv.DictReader(io.StringIO(content), delimiter=';')
        data = list(reader)
        return data[:limit]

    except Exception as e:
        logging.error(f"Erro ao consultar API CVM: {e}")
        return []


def generate_simulated_history(db: Session, cnpj: str):
    """
    Função equivalente ao endpoint /{cnpj}/history-test,
    mas chamada internamente pelo ingestion job.
    """

    fund = get_fund_by_cnpj(db, cnpj)
    if not fund:
        logging.warning(f"[history] Fundo não encontrado: {cnpj}")
        return

    # Evita duplicar histórico se já existir
    if hasattr(fund, "history") and len(fund.history) > 0:
        logging.info(f"[history] Fundo {cnpj} já possui histórico. Pulando.")
        return

    base = 100.0
    rows = []
    start_date = datetime.utcnow() - timedelta(days=29)
    nav = base

    for i in range(30):
        change = random.uniform(-0.02, 0.02)   # variação -2% a +2%
        nav = max(0.01, nav * (1 + change))
        date = start_date + timedelta(days=i)
        rows.append((date, nav))

    add_history_bulk(db, fund.id, rows)
    logging.info(f"[history] Gerado histórico simulado para {cnpj} ({len(rows)} dias)")


def run_cvm_ingestion():
    session: Session = SessionLocal()
    logging.info("Iniciando job de ingestão da CVM...")

    funds = fetch_cvm_data(limit=50)
    logging.info(f"{len(funds)} fundos encontrados na CVM")

    for f in funds:
        try:
            cnpj = f.get("CNPJ_FUNDO")
            nome = f.get("DENOM_SOCIAL")
            classe = f.get("CLASSE") or "N/A"

            rentabilidade = 0.0
            risco = 0.0
            sharpe = 0.0

            if cnpj and nome:
                upsert_fund(session, cnpj, nome, classe, rentabilidade, risco, sharpe)

                # 🔥 GERAR HISTÓRICO AUTOMATICAMENTE
                generate_simulated_history(session, cnpj)

        except Exception as e:
            logging.warning(f"Erro ao inserir fundo {f.get('DENOM_SOCIAL')}: {e}")

    session.close()
    logging.info("Job de ingestão finalizado com sucesso!")
