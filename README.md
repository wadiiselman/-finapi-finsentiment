---
title: FinSentiment
emoji: 📈
colorFrom: blue
colorTo: yellow
sdk: streamlit
sdk_version: "1.35.0"
python_version: "3.10"
app_file: app.py
pinned: false
license: mit
---

# FinSentiment

![CI](https://github.com/wadiiselman/-finapi-finsentiment/actions/workflows/ci.yml/badge.svg)

🚀 **Live demo:** https://huggingface.co/spaces/wadii123/finsentiment

A financial sentiment analysis tool that fetches stock prices and news, runs them through FinBERT, and displays the results in an interactive Streamlit dashboard.

---

## What it does

- Pulls historical prices and news articles for any stock ticker (AAPL, MSFT, GOOGL, TSLA...)
- Classifies each news headline as **positive**, **neutral**, or **negative** using [FinBERT](https://huggingface.co/ProsusAI/finbert), a transformer model pre-trained on 4.9 billion financial tokens
- Exposes all data through a REST API built with Flask
- Displays prices, sentiment distribution, and a color-coded news feed in a Streamlit dashboard
- Fully tested with pytest and linted with Ruff, with CI running on every push via GitHub Actions

---

## Stack

- **Flask** — REST API
- **SQLAlchemy + SQLite** — local persistent storage
- **yfinance** — real-time and historical market data
- **HuggingFace Transformers + FinBERT** — NLP sentiment model
- **Streamlit + Plotly** — interactive dashboard
- **pytest + Ruff + GitHub Actions** — testing and CI/CD

---

## Project structure

```
finapi_clean/               ← clean repo root (see note below)
├── app.py                  ← HuggingFace Spaces entry point
├── finapi/                 ← Flask API + business logic
│   ├── __init__.py
│   ├── app.py              all Flask endpoints
│   ├── db.py               SQLAlchemy engine + session
│   ├── models.py           PriceRecord + NewsItem ORM models
│   ├── prices.py           live data via yfinance
│   ├── sentiment.py        FinBERT singleton + analyze/batch
│   └── etl/
│       ├── prices_etl.py   idempotent price ingestion
│       └── news_etl.py     idempotent news ingestion
├── dashboard/              ← Streamlit front-end
│   ├── app.py              main page (sidebar, metrics, charts, news)
│   ├── api_client.py       HTTP wrapper for Flask API
│   └── charts.py           Plotly price line + sentiment pie
├── project_scripts/        ← data pipeline scripts
│   ├── run_etl.py          ingest prices + news for given tickers
│   └── enrich_sentiment.py run FinBERT on unenriched news (idempotent)
├── tests/
│   ├── conftest.py         shared pytest fixtures
│   ├── test_app_health.py
│   ├── test_history_validation.py
│   └── test_sentiment.py
├── .github/
│   └── workflows/
│       └── ci.yml          GitHub Actions — lint + test on every push
├── pyproject.toml          pytest + ruff configuration
├── requirements.txt        minimal cross-platform dependencies
└── README.md
```

---

## Installation

```bash
git clone https://github.com/wadiiselman/-finapi-finsentiment.git
cd finapi-finsentiment
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

---

## Quickstart

**Step 1 — Ingest prices and news**
```bash
python project_scripts/run_etl.py AAPL MSFT GOOGL
```

**Step 2 — Run FinBERT sentiment enrichment**
```bash
python project_scripts/enrich_sentiment.py
```
> First run downloads the FinBERT model (~440 MB). All subsequent runs are instant.

**Step 3 — Start the Flask API** (terminal 1)
```bash
python -m finapi.app
```

**Step 4 — Start the Streamlit dashboard** (terminal 2)
```bash
streamlit run dashboard/app.py
```

Open `http://localhost:8501` in your browser.

---

## API endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/health` | Health check |
| GET | `/price/<ticker>` | Latest price (live via yfinance) |
| GET | `/history/<ticker>?days=N` | Price history N days (live) |
| GET | `/db/prices/<ticker>` | Prices from SQLite |
| GET | `/db/news/<ticker>` | News from SQLite |
| GET | `/db/stats` | Database statistics |
| POST | `/sentiment` | Classify a single text with FinBERT |
| POST | `/sentiment/batch` | Classify up to 100 texts |
| GET | `/db/sentiment-summary/<ticker>` | Sentiment distribution for a ticker |

```bash
# Examples
curl http://localhost:5000/health
curl http://localhost:5000/db/prices/AAPL
curl http://localhost:5000/db/sentiment-summary/AAPL
curl -X POST http://localhost:5000/sentiment \
  -H "Content-Type: application/json" \
  -d '{"text": "Apple beats earnings expectations significantly."}'
```

---

## Tests

```bash
pytest
pytest --cov=finapi --cov-report=term-missing
```

Expected output:
```
collected 5 items
tests/test_app_health.py::test_health_returns_200        PASSED
tests/test_history_validation.py::test_invalid_days      PASSED
tests/test_history_validation.py::test_days_out_of_range PASSED
tests/test_sentiment.py::test_analyze_positive           PASSED
tests/test_sentiment.py::test_analyze_empty_raises       PASSED
5 passed
```

---

## Linting

```bash
ruff check .
ruff format .
```

---

## ⚠️ Known difficulty — deployment cleanup

During development, the virtual environment (`.venv`, `Lib/`, `Scripts/`) was accidentally committed to the Git repository. This caused pushes to both GitHub (100 MB file limit) and HuggingFace Spaces (10 MB binary file limit) to be rejected repeatedly.

**What happened:**
- The venv was created at the project root instead of in a subfolder, so `Lib/`, `Scripts/`, `Include/` and `pyvenv.cfg` were tracked by Git
- `git filter-repo --strip-blobs-bigger-than 50M` was used to scrub large files from history, but binary `.pyd`, `.dll` and `.exe` files under 10 MB were still blocked by HF Spaces

**How it was resolved:**
A clean repository (`finapi_clean/`) was created from scratch containing only source code files, with a fresh Git history. This is the repository that was pushed to GitHub and HuggingFace Spaces.

**To avoid this in future projects, always:**
1. Create `.gitignore` before the first `git add .`
2. Put your venv in a named subfolder: `python -m venv .venv`
3. Make sure `.gitignore` includes:

```
.venv/
venv/
Lib/
Scripts/
Include/
pyvenv.cfg
__pycache__/
*.pyc
data/
```

---

## HuggingFace Spaces deployment notes

The `app.py` at the repo root is the HF Spaces entry point. It:
1. Bootstraps the SQLite database on first startup (runs ETL + FinBERT enrichment)
2. Launches the Streamlit dashboard via `exec()`

**Important adjustments made for deployment:**
- `requirements.txt` uses unpinned, cross-platform versions (the original was generated on Windows Python 3.14 and contained Windows-specific pinned packages incompatible with the Linux/Python 3.10 HF environment)
- Scripts are in `project_scripts/` (not `scripts/`) to avoid conflicts with the venv's `Scripts/` folder on Windows
- The bootstrap import path is `from project_scripts.enrich_sentiment import main as enrich`
- Streamlit is launched with `exec()` rather than `subprocess.run()` to avoid spawning multiple instances

---

## Author

**Wadii Selmane** — M1/M2 Finance Quantitative  
Supervised by **Mr. Ahmed Ben Taleb** — ITBS · SMARTLab ISG Tunis