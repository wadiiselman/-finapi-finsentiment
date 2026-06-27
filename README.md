# finapi — API Flask avec persistance SQLite

Lab 2 — Coaching M1/M2 Finance Quantitative | EPT  
Étudiant : Wadii Selmane | Enseignant : Mr. Ahmed Ben Taleb

---

## Prérequis

- Python ≥ 3.10
- Git

---

## Installation

```bash
cd projets/finapi
python -m venv .venv
source .venv/Scripts/activate      # Git Bash (Windows)
# source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\Activate.ps1       # PowerShell
pip install -r requirements.txt
```

---

## Lancer l'ETL (ingestion des données)

```bash
PYTHONPATH=. python scripts/run_etl.py AAPL MSFT GOOGL
```

Le pipeline récupère les prix et les actualités pour chaque ticker
et les insère dans `data/finapi.db` (les doublons sont ignorés).

---

## Lancer le serveur

```bash
python -m finapi.app
```

Le serveur démarre sur `http://127.0.0.1:5000`.

---

## Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/health` | Statut du serveur |
| GET | `/price/<ticker>` | Dernier cours (temps réel via yfinance) |
| GET | `/history/<ticker>?days=N` | Historique N jours (temps réel) |
| GET | `/db/prices/<ticker>` | Historique depuis SQLite |
| GET | `/db/news/<ticker>` | Actualités depuis SQLite |

---

## Exemples

```bash
# Santé du serveur
curl http://localhost:5000/health

# Cours en temps réel
curl http://localhost:5000/price/AAPL

# Historique depuis la base
curl http://localhost:5000/db/prices/AAPL

# Actualités depuis la base
curl http://localhost:5000/db/news/AAPL
```

---

## Gestion des erreurs

| Code | Cas |
|------|-----|
| 400 | Paramètre `days` invalide |
| 404 | Ticker introuvable |
| 500 | Erreur interne serveur |

---

## Structure du projet

```
finapi/
├── .venv/                  (ignoré par Git)
├── data/
│   └── finapi.db           (ignoré par Git)
├── finapi/
│   ├── __init__.py
│   ├── app.py              endpoints Flask
│   ├── db.py               configuration SQLAlchemy
│   ├── models.py           modèles prices et news
│   ├── prices.py           accès yfinance (temps réel)
│   └── etl/
│       ├── __init__.py
│       ├── prices_etl.py   ingestion des cours
│       └── news_etl.py     ingestion des actualités
├── scripts/
│   └── run_etl.py          script d'exécution ETL
├── tests/
│   └── test_app.py
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Versionnement

```bash
git log --oneline
# 2ab7d2d add ETL pipeline for prices and news ingestion
# 1773ede add db layer (SQLAlchemy setup + models)
# e1ef7b8 Lab1: API Flask pour cours boursiers
```