"""
Point d’entrée HF Spaces.
Pre-remplit la DB si vide, puis lance le dashboard Streamlit.
"""

import os
import sys
from pathlib import Path

# Ajouter racine projet au PYTHONPATH
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))


from finapi.db import SessionLocal, init_db
from finapi.models import PriceRecord


def bootstrap_data():
    """Si DB vide → lancer mini ETL."""
    init_db()

    with SessionLocal() as session:
        if session.query(PriceRecord).count() > 0:
            return

        print("DB vide, lancement bootstrap ETL...")

        from finapi.etl.news_etl import ingest_news
        from finapi.etl.prices_etl import ingest_prices
        from project_scripts.enrich_sentiment import main as enrich

        for t in ["AAPL", "MSFT", "GOOGL", "TSLA"]:
            ingest_prices(t, period="1mo")
            ingest_news(t)

        enrich()

        print("Bootstrap terminé.")


if os.getenv("BOOTSTRAP", "1") == "1":
    bootstrap_data()


# 🚀 Launch Streamlit app (SAFE way)
import subprocess

dashboard_path = ROOT / "dashboard" / "app.py"

subprocess.run([
    "streamlit",
    "run",
    str(dashboard_path)
])