"""
VentureScope — Geographic Analytics Page
Choropleth map, city-level bubbles, country rankings.
"""
from dash import html, dcc, Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from config import COLORS, CHART_COLORS, PLOTLY_TEMPLATE, apply_template


def create_geo_layout():
    return html.Div(
        [
            html.Div(
                [
                    html.H1("Geo Analytics", className="page-title"),
                    html.P("Explore the global distribution of startup activity", className="page-subtitle"),
                ],
                className="page-header",
            ),
            # Main choropleth
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("Global Startup Funding Distribution", className="chart-title"),
                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id="geo-metric",
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
                    dcc.Graph(id="geo-choropleth", config={"displayModeBar": False}),
                ],
                className="chart-container chart-full",
            ),
            # Row: Country ranking + City bubbles
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("Top Countries by Funding", className="chart-title"),
                                    html.Span(
                                        "Bar length = total funding or count",
                                        style={"fontSize": "11px", "color": COLORS["text_muted"], "fontWeight": "400"},
                                    ),
                                ],
                                className="chart-header",
                            ),
                            dcc.Graph(id="geo-country-ranking", config={"displayModeBar": False}),
                        ],
                        className="chart-container",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("Startup Hotspot Cities", className="chart-title"),
                                    html.Span(
                                        "Bubble size = offices of startups funded in the selected years",
                                        style={"fontSize": "11px", "color": COLORS["text_muted"], "fontWeight": "400"},
                                    ),
                                ],
                                className="chart-header",
                            ),
                            dcc.Graph(id="geo-city-bubbles", config={"displayModeBar": False}),
                        ],
                        className="chart-container",
                    ),
                ],
                className="chart-row",
            ),
            # Region comparison
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("Regional Ecosystem Comparison", className="chart-title"),
                            html.Span(
                                "Bars = funding (left axis), Line = company count (right axis)",
                                style={"fontSize": "11px", "color": COLORS["text_muted"], "fontWeight": "400"},
                            ),
                        ],
                        className="chart-header",
                    ),
                    dcc.Graph(id="geo-region-chart", config={"displayModeBar": False}),
                ],
                className="chart-container chart-full",
            ),
        ],
        style={"padding": "32px", "maxWidth": "1400px", "margin": "0 auto"},
    )


def register_geo_callbacks(app, df_companies, df_funding, df_country_summary, df_offices, df_country_year):

    @app.callback(
        [
            Output("geo-choropleth", "figure"),
            Output("geo-country-ranking", "figure"),
            Output("geo-city-bubbles", "figure"),
            Output("geo-region-chart", "figure"),
        ],
        [
            Input("current-page", "data"),
            Input("global-year-range", "value"),
            Input("geo-metric", "value"),
        ],
    )
    def update_geo(page, year_range, metric):
        if page != "geo":
            return [go.Figure()] * 4

        yr_min, yr_max = year_range or [1995, 2013]

        # Rounds inside the selected year window (all countries — used for cities)
        fr_in_range = df_funding[
            df_funding["funding_year"].notna() &
            (df_funding["funding_year"] >= yr_min) &
            (df_funding["funding_year"] <= yr_max)
        ]

        # ── Dynamically compute country summary from filtered funding data ──
        fr_filtered = fr_in_range[
            fr_in_range["country_code"].notna() &
            (fr_in_range["country"] != "Unknown")
        ]

        cs = fr_filtered.groupby(["country", "country_code"]).agg(
            total_funding=("raised_amount_usd", "sum"),
            company_count=("object_id", "nunique"),
            avg_funding=("raised_amount_usd", "mean"),
        ).round(0).reset_index()

        # Add world_region from the pre-aggregated summary
        region_map = df_country_summary.set_index("country")["world_region"].to_dict()
        cs["world_region"] = cs["country"].map(region_map).fillna("Other")

        cs = cs[cs["total_funding"] > 0]

        # ── Choropleth ──
        z_col = metric or "total_funding"
        z_vals = cs[z_col].clip(lower=1)

        metric_labels = {
            "total_funding": "Total Funding (USD)",
            "company_count": "Companies",
            "avg_funding": "Avg Funding (USD)",
        }

        choropleth = go.Figure(
            go.Choropleth(
                locations=cs["country_code"],
                z=np.log10(z_vals),
                text=cs["country"],
                customdata=np.stack([cs["total_funding"], cs["company_count"], cs["avg_funding"]], axis=-1),
                colorscale=[
                    [0, "#e8edf3"],
                    [0.2, "#a7c4e0"],
                    [0.4, "#4a90d9"],
                    [0.6, "#2563eb"],
                    [0.8, "#1d4ed8"],
                    [1.0, "#1e40af"],
                ],
                showscale=True,
                colorbar=dict(
                    title=dict(
                        text=f"Log₁₀({metric_labels.get(z_col, 'Value')})",
                        font=dict(size=11, color=COLORS["text_secondary"]),
                    ),
                    tickfont=dict(color=COLORS["text_muted"], size=10),
                    len=0.7,
                    thickness=12,
                ),
                marker_line_color="#d0d5dc",
                marker_line_width=0.5,
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Total Funding: $%{customdata[0]:,.0f}<br>"
                    "Companies: %{customdata[1]:,.0f}<br>"
                    "Avg Funding: $%{customdata[2]:,.0f}"
                    "<extra></extra>"
                ),
            )
        )
        choropleth.update_layout(
            **apply_template(
                height=450,
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
                showocean=True,
                oceancolor="#f8f9fb",
            ),
        )

        # ── Country Ranking (Top 15) ──
        top_countries = cs.nlargest(15, z_col).sort_values(z_col, ascending=True)

        # Format hover based on metric
        if z_col == "total_funding" or z_col == "avg_funding":
            hover_tpl = "<b>%{y}</b><br>$%{x:,.0f}<extra></extra>"
        else:
            hover_tpl = "<b>%{y}</b><br>%{x:,.0f} companies<extra></extra>"

        ranking_fig = go.Figure(
            go.Bar(
                x=top_countries[z_col],
                y=top_countries["country"],
                orientation="h",
                marker=dict(
                    color=top_countries[z_col],
                    colorscale=[[0, CHART_COLORS[2]], [1, CHART_COLORS[0]]],
                    cornerradius=4,
                ),
                hovertemplate=hover_tpl,
            )
        )
        ranking_fig.update_layout(
            **apply_template(
                height=400,
                showlegend=False,
                xaxis_title=metric_labels.get(z_col, "Total Funding"),
            ),
        )

        # ── City Bubbles (Scatter Geo) — offices of companies funded in range ──
        # Filter out (0,0) coordinates which are invalid/missing data, and keep
        # only offices of companies that raised a round in the selected years so
        # the map responds to the global year slider in real time.
        funded_ids = fr_in_range["object_id"].unique()
        valid_offices = df_offices[
            ((df_offices["latitude"].abs() > 0.1) | (df_offices["longitude"].abs() > 0.1)) &
            df_offices["object_id"].isin(funded_ids)
        ]
        city_data = valid_offices.groupby(["city", "country"]).agg(
            office_count=("object_id", "size"),
            latitude=("latitude", "median"),
            longitude=("longitude", "median"),
        ).reset_index()
        city_data = city_data[
            city_data["city"].notna() &
            (city_data["office_count"] >= 2)
        ].nlargest(100, "office_count")

        city_fig = go.Figure(
            go.Scattergeo(
                lat=city_data["latitude"],
                lon=city_data["longitude"],
                text=city_data.apply(lambda r: f"{r['city']}, {r['country']}", axis=1),
                customdata=city_data["office_count"],  # actual count for tooltip
                marker=dict(
                    size=np.sqrt(city_data["office_count"]) * 2,
                    color=city_data["office_count"],
                    colorscale=[[0, "rgba(37,99,235,0.25)"], [1, "rgba(37,99,235,0.85)"]],
                    line=dict(width=0.5, color="rgba(37,99,235,0.4)"),
                    sizemode="diameter",
                    colorbar=dict(
                        title=dict(text="Offices", font=dict(size=11, color=COLORS["text_secondary"])),
                        tickfont=dict(color=COLORS["text_muted"], size=10),
                        len=0.5,
                        thickness=10,
                        x=1.0,
                    ),
                ),
                # Fixed: use customdata for actual count instead of marker.size
                hovertemplate="<b>%{text}</b><br>Offices: %{customdata:,}<extra></extra>",
            )
        )
        city_fig.update_layout(
            **apply_template(
                height=400,
                margin=dict(l=0, r=0, t=10, b=0),
            ),
            geo=dict(
                bgcolor="rgba(0,0,0,0)",
                landcolor="#f1f3f5",
                showframe=False,
                showcoastlines=True,
                coastlinecolor="#d0d5dc",
                projection_type="natural earth",
                showocean=True,
                oceancolor="#f8f9fb",
            ),
        )

        # ── Region Comparison (Grouped Bar) ──
        if len(cs) > 0:
            region_data = cs.groupby("world_region").agg(
                total_funding=("total_funding", "sum"),
                company_count=("company_count", "sum"),
                avg_funding=("avg_funding", "mean"),
            ).reset_index()
            region_data = region_data.sort_values("total_funding", ascending=False)
        else:
            region_data = pd.DataFrame(columns=["world_region", "total_funding", "company_count", "avg_funding"])

        region_fig = go.Figure()
        region_fig.add_trace(
            go.Bar(
                x=region_data["world_region"],
                y=region_data["total_funding"],
                name="Total Funding ($)",
                marker=dict(color=CHART_COLORS[0], cornerradius=4),
                yaxis="y",
                hovertemplate="<b>%{x}</b><br>Funding: $%{y:,.0f}<extra></extra>",
            )
        )
        region_fig.add_trace(
            go.Scatter(
                x=region_data["world_region"],
                y=region_data["company_count"],
                name="Companies",
                mode="lines+markers",
                line=dict(color=CHART_COLORS[4], width=2),
                marker=dict(size=8),
                yaxis="y2",
                hovertemplate="<b>%{x}</b><br>Companies: %{y:,.0f}<extra></extra>",
            )
        )
        region_fig.update_layout(
            **apply_template(
                height=350,
                yaxis=dict(title="Total Funding (USD)"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            ),
            yaxis2=dict(
                title="Company Count",
                overlaying="y",
                side="right",
                showgrid=False,
            ),
        )

        return [choropleth, ranking_fig, city_fig, region_fig]
