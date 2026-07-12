"""
VentureScope — Overview Page (Command Center)
KPI cards, funding velocity chart, sector allocation, and geographic preview.
"""
from dash import html, dcc, Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from config import COLORS, CHART_COLORS, PLOTLY_TEMPLATE, apply_template


def _format_currency(val):
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


def _format_number(val):
    """Format numbers with commas."""
    if val >= 1e6:
        return f"{val/1e6:.1f}M"
    elif val >= 1e3:
        return f"{val/1e3:.1f}K"
    return f"{val:,.0f}"


def create_overview_layout():
    """Create the Overview page layout."""
    return html.Div(
        [
            # Page Header
            html.Div(
                [
                    html.H1("Command Center", className="page-title"),
                    html.P(
                        "Real-time overview of the global startup ecosystem",
                        className="page-subtitle",
                    ),
                ],
                className="page-header",
            ),
            # KPI Cards (will be filled by callback)
            html.Div(id="overview-kpi-grid", className="kpi-grid"),
            # Row: Funding Velocity + Sector Allocation
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("Funding Velocity", className="chart-title"),
                                    html.Span(
                                        "Y-axis: total funding raised per year (USD)",
                                        style={"fontSize": "11px", "color": COLORS["text_muted"], "fontWeight": "400"},
                                    ),
                                ],
                                className="chart-header",
                            ),
                            dcc.Graph(id="overview-velocity-chart", config={"displayModeBar": False}),
                        ],
                        className="chart-container",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("Sector Allocation", className="chart-title"),
                                    html.Span(
                                        "Slice size = share of total funding",
                                        style={"fontSize": "11px", "color": COLORS["text_muted"], "fontWeight": "400"},
                                    ),
                                ],
                                className="chart-header",
                            ),
                            dcc.Graph(id="overview-sector-chart", config={"displayModeBar": False}),
                        ],
                        className="chart-container",
                    ),
                ],
                className="chart-row",
            ),
            # Row: Geographic Heatmap + Stage Distribution
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("Global Funding Distribution", className="chart-title"),
                                    html.Span(
                                        "Color intensity = log₁₀ of total funding (USD)",
                                        style={"fontSize": "11px", "color": COLORS["text_muted"], "fontWeight": "400"},
                                    ),
                                ],
                                className="chart-header",
                            ),
                            dcc.Graph(id="overview-geo-chart", config={"displayModeBar": False}),
                        ],
                        className="chart-container",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("Funding Stage Breakdown", className="chart-title"),
                                    html.Span(
                                        "Bar length = total funding per stage",
                                        style={"fontSize": "11px", "color": COLORS["text_muted"], "fontWeight": "400"},
                                    ),
                                ],
                                className="chart-header",
                            ),
                            dcc.Graph(id="overview-stage-chart", config={"displayModeBar": False}),
                        ],
                        className="chart-container",
                    ),
                ],
                className="chart-row",
            ),
        ],
        # Removed duplicate id="page-content" — the parent in app.py already has this id
        style={"padding": "32px", "maxWidth": "1400px", "margin": "0 auto"},
    )


def register_overview_callbacks(app, df_companies, df_funding, df_sector_summary, df_timeline):
    """Register all callbacks for the Overview page."""

    @app.callback(
        [
            Output("overview-kpi-grid", "children"),
            Output("overview-velocity-chart", "figure"),
            Output("overview-sector-chart", "figure"),
            Output("overview-geo-chart", "figure"),
            Output("overview-stage-chart", "figure"),
        ],
        [Input("current-page", "data"),
         Input("global-year-range", "value")],
    )
    def update_overview(page, year_range):
        if page != "overview":
            return [[], go.Figure(), go.Figure(), go.Figure(), go.Figure()]

        yr_min, yr_max = year_range or [1995, 2013]

        # Filter funding data by year range
        mask = (
            df_funding["funding_year"].notna() &
            (df_funding["funding_year"] >= yr_min) &
            (df_funding["funding_year"] <= yr_max)
        )
        fr_filtered = df_funding[mask]

        # ── KPI Cards ──
        total_funding = fr_filtered["raised_amount_usd"].sum()
        total_deals = len(fr_filtered)
        total_companies = df_companies[
            df_companies["founded_year"].between(yr_min, yr_max)
        ]["id"].nunique() if "founded_year" in df_companies.columns else len(df_companies)
        # Average over rounds with a disclosed (>0) amount, so the KPI matches
        # the "Avg Deal Size" metric on the Funding Trends page.
        disclosed = fr_filtered[fr_filtered["raised_amount_usd"] > 0]
        avg_deal = disclosed["raised_amount_usd"].mean() if len(disclosed) > 0 else 0

        kpi_cards = [
            html.Div(
                [
                    html.Div("TOTAL FUNDING", className="kpi-label"),
                    html.Div(_format_currency(total_funding), className="kpi-value"),
                    html.Div(
                        f"{total_deals:,} deals",
                        className="kpi-change positive",
                    ),
                ],
                className="kpi-card",
            ),
            html.Div(
                [
                    html.Div("COMPANIES FOUNDED", className="kpi-label"),
                    html.Div(_format_number(total_companies), className="kpi-value"),
                    html.Div(
                        f"{yr_min}–{yr_max}",
                        className="kpi-change positive",
                    ),
                ],
                className="kpi-card",
            ),
            html.Div(
                [
                    html.Div("AVG DEAL SIZE", className="kpi-label"),
                    html.Div(_format_currency(avg_deal), className="kpi-value"),
                    html.Div(
                        "per round",
                        className="kpi-change positive",
                    ),
                ],
                className="kpi-card",
            ),
            html.Div(
                [
                    html.Div("UNIQUE SECTORS", className="kpi-label"),
                    html.Div(
                        str(fr_filtered["sector"].nunique()),
                        className="kpi-value",
                    ),
                    html.Div(
                        f"{fr_filtered['country'].nunique()} countries",
                        className="kpi-change positive",
                    ),
                ],
                className="kpi-card",
            ),
        ]

        # ── Funding Velocity (Area Chart) ──
        timeline = fr_filtered.groupby("funding_year").agg(
            total=("raised_amount_usd", "sum"),
            count=("funding_round_id", "count"),
        ).reset_index()
        timeline = timeline.sort_values("funding_year")

        velocity_fig = go.Figure()
        velocity_fig.add_trace(
            go.Scatter(
                x=timeline["funding_year"],
                y=timeline["total"],
                mode="lines+markers",
                fill="tozeroy",
                line=dict(color=CHART_COLORS[0], width=2.5),
                marker=dict(size=5, color=CHART_COLORS[0]),
                fillcolor="rgba(37, 99, 235, 0.08)",
                name="Total Funding",
                hovertemplate="<b>Year: %{x}</b><br>Funding: $%{y:,.0f}<extra></extra>",
            )
        )
        velocity_fig.update_layout(
            **apply_template(
                height=320,
                showlegend=False,
                xaxis_title="Year",
                yaxis_title="Total Funding (USD)",
                hovermode="x unified",
            ),
        )

        # ── Sector Allocation (Donut Chart) ──
        sector_data = fr_filtered.groupby("sector")["raised_amount_usd"].sum().reset_index()
        sector_data = sector_data.sort_values("raised_amount_usd", ascending=False).head(10)

        total_sector_funding = sector_data["raised_amount_usd"].sum()
        center_text = f"<b>{_format_currency(total_sector_funding)}</b><br>Top 10"

        sector_fig = go.Figure(
            go.Pie(
                labels=sector_data["sector"],
                values=sector_data["raised_amount_usd"],
                hole=0.55,
                sort=True,
                direction="clockwise",
                marker=dict(
                    colors=[CHART_COLORS[i % len(CHART_COLORS)] for i in range(len(sector_data))],
                    line=dict(color="#ffffff", width=2),
                ),
                # Percent-only labels inside slices + interactive legend for names:
                # avoids the overlapping outside-label problem for any sector count.
                textinfo="percent",
                textposition="inside",
                insidetextorientation="horizontal",
                textfont=dict(size=11, color="#ffffff"),
                hovertemplate="<b>%{label}</b><br>Funding: $%{value:,.0f}<br>Share: %{percent}<extra></extra>",
                pull=[0] * len(sector_data),  # hover popout handled in assets/interactions.js
                domain=dict(x=[0, 0.58], y=[0, 1]),
            )
        )
        sector_fig.update_layout(
            **apply_template(
                height=320,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle", y=0.5,
                    xanchor="left", x=0.62,
                    font=dict(size=11),
                    itemclick="toggle",
                    itemdoubleclick="toggleothers",
                ),
                margin=dict(l=10, r=10, t=20, b=20),
            ),
            annotations=[
                dict(
                    text=center_text,
                    x=0.29, y=0.5,  # center of the pie domain [0, 0.58]
                    xref="paper", yref="paper",
                    font=dict(size=14, color=COLORS["text_primary"]),
                    showarrow=False,
                )
            ],
        )

        # ── Geographic Heatmap (Choropleth) ──
        country_data = fr_filtered[fr_filtered["country_code"].notna()].groupby(
            ["country_code", "country"]
        )["raised_amount_usd"].sum().reset_index()

        geo_fig = go.Figure(
            go.Choropleth(
                locations=country_data["country_code"],
                text=country_data["country"],
                z=np.log10(country_data["raised_amount_usd"].clip(lower=1)),
                colorscale=[
                    [0, "#e8edf3"],
                    [0.3, "#a7c4e0"],
                    [0.6, "#4a90d9"],
                    [0.8, "#2563eb"],
                    [1.0, "#1d4ed8"],
                ],
                showscale=True,
                colorbar=dict(
                    title=dict(text="Log₁₀($)", font=dict(size=11, color=COLORS["text_secondary"])),
                    tickfont=dict(color=COLORS["text_muted"], size=10),
                    len=0.6,
                    thickness=12,
                    x=1.0,
                ),
                hovertemplate="<b>%{text}</b><br>Funding: $%{customdata:,.0f}<extra></extra>",
                customdata=country_data["raised_amount_usd"],
                marker_line_color="#d0d5dc",
                marker_line_width=0.5,
            )
        )
        geo_fig.update_layout(
            **apply_template(
                height=320,
                margin=dict(l=0, r=0, t=10, b=0),
            ),
            geo=dict(
                bgcolor="rgba(0,0,0,0)",
                lakecolor="#e8edf3",
                landcolor="#f1f3f5",
                showframe=False,
                showcoastlines=True,
                coastlinecolor="#d0d5dc",
                projection_type="natural earth",
            ),
        )

        # ── Stage Breakdown (Horizontal Bar) ──
        stage_data = fr_filtered.groupby("funding_stage")["raised_amount_usd"].sum().reset_index()
        stage_data = stage_data.sort_values("raised_amount_usd", ascending=True)

        stage_fig = go.Figure(
            go.Bar(
                x=stage_data["raised_amount_usd"],
                y=stage_data["funding_stage"],
                orientation="h",
                marker=dict(
                    color=stage_data["raised_amount_usd"],
                    colorscale=[[0, CHART_COLORS[1]], [1, CHART_COLORS[0]]],
                    cornerradius=4,
                ),
                hovertemplate="<b>%{y}</b><br>Funding: $%{x:,.0f}<extra></extra>",
            )
        )
        stage_fig.update_layout(
            **apply_template(
                height=320,
                showlegend=False,
                xaxis_title="Total Funding (USD)",
                yaxis_title="",
            ),
        )

        return [kpi_cards, velocity_fig, sector_fig, geo_fig, stage_fig]
