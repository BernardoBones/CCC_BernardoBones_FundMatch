import requests
from backend.app.db import SessionLocal
from sqlalchemy.orm import Session
from backend.app.crud import upsert_fund
import logging
import csv
import io

# from backend.app.cvm_ingest import run_cvm_ingestion
# run_cvm_ingestion()


logging.basicConfig(level=logging.INFO)

CVM_CSV_URL = "https://dados.cvm.gov.br/dados/FI/CAD/DADOS/cad_fi.csv"


def fetch_cvm_data(limit=50):
    """Busca dados de fundos diretamente do CSV da CVM"""
    try:
        resp = requests.get(CVM_CSV_URL, timeout=30)
        resp.raise_for_status()

        # Decodifica o conteúdo do CSV
        content = resp.content.decode("latin1")  # encoding original da CVM
        reader = csv.DictReader(io.StringIO(content), delimiter=';')
        data = list(reader)
        return data[:limit]
    except Exception as e:
        logging.error(f"Erro ao consultar API CVM: {e}")
        return []


def run_cvm_ingestion():
    """Job principal: busca e grava fundos no banco"""
    
    session: Session = SessionLocal()
    logging.info("Iniciando job de ingestão da CVM...")

    funds = fetch_cvm_data(limit=50)
    logging.info(f"{len(funds)} fundos encontrados na CVM")

    for f in funds:
        try:
            cnpj = f.get("CNPJ_FUNDO")
            nome = f.get("DENOM_SOCIAL")
            classe = f.get("CLASSE") or "N/A"
            # para simplificação inicial
            rentabilidade = 0.0
            risco = 0.0
            sharpe = 0.0
            if cnpj and nome:
                upsert_fund(session, cnpj, nome, classe, rentabilidade, risco, sharpe)
        except Exception as e:
            logging.warning(f"Erro ao inserir fundo {f.get('DENOM_SOCIAL')}: {e}")

    session.close()
    logging.info("Job de ingestão finalizado.")
