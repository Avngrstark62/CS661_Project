"""
VentureScope — Investor Network Page
Investor rankings, investor × sector heatmap, portfolio analysis.
"""
from dash import html, dcc, Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from config import COLORS, CHART_COLORS, PLOTLY_TEMPLATE, apply_template


def _fmt_currency(val):
    """Format large numbers as currency strings."""
    if val >= 1e12:
        return f"${val/1e12:.1f}T"
    elif val >= 1e9:
        return f"${val/1e9:.1f}B"
    elif val >= 1e6:
        return f"${val/1e6:.1f}M"
    elif val >= 1e3:
        return f"${val/1e3:.0f}K"
    return f"${val:.0f}"


def create_investors_layout():
    return html.Div(
        [
            html.Div(
                [
                    html.H1("Investor Intelligence", className="page-title"),
                    html.P("Analyze investor behavior, sector preferences, and deal patterns", className="page-subtitle"),
                ],
                className="page-header",
            ),
            # KPI row for investors
            html.Div(id="investor-kpis", className="kpi-grid"),
            # Investor × Sector Heatmap
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("Investor × Sector Heatmap", className="chart-title"),
                            html.Span(
                                "Color intensity = number of deals per investor-sector pair",
                                style={
                                    "fontSize": "11px", "color": COLORS["text_muted"],
                                    "fontWeight": "400",
                                },
                            ),
                        ],
                        className="chart-header",
                    ),
                    dcc.Graph(id="investor-heatmap", config={"displayModeBar": False}),
                ],
                className="chart-container chart-full",
            ),
            # Row: Top investors + Deal size distribution
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("Top Investors by Deal Count", className="chart-title"),
                                    html.Span(
                                        "Bar length = total unique deals",
                                        style={"fontSize": "11px", "color": COLORS["text_muted"], "fontWeight": "400"},
                                    ),
                                ],
                                className="chart-header",
                            ),
                            dcc.Graph(id="investor-ranking", config={"displayModeBar": False}),
                        ],
                        className="chart-container",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("Investment Size Distribution", className="chart-title"),
                                    html.Span(
                                        "X-axis: log₁₀ scale of avg deal size (USD)",
                                        style={"fontSize": "11px", "color": COLORS["text_muted"], "fontWeight": "400"},
                                    ),
                                ],
                                className="chart-header",
                            ),
                            dcc.Graph(id="investor-deal-dist", config={"displayModeBar": False}),
                        ],
                        className="chart-container",
                    ),
                ],
                className="chart-row",
            ),
        ],
        style={"padding": "32px", "maxWidth": "1400px", "margin": "0 auto"},
    )


def register_investors_callbacks(app, df_investors, df_investor_summary, df_inv_sector):

    @app.callback(
        [
            Output("investor-kpis", "children"),
            Output("investor-heatmap", "figure"),
            Output("investor-ranking", "figure"),
            Output("investor-deal-dist", "figure"),
        ],
        [
            Input("current-page", "data"),
            Input("global-year-range", "value"),
        ],
    )
    def update_investors(page, year_range):
        if page != "investors":
            return [[], go.Figure(), go.Figure(), go.Figure()]

        yr_min, yr_max = year_range or [1995, 2013]

        # ── Filter investors by year range ──
        # fund_year / raised_amount_usd are precomputed once in app.py
        inv_filtered = df_investors[
            df_investors["fund_year"].notna() &
            (df_investors["fund_year"] >= yr_min) &
            (df_investors["fund_year"] <= yr_max)
        ]

        # Recompute investor summary from filtered data
        inv_summary = inv_filtered.groupby("investor_name").agg(
            total_investments=("raised_amount_usd", "sum"),
            deal_count=("funding_round_id", "nunique"),
            avg_deal_size=("raised_amount_usd", "mean"),
        ).round(0).reset_index()
        inv_summary = inv_summary.sort_values("total_investments", ascending=False)

        # ── KPIs ──
        total_investors = inv_summary["investor_name"].nunique()
        total_invested = inv_summary["total_investments"].sum()
        avg_deals = inv_summary["deal_count"].mean() if len(inv_summary) > 0 else 0
        # KPI is captioned "by deal count" — rank by deals, not by total invested
        top_investor = (
            inv_summary.loc[inv_summary["deal_count"].idxmax(), "investor_name"]
            if len(inv_summary) > 0 else "N/A"
        )

        kpis = [
            html.Div(
                [
                    html.Div("ACTIVE INVESTORS", className="kpi-label"),
                    html.Div(f"{total_investors:,}", className="kpi-value"),
                    html.Div(f"{yr_min}–{yr_max}", className="kpi-change positive"),
                ],
                className="kpi-card",
            ),
            html.Div(
                [
                    html.Div("TOTAL INVESTED", className="kpi-label"),
                    html.Div(_fmt_currency(total_invested), className="kpi-value"),
                    html.Div("cumulative", className="kpi-change positive"),
                ],
                className="kpi-card",
            ),
            html.Div(
                [
                    html.Div("AVG DEALS/INVESTOR", className="kpi-label"),
                    html.Div(f"{avg_deals:.0f}", className="kpi-value"),
                    html.Div("deals avg", className="kpi-change positive"),
                ],
                className="kpi-card",
            ),
            html.Div(
                [
                    html.Div("TOP INVESTOR", className="kpi-label"),
                    html.Div(
                        top_investor[:18],
                        className="kpi-value",
                        style={"fontSize": "18px"},
                    ),
                    html.Div(
                        "by deal count",
                        className="kpi-change positive",
                    ),
                ],
                className="kpi-card",
            ),
        ]

        # ── Heatmap (Investor × Sector) — recomputed from year-filtered data ──
        # 'sector' is mapped onto each investment once in app.py, so the heatmap
        # reflects the active year range instead of the static all-time matrix.
        active_investors = inv_summary.nlargest(20, "deal_count")["investor_name"].tolist()
        hm_source = inv_filtered[
            inv_filtered["investor_name"].isin(active_investors) &
            inv_filtered["sector"].notna() &
            (inv_filtered["sector"] != "Other")
        ]

        if len(hm_source) > 0 and len(active_investors) > 0:
            hm_data = hm_source.groupby(["investor_name", "sector"]).agg(
                deal_count=("funding_round_id", "nunique"),
            ).reset_index()
            if len(hm_data) > 0:
                pivot = hm_data.pivot_table(
                    index="investor_name",
                    columns="sector",
                    values="deal_count",
                    fill_value=0,
                )
                # Remove sectors with very few deals
                pivot = pivot.loc[:, pivot.sum() > 3]
                # Order investors by total deals (most active at top)
                pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=True).index]

                heatmap_fig = go.Figure(
                    go.Heatmap(
                        z=pivot.values,
                        x=pivot.columns.tolist(),
                        y=pivot.index.tolist(),
                        colorscale=[
                            [0, "#f8f9fb"],
                            [0.2, "#dbeafe"],
                            [0.5, "#60a5fa"],
                            [0.8, "#2563eb"],
                            [1.0, "#1e40af"],
                        ],
                        showscale=True,
                        colorbar=dict(
                            title=dict(text="Deals", font=dict(color=COLORS["text_secondary"], size=12)),
                            tickfont=dict(color=COLORS["text_muted"]),
                            len=0.8,
                        ),
                        hovertemplate="Investor: %{y}<br>Sector: %{x}<br>Deals: %{z}<extra></extra>",
                    )
                )
                heatmap_fig.update_layout(
                    **apply_template(
                        height=500,
                        xaxis=dict(side="bottom", tickangle=-45),
                        margin=dict(l=200, r=50, t=20, b=100),
                    ),
                )
            else:
                heatmap_fig = _empty_fig("No investor–sector deals in the selected year range")
        else:
            heatmap_fig = _empty_fig("No investor–sector deals in the selected year range")

        # ── Investor Ranking ──
        top20 = inv_summary.nlargest(20, "deal_count").sort_values("deal_count", ascending=True)

        ranking_fig = go.Figure(
            go.Bar(
                x=top20["deal_count"],
                y=top20["investor_name"],
                orientation="h",
                marker=dict(
                    color=top20["deal_count"],
                    colorscale=[[0, CHART_COLORS[1]], [1, CHART_COLORS[0]]],
                    cornerradius=4,
                ),
                hovertemplate="<b>%{y}</b><br>Deals: %{x:,}<extra></extra>",
            )
        )
        ranking_fig.update_layout(
            **apply_template(
                height=450,
                showlegend=False,
                xaxis_title="Number of Deals",
                margin=dict(l=180),
            ),
        )

        # ── Deal Size Distribution ──
        deal_sizes = inv_summary["avg_deal_size"].dropna()
        deal_sizes = deal_sizes[deal_sizes > 0]

        dist_fig = go.Figure(
            go.Histogram(
                x=np.log10(deal_sizes.clip(lower=1)),
                nbinsx=30,
                marker=dict(
                    color=CHART_COLORS[2],
                    line=dict(color=COLORS["border"], width=1),
                ),
                hovertemplate="Log₁₀(Avg Deal Size): %{x:.1f}<br>Count: %{y}<extra></extra>",
            )
        )
        dist_fig.update_layout(
            **apply_template(
                height=450,
                showlegend=False,
                xaxis_title="Log₁₀(Average Deal Size USD)",
                yaxis_title="Number of Investors",
            ),
        )

        return [kpis, heatmap_fig, ranking_fig, dist_fig]


def _empty_fig(message):
    """Styled empty-state figure shown when a filter yields no data."""
    fig = go.Figure()
    fig.update_layout(
        **apply_template(
            height=300,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        ),
        annotations=[dict(
            text=message, x=0.5, y=0.5, xref="paper", yref="paper",
            showarrow=False, font=dict(size=13, color=COLORS["text_muted"]),
        )],
    )
    return fig
