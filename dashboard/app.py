"""Dashboard interactif d'analyse de sentiment financier."""

from datetime import datetime

import streamlit as st

from dashboard import api_client as api
from dashboard.charts import price_line_chart, sentiment_pie_chart, SENT_COLORS


# -------- Configuration de la page --------
st.set_page_config(
    page_title="FinSentiment Dashboard",
    page_icon="📈",
    layout="wide",
)


# -------- Sidebar --------
with st.sidebar:
    st.title("Contrôles")
    st.caption("Configurez votre vue ci-dessous.")

    api_ok = api.get_health()

    if api_ok:
        st.success("API connectée")
    else:
        st.error("API injoignable")
        st.info("Lancez `python -m finapi.app` dans un autre terminal.")
        st.stop()

    stats = api.get_db_stats()
    available_tickers = stats.get("tickers", [])

    if not available_tickers:
        st.warning("Base vide. Lancez `python scripts/run_etl.py AAPL MSFT`.")
        st.stop()

    ticker = st.selectbox("Ticker", available_tickers)

    st.divider()

    if st.button("Refresh maintenant"):
        st.cache_data.clear()
        st.rerun()

    st.caption(
        f"DB: {stats.get('prices_count', 0)} prix | "
        f"{stats.get('news_count', 0)} news | "
        f"{stats.get('news_enriched', 0)} avec sentiment"
    )


# -------- Header --------
st.title(f"📈 FinSentiment - {ticker}")
st.caption("Dashboard interactif - prix, news, sentiment FinBERT")


# -------- Data caching --------
@st.cache_data(ttl=60)
def load_prices(t: str):
    return api.get_db_prices(t)


@st.cache_data(ttl=60)
def load_news(t: str):
    return api.get_db_news(t)


@st.cache_data(ttl=60)
def load_summary(t: str):
    return api.get_sentiment_summary(t)


prices = load_prices(ticker)
news = load_news(ticker)
sentiment = load_summary(ticker)


# -------- Metrics --------
col1, col2, col3, col4 = st.columns(4)

if prices:
    last = prices[0]
    prev = prices[1] if len(prices) > 1 else last

    delta = last["close"] - prev["close"]

    col1.metric("Dernier cours", f"{last['close']:.2f}", f"{delta:+.2f}")
    col2.metric("Date", last["date"])
    col3.metric("News stockées", len(news))

    total_sent = sum(sentiment.values()) or 1
    pos_share = sentiment.get("positive", 0) / total_sent * 100

    col4.metric("Sentiment positif", f"{pos_share:.0f}%")


st.divider()


# -------- Charts --------
g1, g2 = st.columns([2, 1])

with g1:
    st.subheader("Évolution du prix")
    st.plotly_chart(price_line_chart(prices), use_container_width=True)

with g2:
    st.subheader("Distribution sentiment")

    if sentiment:
        st.plotly_chart(sentiment_pie_chart(sentiment), use_container_width=True)
    else:
        st.info("Aucun sentiment calculé. Lancez `enrich_sentiment.py`.")


# -------- News list --------
st.subheader(f"Dernières news - {ticker}")

if not news:
    st.info("Aucune news en base.")
else:
    for n in news[:15]:
        sent = n.get("sentiment_label") or "neutral"
        color = SENT_COLORS.get(sent, "#94A3B8")

        st.markdown(
            f"""
            <div style="
                border-left: 4px solid {color};
                padding: 8px 14px;
                margin: 6px 0;
                background: #F8FAFC;
            ">
                <b>{n["title"]}</b><br>
                <small style="color:#64748B">
                    {n.get("publisher", "")} - {n.get("published_at", "")[:16]} -
                    <span style="color:{color}; font-weight:bold;">
                        {sent.upper()}
                    </span>
                </small>
            </div>
            """,
            unsafe_allow_html=True,
        )


st.divider()

st.caption(f"Mise à jour : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
