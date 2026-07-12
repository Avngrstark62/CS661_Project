"""
VentureScope — Funding Trends Page
Time-series deep dive: funding growth over time, round-type breakdown, sector trends.
"""
from dash import html, dcc, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from config import COLORS, CHART_COLORS, PLOTLY_TEMPLATE, apply_template


def create_funding_layout():
    """Create the Funding Trends page layout."""
    return html.Div(
        [
            html.Div(
                [
                    html.H1("Funding Trends", className="page-title"),
                    html.P("Track how startup funding has evolved over time", className="page-subtitle"),
                ],
                className="page-header",
            ),
            # Main timeline chart
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("Funding Over Time", className="chart-title"),
                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id="funding-metric-select",
                                        options=[
                                            {"label": "Total Funding ($)", "value": "total_funding"},
                                            {"label": "Deal Count", "value": "deal_count"},
                                            {"label": "Avg Deal Size ($)", "value": "avg_deal_size"},
                                        ],
                                        value="total_funding",
                                        clearable=False,
                                        style={"width": "200px"},
                                    ),
                                ],
                                className="chart-controls",
                            ),
                        ],
                        className="chart-header",
                    ),
                    dcc.Graph(id="funding-timeline-chart", config={"displayModeBar": False}),
                ],
                className="chart-container chart-full",
            ),
            # Row: Stage breakdown + Sector trends
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("Funding by Stage Over Time", className="chart-title"),
                                    html.Span(
                                        "Stacked area = funding per round type",
                                        style={"fontSize": "11px", "color": COLORS["text_muted"], "fontWeight": "400"},
                                    ),
                                ],
                                className="chart-header",
                            ),
                            dcc.Graph(id="funding-stage-chart", config={"displayModeBar": False}),
                        ],
                        className="chart-container",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("Top Sectors Over Time", className="chart-title"),
                                    html.Span(
                                        "Lines = top 6 sectors by total funding",
                                        style={"fontSize": "11px", "color": COLORS["text_muted"], "fontWeight": "400"},
                                    ),
                                ],
                                className="chart-header",
                            ),
                            dcc.Graph(id="funding-sector-trend-chart", config={"displayModeBar": False}),
                        ],
                        className="chart-container",
                    ),
                ],
                className="chart-row",
            ),
            # Year-over-Year growth
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("Year-over-Year Growth Rate", className="chart-title"),
                            html.Span(
                                "Green = positive growth, Red = decline",
                                style={"fontSize": "11px", "color": COLORS["text_muted"], "fontWeight": "400"},
                            ),
                        ],
                        className="chart-header",
                    ),
                    dcc.Graph(id="funding-yoy-chart", config={"displayModeBar": False}),
                ],
                className="chart-container chart-full",
            ),
        ],
        style={"padding": "32px", "maxWidth": "1400px", "margin": "0 auto"},
    )


def register_funding_callbacks(app, df_funding, df_stage_year, df_sector_year, df_timeline):
    """Register all callbacks for the Funding Trends page."""

    @app.callback(
        [
            Output("funding-timeline-chart", "figure"),
            Output("funding-stage-chart", "figure"),
            Output("funding-sector-trend-chart", "figure"),
            Output("funding-yoy-chart", "figure"),
        ],
        [
            Input("current-page", "data"),
            Input("global-year-range", "value"),
            Input("funding-metric-select", "value"),
        ],
    )
    def update_funding_page(page, year_range, metric):
        if page != "funding":
            return [go.Figure()] * 4

        yr_min, yr_max = year_range or [1995, 2013]

        # Filter timeline
        tl = df_timeline[
            (df_timeline["funding_year"] >= yr_min) &
            (df_timeline["funding_year"] <= yr_max)
        ].sort_values("funding_year")

        # ── Main Timeline ──
        y_col = metric or "total_funding"
        y_labels = {
            "total_funding": "Total Funding (USD)",
            "deal_count": "Number of Deals",
            "avg_deal_size": "Average Deal Size (USD)",
        }

        timeline_fig = go.Figure()
        timeline_fig.add_trace(
            go.Scatter(
                x=tl["funding_year"],
                y=tl[y_col],
                mode="lines+markers",
                line=dict(color=CHART_COLORS[0], width=3),
                marker=dict(size=6, color=CHART_COLORS[0]),
                fill="tozeroy",
                fillcolor="rgba(59, 130, 246, 0.08)",
                hovertemplate=f"<b>Year: %{{x}}</b><br>{y_labels[y_col]}: %{{y:,.0f}}<extra></extra>",
            )
        )
        timeline_fig.update_layout(
            **apply_template(
                height=350,
                showlegend=False,
                xaxis_title="Year",
                yaxis_title=y_labels[y_col],
                hovermode="x unified",
            ),
        )

        # ── Stage Breakdown (Stacked Area) — Fixed stage order to match data ──
        stage_data = df_stage_year[
            (df_stage_year["funding_year"] >= yr_min) &
            (df_stage_year["funding_year"] <= yr_max)
        ].copy()

        # Use the actual stages from the data, ordered logically
        stage_order = ["Angel", "Venture", "Series A", "Series B", "Series C+", "Private Equity", "Crowdfunding", "Post-IPO", "Other"]
        # Filter to only stages that exist in data
        available_stages = stage_data["funding_stage"].unique()
        stage_order = [s for s in stage_order if s in available_stages]

        stage_fig = go.Figure()
        for i, stage in enumerate(stage_order):
            sd = stage_data[stage_data["funding_stage"] == stage].sort_values("funding_year")
            if len(sd) > 0:
                stage_fig.add_trace(
                    go.Scatter(
                        x=sd["funding_year"],
                        y=sd["total_funding"],
                        mode="lines",
                        name=stage,
                        stackgroup="one",
                        line=dict(width=0.5, color=CHART_COLORS[i % len(CHART_COLORS)]),
                        hovertemplate=f"<b>{stage}</b><br>Year: %{{x}}<br>Funding: $%{{y:,.0f}}<extra></extra>",
                    )
                )

        stage_fig.update_layout(
            **apply_template(
                height=350,
                xaxis_title="Year",
                yaxis_title="Total Funding (USD)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            ),
        )

        # ── Sector Trends (Multi-line) ──
        sector_data = df_sector_year[
            (df_sector_year["funding_year"] >= yr_min) &
            (df_sector_year["funding_year"] <= yr_max)
        ].copy()

        # Top 6 sectors by total funding
        top_sectors = sector_data.groupby("sector")["total_funding"].sum().nlargest(6).index.tolist()

        sector_fig = go.Figure()
        for i, sector in enumerate(top_sectors):
            sd = sector_data[sector_data["sector"] == sector].sort_values("funding_year")
            sector_fig.add_trace(
                go.Scatter(
                    x=sd["funding_year"],
                    y=sd["total_funding"],
                    mode="lines+markers",
                    name=sector,
                    line=dict(color=CHART_COLORS[i], width=2),
                    marker=dict(size=4),
                    hovertemplate=f"<b>{sector}</b><br>Year: %{{x}}<br>Funding: $%{{y:,.0f}}<extra></extra>",
                )
            )

        sector_fig.update_layout(
            **apply_template(
                height=350,
                xaxis_title="Year",
                yaxis_title="Total Funding (USD)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            ),
        )

        # ── YoY Growth ──
        if len(tl) > 1:
            tl_growth = tl.copy()
            tl_growth["yoy_growth"] = tl_growth["total_funding"].pct_change() * 100

            # Green = positive growth, Red = decline (matches the chart caption)
            colors = [COLORS["accent_green"] if v >= 0 else COLORS["accent_red"]
                      for v in tl_growth["yoy_growth"].fillna(0)]

            yoy_fig = go.Figure(
                go.Bar(
                    x=tl_growth["funding_year"],
                    y=tl_growth["yoy_growth"],
                    marker=dict(color=colors, cornerradius=4),
                    hovertemplate="<b>Year: %{x}</b><br>YoY Growth: %{y:.1f}%<extra></extra>",
                )
            )
        else:
            yoy_fig = go.Figure()

        yoy_fig.update_layout(
            **apply_template(
                height=280,
                showlegend=False,
                xaxis_title="Year",
                yaxis_title="Year-over-Year Growth (%)",
            ),
        )
        yoy_fig.add_hline(y=0, line_color=COLORS["text_muted"], line_dash="dash", line_width=1)

        return [timeline_fig, stage_fig, sector_fig, yoy_fig]
