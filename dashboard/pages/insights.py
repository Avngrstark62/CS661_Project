"""
VentureScope — Insights & Story Mode Page
Auto-generated narratives, key findings, and data stories.
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


def _empty_fig(message, height=340):
    """Styled empty-state figure shown when a filter yields no data."""
    fig = go.Figure()
    fig.update_layout(
        **apply_template(
            height=height,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        ),
        annotations=[dict(
            text=message, x=0.5, y=0.5, xref="paper", yref="paper",
            showarrow=False, font=dict(size=13, color=COLORS["text_muted"]),
        )],
    )
    return fig


def create_insights_layout():
    return html.Div(
        [
            html.Div(
                [
                    html.H1("Insights & Stories", className="page-title"),
                    html.P("Data-driven narratives from the startup ecosystem", className="page-subtitle"),
                ],
                className="page-header",
            ),
            # Key metrics summary
            html.Div(id="insights-summary", className="kpi-grid"),
            # Insight cards
            html.Div(id="insights-cards"),
            # Supporting charts
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("Success Rate by Sector", className="chart-title"),
                                    html.Span(
                                        "Bar length = % of companies acquired or IPO'd",
                                        style={"fontSize": "11px", "color": COLORS["text_muted"], "fontWeight": "400"},
                                    ),
                                ],
                                className="chart-header",
                            ),
                            dcc.Graph(id="insights-success-chart", config={"displayModeBar": False}),
                        ],
                        className="chart-container",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("Funding Concentration (Pareto)", className="chart-title"),
                                    html.Span(
                                        "Curve above diagonal = unequal distribution",
                                        style={"fontSize": "11px", "color": COLORS["text_muted"], "fontWeight": "400"},
                                    ),
                                ],
                                className="chart-header",
                            ),
                            dcc.Graph(id="insights-pareto-chart", config={"displayModeBar": False}),
                        ],
                        className="chart-container",
                    ),
                ],
                className="chart-row",
            ),
            # ── India Spotlight ─────────────────────────────────
            html.Div(
                [
                    html.H1("India Spotlight", className="page-title", style={"fontSize": "20px"}),
                    html.P(
                        "A dedicated deep-dive into the Indian startup ecosystem — all figures respect the global year range",
                        className="page-subtitle",
                    ),
                ],
                className="page-header",
                style={"marginTop": "40px", "marginBottom": "20px"},
            ),
            html.Div(id="insights-india-kpis", className="kpi-grid"),
            html.Div(id="insights-india-card"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("India Funding Over Time", className="chart-title"),
                                    html.Span(
                                        "Area = total funding raised by Indian startups per year (USD)",
                                        style={"fontSize": "11px", "color": COLORS["text_muted"], "fontWeight": "400"},
                                    ),
                                ],
                                className="chart-header",
                            ),
                            dcc.Graph(id="insights-india-timeline", config={"displayModeBar": False}),
                        ],
                        className="chart-container",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("Top Sectors in India", className="chart-title"),
                                    html.Span(
                                        "Bar length = total funding raised per sector (USD)",
                                        style={"fontSize": "11px", "color": COLORS["text_muted"], "fontWeight": "400"},
                                    ),
                                ],
                                className="chart-header",
                            ),
                            dcc.Graph(id="insights-india-sectors", config={"displayModeBar": False}),
                        ],
                        className="chart-container",
                    ),
                ],
                className="chart-row",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("Indian Startup Hubs", className="chart-title"),
                                    html.Span(
                                        "Bar length = total funding raised by startups based in each city (USD)",
                                        style={"fontSize": "11px", "color": COLORS["text_muted"], "fontWeight": "400"},
                                    ),
                                ],
                                className="chart-header",
                            ),
                            dcc.Graph(id="insights-india-cities", config={"displayModeBar": False}),
                        ],
                        className="chart-container",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("India's Share of Global Funding", className="chart-title"),
                                    html.Span(
                                        "Line = India's % of worldwide startup funding per year",
                                        style={"fontSize": "11px", "color": COLORS["text_muted"], "fontWeight": "400"},
                                    ),
                                ],
                                className="chart-header",
                            ),
                            dcc.Graph(id="insights-india-share", config={"displayModeBar": False}),
                        ],
                        className="chart-container",
                    ),
                ],
                className="chart-row",
            ),
        ],
        style={"padding": "32px", "maxWidth": "1400px", "margin": "0 auto"},
    )


def register_insights_callbacks(app, df_companies, df_funding, df_sector_summary, df_country_summary, df_investor_summary, df_investors):

    @app.callback(
        [
            Output("insights-summary", "children"),
            Output("insights-cards", "children"),
            Output("insights-success-chart", "figure"),
            Output("insights-pareto-chart", "figure"),
            Output("insights-india-kpis", "children"),
            Output("insights-india-card", "children"),
            Output("insights-india-timeline", "figure"),
            Output("insights-india-sectors", "figure"),
            Output("insights-india-cities", "figure"),
            Output("insights-india-share", "figure"),
        ],
        [
            Input("current-page", "data"),
            Input("global-year-range", "value"),
        ],
    )
    def update_insights(page, year_range):
        if page != "insights":
            return [[], [], go.Figure(), go.Figure(), [], [],
                    go.Figure(), go.Figure(), go.Figure(), go.Figure()]

        yr_min, yr_max = year_range or [1995, 2013]

        # ── Filter companies by founded year (strict cohort so every KPI
        #    responds to the global year slider) ──
        comp = df_companies[
            (df_companies["founded_year"] >= yr_min) &
            (df_companies["founded_year"] <= yr_max)
        ]

        # ── Filter funding by year range ──
        fr = df_funding[
            df_funding["funding_year"].notna() &
            (df_funding["funding_year"] >= yr_min) &
            (df_funding["funding_year"] <= yr_max)
        ]

        # ── Compute insights from filtered data ──
        total_companies = len(comp)
        funded = comp[comp["funding_total_usd"] > 0]
        total_funding = funded["funding_total_usd"].sum()
        acquired = len(comp[comp["status"] == "acquired"])
        ipo = len(comp[comp["status"] == "ipo"])
        closed = len(comp[comp["status"] == "closed"])

        # Top sector from filtered funding
        sector_totals = fr.groupby("sector")["raised_amount_usd"].sum().sort_values(ascending=False)
        top_sector = sector_totals.index[0] if len(sector_totals) > 0 else "Unknown"
        top_sector_funding = sector_totals.iloc[0] if len(sector_totals) > 0 else 0

        # Top country from filtered funding
        country_totals = fr.groupby("country")["raised_amount_usd"].sum().sort_values(ascending=False)
        top_country = country_totals.index[0] if len(country_totals) > 0 else "Unknown"

        # Top investor (by deal count) within the selected year range —
        # fund_year is precomputed once in app.py
        inv_in_range = df_investors[
            df_investors["fund_year"].notna() &
            (df_investors["fund_year"] >= yr_min) &
            (df_investors["fund_year"] <= yr_max)
        ]
        if len(inv_in_range) > 0:
            top_investor = inv_in_range.groupby("investor_name")["funding_round_id"].nunique().idxmax()
        else:
            top_investor = "Unknown"

        # Success rate
        success_rate = (acquired + ipo) / total_companies * 100 if total_companies > 0 else 0
        failure_rate = closed / total_companies * 100 if total_companies > 0 else 0

        # ── Summary KPIs ──
        summary = [
            html.Div(
                [
                    html.Div("SUCCESS RATE", className="kpi-label"),
                    html.Div(f"{success_rate:.1f}%", className="kpi-value"),
                    html.Div(
                        f"{acquired + ipo:,} exits",
                        className="kpi-change positive",
                    ),
                ],
                className="kpi-card",
            ),
            html.Div(
                [
                    html.Div("FAILURE RATE", className="kpi-label"),
                    html.Div(f"{failure_rate:.1f}%", className="kpi-value"),
                    html.Div(
                        f"{closed:,} closed",
                        className="kpi-change negative",
                    ),
                ],
                className="kpi-card",
            ),
            html.Div(
                [
                    html.Div("DOMINANT SECTOR", className="kpi-label"),
                    html.Div(top_sector[:16], className="kpi-value", style={"fontSize": "18px"}),
                    html.Div(
                        f"${top_sector_funding/1e9:.1f}B" if top_sector_funding >= 1e9 else f"${top_sector_funding/1e6:.0f}M",
                        className="kpi-change positive",
                    ),
                ],
                className="kpi-card",
            ),
            html.Div(
                [
                    html.Div("TOP ECOSYSTEM", className="kpi-label"),
                    html.Div(top_country[:16], className="kpi-value", style={"fontSize": "18px"}),
                    html.Div(
                        "#1 by funding",
                        className="kpi-change positive",
                    ),
                ],
                className="kpi-card",
            ),
        ]

        # ── Insight Cards (data-driven, no hardcoded values) ──
        # US dominance
        us_companies = len(comp[comp["country"] == "United States"])
        us_pct = us_companies / total_companies * 100 if total_companies > 0 else 0

        # Sector concentration
        top3_sectors = sector_totals.head(3)
        top3_pct = top3_sectors.sum() / total_funding * 100 if total_funding > 0 else 0
        top3_names = ", ".join(top3_sectors.index.tolist()) if len(top3_sectors) > 0 else "N/A"

        insights = [
            _create_insight_card(
                f"US Startup Dominance ({yr_min}–{yr_max})",
                f"The United States accounts for {us_pct:.0f}% of all tracked startups ({us_companies:,} companies), "
                f"making it by far the world's largest startup ecosystem. The top country by funding is "
                f"{top_country}, confirming the geographic concentration of venture capital.",
                ["Geography", "Market Share"],
                "blue",
            ),
            _create_insight_card(
                "Sector Concentration Risk",
                f"The top 3 sectors ({top3_names}) "
                f"capture {top3_pct:.0f}% of all funding. This heavy concentration means a downturn "
                f"in any single sector could significantly impact the broader ecosystem.",
                ["Sectors", "Risk"],
                "purple",
            ),
            _create_insight_card(
                "Exit Landscape",
                f"Only {success_rate:.1f}% of tracked startups have achieved a successful exit "
                f"(acquisition or IPO), while {failure_rate:.1f}% have shut down. The remaining "
                f"{100 - success_rate - failure_rate:.0f}% are still operating — a testament to "
                f"the high-risk, high-reward nature of venture capital.",
                ["Exits", "Returns"],
                "green",
            ),
            _create_insight_card(
                "Power Law of Returns",
                f"Startup funding follows a power law distribution. The top 1% of funded companies "
                f"account for a disproportionate share of total capital raised. Most startups raise "
                f"modest seed rounds, while a select few attract hundreds of millions.",
                ["Funding", "Distribution"],
                "amber",
            ),
            _create_insight_card(
                f"Investor Influence: {top_investor}",
                f"{top_investor} emerges as the most active investor by deal count, "
                f"with a diversified portfolio spanning multiple sectors and geographies. "
                f"Top-tier investors like these act as kingmakers in the startup ecosystem.",
                ["Investors", "Network"],
                "blue",
            ),
        ]

        # ── Success Rate by Sector Chart ──
        sector_status = comp.groupby("sector")["status"].value_counts().unstack(fill_value=0)
        if "acquired" in sector_status.columns and "ipo" in sector_status.columns:
            sector_status["success"] = sector_status.get("acquired", 0) + sector_status.get("ipo", 0)
        elif "acquired" in sector_status.columns:
            sector_status["success"] = sector_status["acquired"]
        else:
            sector_status["success"] = 0

        status_cols = [c for c in sector_status.columns if c not in ('success',)]
        sector_status["total"] = sector_status[status_cols].sum(axis=1)
        sector_status["success_rate"] = (sector_status["success"] / sector_status["total"] * 100).round(1)
        sector_status = sector_status.sort_values("success_rate", ascending=True)
        sector_status = sector_status[sector_status["total"] >= 50]  # Min 50 companies

        success_fig = go.Figure(
            go.Bar(
                x=sector_status["success_rate"],
                y=sector_status.index,
                orientation="h",
                marker=dict(
                    color=sector_status["success_rate"],
                    colorscale=[[0, COLORS["accent_red"]], [0.5, CHART_COLORS[4]], [1, COLORS["accent_green"]]],
                    cornerradius=4,
                    colorbar=dict(
                        title=dict(text="Rate %", font=dict(size=11, color=COLORS["text_secondary"])),
                        tickfont=dict(color=COLORS["text_muted"]),
                        len=0.8,
                    ),
                ),
                hovertemplate="<b>%{y}</b><br>Success Rate: %{x:.1f}%<br>(acquired + IPO / total)<extra></extra>",
            )
        )
        success_fig.update_layout(
            **apply_template(
                height=400,
                showlegend=False,
                xaxis_title="Exit Success Rate (%)",
            ),
        )

        # ── Pareto Chart ──
        if len(funded) > 0:
            funded_sorted = funded.sort_values("funding_total_usd", ascending=False).reset_index(drop=True)
            funded_sorted["cumulative_pct"] = funded_sorted["funding_total_usd"].cumsum() / total_funding * 100
            funded_sorted["company_pct"] = (funded_sorted.index + 1) / len(funded_sorted) * 100

            pareto_fig = go.Figure()
            pareto_fig.add_trace(
                go.Scatter(
                    x=funded_sorted["company_pct"],
                    y=funded_sorted["cumulative_pct"],
                    mode="lines",
                    fill="tozeroy",
                    line=dict(color=CHART_COLORS[0], width=2),
                    fillcolor="rgba(37, 99, 235, 0.06)",
                    name="Actual Distribution",
                    hovertemplate="Top %{x:.0f}% of companies<br>control %{y:.0f}% of funding<extra></extra>",
                )
            )
            # Add reference line (perfect equality)
            pareto_fig.add_trace(
                go.Scatter(
                    x=[0, 100],
                    y=[0, 100],
                    mode="lines",
                    line=dict(color=COLORS["text_muted"], dash="dash", width=1),
                    name="Perfect Equality",
                    hoverinfo="skip",
                )
            )
        else:
            pareto_fig = go.Figure()

        pareto_fig.update_layout(
            **apply_template(
                height=400,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis_title="% of Companies (ranked by funding)",
                yaxis_title="% of Total Funding (cumulative)",
            ),
        )

        # ── India Spotlight (fully data-driven, respects year range) ──
        india_out = _build_india_section(comp, fr, yr_min, yr_max)

        return [summary, insights, success_fig, pareto_fig] + india_out


def _normalize_indian_city(city):
    """Collapse raw-data variants of Indian city names (e.g. 'Bangalore,
    Karnataka', 'Saket,New Delhi', 'Gurgaon, Haryana') onto one metro name."""
    if pd.isna(city):
        return city
    c = str(city).lower()
    metros = [
        (("bangalore", "bengaluru"), "Bangalore"),
        (("gurgaon", "gurugram"), "Gurgaon"),
        (("delhi",), "New Delhi"),
        (("mumbai", "bombay"), "Mumbai"),
        (("hyderabad",), "Hyderabad"),
        (("chennai", "madras"), "Chennai"),
        (("pune",), "Pune"),
        (("kolkata", "calcutta"), "Kolkata"),
        (("noida",), "Noida"),
        (("ahmedabad",), "Ahmedabad"),
    ]
    for keys, name in metros:
        if any(k in c for k in keys):
            return name
    # Fallback: keep only the city part before any comma ("City, State")
    return str(city).split(",")[0].strip().title()


def _build_india_section(comp, fr, yr_min, yr_max):
    """Compute the India Spotlight KPIs, narrative card, and four charts.

    `comp` and `fr` are already filtered to the active year range.
    Returns [kpis, card, timeline_fig, sectors_fig, cities_fig, share_fig].
    """
    fr_india = fr[fr["country"] == "India"].copy()
    fr_india["city"] = fr_india["city"].apply(_normalize_indian_city)
    comp_india = comp[comp["country"] == "India"]

    if len(fr_india) == 0:
        empty = _empty_fig("No Indian funding rounds in the selected year range")
        kpis = []
        card = _create_insight_card(
            f"India ({yr_min}–{yr_max})",
            "No Indian funding rounds fall inside the selected year range. "
            "Widen the global year slider to explore India's startup story.",
            ["India", "Geography"],
            "amber",
        )
        return [kpis, card, empty, empty, empty, empty]

    # KPI values
    india_funding = fr_india["raised_amount_usd"].sum()
    india_deals = len(fr_india)
    india_companies = len(comp_india)
    india_sector_totals = fr_india.groupby("sector")["raised_amount_usd"].sum().sort_values(ascending=False)
    india_top_sector = india_sector_totals.index[0] if len(india_sector_totals) > 0 else "N/A"

    # India's rank among countries by total funding
    country_rank = fr[fr["country"] != "Unknown"].groupby("country")["raised_amount_usd"].sum().rank(
        ascending=False, method="min"
    )
    india_rank = int(country_rank.get("India", 0)) if "India" in country_rank.index else None
    global_funding = fr["raised_amount_usd"].sum()
    india_share = india_funding / global_funding * 100 if global_funding > 0 else 0

    kpis = [
        html.Div(
            [
                html.Div("INDIA TOTAL FUNDING", className="kpi-label"),
                html.Div(_fmt_currency(india_funding), className="kpi-value"),
                html.Div(f"{yr_min}–{yr_max}", className="kpi-change positive"),
            ],
            className="kpi-card",
        ),
        html.Div(
            [
                html.Div("FUNDING ROUNDS", className="kpi-label"),
                html.Div(f"{india_deals:,}", className="kpi-value"),
                html.Div(f"{india_share:.1f}% of global $", className="kpi-change positive"),
            ],
            className="kpi-card",
        ),
        html.Div(
            [
                html.Div("INDIAN STARTUPS", className="kpi-label"),
                html.Div(f"{india_companies:,}", className="kpi-value"),
                html.Div("founded in range", className="kpi-change positive"),
            ],
            className="kpi-card",
        ),
        html.Div(
            [
                html.Div("TOP SECTOR (INDIA)", className="kpi-label"),
                html.Div(india_top_sector[:16], className="kpi-value", style={"fontSize": "18px"}),
                html.Div(
                    _fmt_currency(india_sector_totals.iloc[0]) if len(india_sector_totals) > 0 else "—",
                    className="kpi-change positive",
                ),
            ],
            className="kpi-card",
        ),
    ]

    # Narrative card
    india_city_totals = (
        fr_india[fr_india["city"].notna() & (fr_india["city"] != "Unknown")]
        .groupby("city")["raised_amount_usd"].sum().sort_values(ascending=False)
    )
    top_city = india_city_totals.index[0] if len(india_city_totals) > 0 else "N/A"
    rank_text = f"ranking #{india_rank} worldwide by venture funding" if india_rank else "an emerging venture market"
    card = _create_insight_card(
        f"India's Startup Story ({yr_min}–{yr_max})",
        f"Indian startups raised {_fmt_currency(india_funding)} across {india_deals:,} funding rounds — "
        f"{india_share:.1f}% of global venture capital and {rank_text}. "
        f"{india_top_sector} leads sector funding, while {top_city} anchors the ecosystem as the top hub. "
        f"{india_companies:,} Indian startups were founded in this period.",
        ["India", "Geography", "Emerging Markets"],
        "green",
    )

    # ── Chart 1: India funding over time (area) ──
    india_tl = fr_india.groupby("funding_year").agg(
        total=("raised_amount_usd", "sum"),
        deals=("funding_round_id", "count"),
    ).reset_index().sort_values("funding_year")

    timeline_fig = go.Figure(
        go.Scatter(
            x=india_tl["funding_year"],
            y=india_tl["total"],
            mode="lines+markers",
            fill="tozeroy",
            line=dict(color=CHART_COLORS[3], width=2.5),
            marker=dict(size=5, color=CHART_COLORS[3]),
            fillcolor="rgba(5, 150, 105, 0.08)",
            customdata=india_tl["deals"],
            hovertemplate="<b>Year: %{x}</b><br>Funding: $%{y:,.0f}<br>Rounds: %{customdata}<extra></extra>",
        )
    )
    timeline_fig.update_layout(
        **apply_template(
            height=340,
            showlegend=False,
            xaxis_title="Year",
            yaxis_title="Total Funding (USD)",
            hovermode="x unified",
        ),
    )

    # ── Chart 2: Top sectors in India (h-bar) ──
    sect = india_sector_totals.head(8).sort_values(ascending=True)
    sectors_fig = go.Figure(
        go.Bar(
            x=sect.values,
            y=sect.index,
            orientation="h",
            marker=dict(
                color=sect.values,
                colorscale=[[0, CHART_COLORS[2]], [1, CHART_COLORS[3]]],
                cornerradius=4,
            ),
            hovertemplate="<b>%{y}</b><br>Funding: $%{x:,.0f}<extra></extra>",
        )
    )
    sectors_fig.update_layout(
        **apply_template(
            height=340,
            showlegend=False,
            xaxis_title="Total Funding (USD)",
        ),
    )

    # ── Chart 3: Indian startup hubs (h-bar by city funding) ──
    cities = india_city_totals.head(10).sort_values(ascending=True)
    if len(cities) > 0:
        cities_fig = go.Figure(
            go.Bar(
                x=cities.values,
                y=cities.index,
                orientation="h",
                marker=dict(
                    color=cities.values,
                    colorscale=[[0, CHART_COLORS[1]], [1, CHART_COLORS[0]]],
                    cornerradius=4,
                ),
                hovertemplate="<b>%{y}</b><br>Funding: $%{x:,.0f}<extra></extra>",
            )
        )
        cities_fig.update_layout(
            **apply_template(
                height=340,
                showlegend=False,
                xaxis_title="Total Funding (USD)",
            ),
        )
    else:
        cities_fig = _empty_fig("No city-level data for India in this range")

    # ── Chart 4: India's share of global funding per year (line %) ──
    global_tl = fr.groupby("funding_year")["raised_amount_usd"].sum()
    share_tl = (india_tl.set_index("funding_year")["total"] / global_tl * 100).dropna().reset_index()
    share_tl.columns = ["funding_year", "share_pct"]

    share_fig = go.Figure(
        go.Scatter(
            x=share_tl["funding_year"],
            y=share_tl["share_pct"],
            mode="lines+markers",
            line=dict(color=CHART_COLORS[1], width=2.5),
            marker=dict(size=5, color=CHART_COLORS[1]),
            hovertemplate="<b>Year: %{x}</b><br>India's share: %{y:.2f}%<extra></extra>",
        )
    )
    share_fig.update_layout(
        **apply_template(
            height=340,
            showlegend=False,
            xaxis_title="Year",
            yaxis_title="Share of Global Funding (%)",
            hovermode="x unified",
        ),
    )

    return [kpis, card, timeline_fig, sectors_fig, cities_fig, share_fig]


def _create_insight_card(title, body, tags, color):
    """Create a styled insight card."""
    tag_class_map = {
        "blue": "insight-tag-blue",
        "purple": "insight-tag-purple",
        "green": "insight-tag-green",
        "amber": "insight-tag-blue",
    }
    tag_els = [
        html.Span(tag, className=f"insight-tag {tag_class_map.get(color, 'insight-tag-blue')}")
        for tag in tags
    ]

    border_colors = {
        "blue": COLORS["accent_blue"],
        "purple": COLORS["accent_purple"],
        "green": COLORS["accent_green"],
        "amber": COLORS["accent_amber"],
    }

    return html.Div(
        [
            html.Div(title, className="insight-title"),
            html.Div(body, className="insight-body"),
            html.Div(tag_els, style={"marginTop": "12px"}),
        ],
        className="insight-card",
        style={"borderLeftColor": border_colors.get(color, COLORS["accent_blue"])},
    )
