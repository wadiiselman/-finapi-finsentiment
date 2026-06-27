"""Graphiques Plotly pour le dashboard."""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


NAVY = "#0A1F44"
GOLD = "#C9A961"

SENT_COLORS = {
    "positive": "#16A34A",
    "neutral": "#94A3B8",
    "negative": "#DC2626",
}


def price_line_chart(prices: list[dict]) -> go.Figure:
    if not prices:
        return go.Figure()

    df = pd.DataFrame(prices).sort_values("date")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["close"],
            mode="lines+markers",
            line=dict(color=NAVY, width=2),
            marker=dict(size=4, color=GOLD),
            name="Close",
        )
    )

    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        height=320,
        xaxis_title="Date",
        yaxis_title="Close",
        plot_bgcolor="white",
    )

    return fig


def sentiment_pie_chart(distribution: dict[str, int]) -> go.Figure:
    if not distribution:
        return go.Figure()

    df = pd.DataFrame([{"label": k, "count": v} for k, v in distribution.items()])

    fig = px.pie(
        df,
        values="count",
        names="label",
        color="label",
        color_discrete_map=SENT_COLORS,
        hole=0.55,
    )

    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        height=320,
        showlegend=True,
    )

    return fig
