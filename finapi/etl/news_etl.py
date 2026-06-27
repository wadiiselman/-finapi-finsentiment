"""ETL des news : récupération via yfinance news."""

import logging
from datetime import datetime
import yfinance as yf
from sqlalchemy.dialects.sqlite import insert

from finapi.db import SessionLocal
from finapi.models import NewsItem

log = logging.getLogger(__name__)


def ingest_news(ticker: str) -> int:
    """Récupère les news récentes pour un ticker et les stocke."""

    log.info("ETL news: fetching %s", ticker)

    news_list = yf.Ticker(ticker).news or []

    rows = []

    for item in news_list:
        content = item.get("content", item)

        published = content.get("pubDate") or content.get("displayTime")
        if not published:
            continue

        try:
            published_at = datetime.fromisoformat(published.replace("Z", "+00:00"))
        except ValueError:
            continue

        url = (content.get("clickThroughUrl") or {}).get("url")

        rows.append(
            {
                "ticker": ticker.upper(),
                "published_at": published_at,
                "title": (content.get("title") or "")[:500],
                "publisher": (content.get("provider") or {}).get("displayName", ""),
                "url": url,
                "summary": (content.get("summary") or "")[:2000],
            }
        )

    if not rows:
        log.warning("ETL news: aucun article pour %s", ticker)
        return 0

    # remove rows without URL (cannot deduplicate)
    rows = [r for r in rows if r["url"]]

    if not rows:
        return 0

    with SessionLocal() as session:
        stmt = insert(NewsItem).values(rows)

        stmt = stmt.on_conflict_do_nothing(index_elements=["url"])

        result = session.execute(stmt)
        session.commit()

        inserted = result.rowcount or 0

    log.info("ETL news: %d articles insérés pour %s", inserted, ticker)
    return inserted
