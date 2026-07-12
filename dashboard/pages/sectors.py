"""
VentureScope — Sector Intelligence Page
Treemap, sector comparison, and sector lifecycle analysis.
"""
from dash import html, dcc, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from config import COLORS, CHART_COLORS, PLOTLY_TEMPLATE, apply_template


def create_sectors_layout():
    return html.Div(
        [
            html.Div(
                [
                    html.H1("Sector Intelligence", className="page-title"),
                    html.P("Analyze funding allocation across startup sectors", className="page-subtitle"),
                ],
                className="page-header",
            ),
            # Treemap
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("Sector Allocation Treemap", className="chart-title"),
                            html.Span(
                                "Tile area = total funding, Color = sector identity",
                                style={"fontSize": "11px", "color": COLORS["text_muted"], "fontWeight": "400"},
                            ),
                        ],
                        className="chart-header",
                    ),
                    dcc.Graph(id="sectors-treemap", config={"displayModeBar": False}),
                ],
                className="chart-container chart-full",
            ),
            # Row: Sector comparison bar + Sector donut
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("Sector Comparison", className="chart-title"),
                                    html.Div(
                                        [
                                            dcc.Dropdown(
                                                id="sector-compare-metric",
                                                options=[
                                                    {"label": "Total Funding", "value": "total_funding"},
                                                    {"label": "Company Count", "value": "company_count"},
                                                    {"label": "Avg Funding", "value": "avg_funding"},
                                                ],
                                                value="total_funding",
                                                clearable=False,
                                                style={"width": "180px"},
                                            ),
                                        ],
                                        className="chart-controls",
                                    ),
                                ],
                                className="chart-header",
                            ),
                            dcc.Graph(id="sectors-comparison", config={"displayModeBar": False}),
                        ],
                        className="chart-container",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("Company Status by Sector", className="chart-title"),
                                    html.Span(
                                        "Stacked bars show operating, acquired, IPO, closed",
                                        style={"fontSize": "11px", "color": COLORS["text_muted"], "fontWeight": "400"},
                                    ),
                                ],
                                className="chart-header",
                            ),
                            dcc.Graph(id="sectors-status-chart", config={"displayModeBar": False}),
                        ],
                        className="chart-container",
                    ),
                ],
                className="chart-row",
            ),
            # Sector growth over time
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("Sector Growth Trajectory", className="chart-title"),
                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id="sector-growth-select",
                                        options=[],  # Filled by callback
                                        value=None,
                                        multi=True,
                                        placeholder="Select sectors to compare...",
                                        style={"width": "400px"},
                                    ),
                                ],
                                className="chart-controls",
                            ),
                        ],
                        className="chart-header",
                    ),
                    dcc.Graph(id="sectors-growth-chart", config={"displayModeBar": False}),
                ],
                className="chart-container chart-full",
            ),
        ],
        style={"padding": "32px", "maxWidth": "1400px", "margin": "0 auto"},
    )


def register_sectors_callbacks(app, df_companies, df_funding, df_sector_summary, df_sector_year):

    @app.callback(
        [
            Output("sectors-treemap", "figure"),
            Output("sectors-comparison", "figure"),
            Output("sectors-status-chart", "figure"),
            Output("sectors-growth-chart", "figure"),
            Output("sector-growth-select", "options"),
        ],
        [
            Input("current-page", "data"),
            Input("global-year-range", "value"),
            Input("sector-compare-metric", "value"),
            Input("sector-growth-select", "value"),
        ],
    )
    def update_sectors(page, year_range, metric, selected_sectors):
        if page != "sectors":
            return [go.Figure()] * 4 + [[]]

        yr_min, yr_max = year_range or [1995, 2013]

        # Filter
        fr = df_funding[
            (df_funding["funding_year"] >= yr_min) &
            (df_funding["funding_year"] <= yr_max) &
            df_funding["sector"].notna()
        ]

        # ── Treemap ──
        sector_totals = fr.groupby("sector").agg(
            funding=("raised_amount_usd", "sum"),
            deals=("funding_round_id", "count"),
            companies=("object_id", "nunique"),
        ).reset_index()
        sector_totals = sector_totals[sector_totals["funding"] > 0]
        sector_totals["avg_funding"] = (sector_totals["funding"] / sector_totals["companies"]).round(0)
        sector_totals["funding_label"] = sector_totals["funding"].apply(
            lambda x: f"${x/1e9:.1f}B" if x >= 1e9 else f"${x/1e6:.0f}M"
        )

        treemap_fig = go.Figure(
            go.Treemap(
                labels=sector_totals["sector"],
                parents=[""] * len(sector_totals),
                values=sector_totals["funding"],
                customdata=np.stack([
                    sector_totals["deals"],
                    sector_totals["funding_label"],
                    sector_totals["companies"],
                ], axis=-1),
                texttemplate="<b>%{label}</b><br>%{customdata[1]}<br>%{customdata[0]} deals",
                textfont=dict(size=13),
                marker=dict(
                    colors=[CHART_COLORS[i % len(CHART_COLORS)] for i in range(len(sector_totals))],
                    line=dict(color=COLORS["bg_primary"], width=2),
                ),
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Funding: %{customdata[1]}<br>"
                    "Deals: %{customdata[0]}<br>"
                    "Companies: %{customdata[2]}"
                    "<extra></extra>"
                ),
            )
        )
        treemap_fig.update_layout(
            **apply_template(
                height=400,
                margin=dict(l=10, r=10, t=10, b=10),
            ),
        )

        # ── Sector Comparison Bar — Fixed: correctly handle all 3 metrics ──
        comp_metric = metric or "total_funding"

        if comp_metric == "total_funding":
            comp_data = sector_totals.sort_values("funding", ascending=True).tail(12)
            bar_vals = comp_data["funding"]
            x_title = "Total Funding (USD)"
            hover_tpl = "<b>%{y}</b><br>$%{x:,.0f}<extra></extra>"
        elif comp_metric == "company_count":
            comp_data = sector_totals.sort_values("companies", ascending=True).tail(12)
            bar_vals = comp_data["companies"]
            x_title = "Company Count"
            hover_tpl = "<b>%{y}</b><br>%{x:,.0f} companies<extra></extra>"
        else:  # avg_funding
            comp_data = sector_totals.sort_values("avg_funding", ascending=True).tail(12)
            bar_vals = comp_data["avg_funding"]
            x_title = "Average Funding per Company (USD)"
            hover_tpl = "<b>%{y}</b><br>$%{x:,.0f}<extra></extra>"

        comp_fig = go.Figure(
            go.Bar(
                x=bar_vals,
                y=comp_data["sector"],
                orientation="h",
                marker=dict(
                    color=bar_vals,
                    colorscale=[[0, CHART_COLORS[2]], [1, CHART_COLORS[0]]],
                    cornerradius=4,
                ),
                hovertemplate=hover_tpl,
            )
        )
        comp_fig.update_layout(
            **apply_template(
                height=380,
                showlegend=False,
                xaxis_title=x_title,
            ),
        )

        # ── Status by Sector (Stacked Bar) — cohort of companies founded in range ──
        companies_filtered = df_companies[
            df_companies["sector"].notna() &
            df_companies["status"].isin(["operating", "acquired", "closed", "ipo"])
        ]
        # Strict year filter (companies without a founding year are excluded) so
        # the chart responds to the global year slider in real time.
        if "founded_year" in companies_filtered.columns:
            companies_filtered = companies_filtered[
                (companies_filtered["founded_year"] >= yr_min) &
                (companies_filtered["founded_year"] <= yr_max)
            ]

        status_data = companies_filtered.groupby(["sector", "status"]).size().reset_index(name="count")
        top_sectors = companies_filtered["sector"].value_counts().head(10).index.tolist()
        status_data = status_data[status_data["sector"].isin(top_sectors)]

        status_colors = {
            "operating": CHART_COLORS[4],
            "acquired": CHART_COLORS[0],
            "ipo": CHART_COLORS[2],
            "closed": COLORS["accent_red"],
        }
        status_fig = go.Figure()
        for status in ["operating", "acquired", "ipo", "closed"]:
            sd = status_data[status_data["status"] == status]
            status_fig.add_trace(
                go.Bar(
                    x=sd["sector"],
                    y=sd["count"],
                    name=status.title(),
                    marker=dict(color=status_colors.get(status, COLORS["text_muted"])),
                    hovertemplate="<b>%{x}</b><br>" + status.title() + ": %{y:,}<extra></extra>",
                )
            )
        status_fig.update_layout(
            **apply_template(
                barmode="stack",
                height=380,
                xaxis_tickangle=-45,
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            ),
        )

        # ── Sector Growth ──
        all_sectors = sorted(df_sector_year["sector"].unique())
        sector_options = [{"label": s, "value": s} for s in all_sectors]

        growth_sectors = selected_sectors or all_sectors[:5]
        growth_data = df_sector_year[
            (df_sector_year["funding_year"] >= yr_min) &
            (df_sector_year["funding_year"] <= yr_max) &
            (df_sector_year["sector"].isin(growth_sectors))
        ]

        growth_fig = go.Figure()
        for i, sector in enumerate(growth_sectors):
            sd = growth_data[growth_data["sector"] == sector].sort_values("funding_year")
            growth_fig.add_trace(
                go.Scatter(
                    x=sd["funding_year"],
                    y=sd["total_funding"],
                    name=sector,
                    mode="lines+markers",
                    line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=2),
                    marker=dict(size=5),
                    hovertemplate=f"<b>{sector}</b><br>Year: %{{x}}<br>Funding: $%{{y:,.0f}}<extra></extra>",
                )
            )
        growth_fig.update_layout(
            **apply_template(
                height=350,
                xaxis_title="Year",
                yaxis_title="Total Funding (USD)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            ),
        )

        return [treemap_fig, comp_fig, status_fig, growth_fig, sector_options]
