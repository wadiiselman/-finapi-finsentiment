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

A financial sentiment analysis tool that fetches stock prices and news, runs them through FinBERT, and displays the results in an interactive dashboard.

## What it does

- Pulls historical prices and news articles for any stock ticker (AAPL, MSFT, GOOGL...)
- Classifies each news headline as **positive**, **neutral**, or **negative** using [FinBERT](https://huggingface.co/ProsusAI/finbert)
- Displays prices, sentiment distribution, and colored news feed in a Streamlit dashboard

## Installation

```bash
git clone https://github.com/wadiiselman/-finapi-finsentiment.git
cd finapi-finsentiment
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

## Quickstart

```bash
python project_scripts/run_etl.py AAPL MSFT GOOGL
python project_scripts/enrich_sentiment.py
python -m finapi.app        # terminal 1
streamlit run dashboard/app.py  # terminal 2
```

## Stack

- Flask · SQLAlchemy · SQLite · yfinance · FinBERT · Streamlit · Plotly