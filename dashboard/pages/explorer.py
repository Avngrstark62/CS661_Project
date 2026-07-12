"""
VentureScope — Startup Explorer Page
Filterable data table with sidebar filters and detail panels.
"""
from dash import html, dcc, Input, Output, State, dash_table, callback_context
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from config import COLORS, CHART_COLORS, PLOTLY_TEMPLATE


def create_explorer_layout(search_value=""):
    return html.Div(
        [
            html.Div(
                [
                    html.H1("Startup Explorer", className="page-title"),
                    html.P("Search, filter, and analyze individual startups", className="page-subtitle"),
                ],
                className="page-header",
            ),
            # Explorer layout: Filters + Table
            html.Div(
                [
                    # Left: Filter Panel
                    html.Div(
                        [
                            html.Div("FILTERS", style={
                                "fontSize": "11px", "fontWeight": "600",
                                "color": COLORS["text_muted"], "letterSpacing": "1px",
                                "marginBottom": "16px", "textTransform": "uppercase",
                            }),
                            # Search
                            html.Div(
                                [
                                    html.Label("Search", className="filter-label"),
                                    dcc.Input(
                                        id="explorer-search",
                                        type="text",
                                        placeholder="Company name...",
                                        value=search_value or "",
                                        debounce=True,
                                        style={
                                            "width": "100%", "height": "36px",
                                            "background": COLORS["bg_tertiary"],
                                            "border": f"1px solid {COLORS['border']}",
                                            "borderRadius": "8px", "padding": "0 12px",
                                            "color": COLORS["text_primary"],
                                            "fontSize": "13px",
                                        },
                                    ),
                                ],
                                style={"marginBottom": "16px"},
                            ),
                            # Country Filter
                            html.Div(
                                [
                                    html.Label("Country", className="filter-label"),
                                    dcc.Dropdown(
                                        id="explorer-country",
                                        multi=True,
                                        placeholder="All countries",
                                    ),
                                ],
                                style={"marginBottom": "16px"},
                            ),
                            # Sector Filter
                            html.Div(
                                [
                                    html.Label("Sector", className="filter-label"),
                                    dcc.Dropdown(
                                        id="explorer-sector",
                                        multi=True,
                                        placeholder="All sectors",
                                    ),
                                ],
                                style={"marginBottom": "16px"},
                            ),
                            # Status Filter
                            html.Div(
                                [
                                    html.Label("Status", className="filter-label"),
                                    dcc.Dropdown(
                                        id="explorer-status",
                                        options=[
                                            {"label": "Operating", "value": "operating"},
                                            {"label": "Acquired", "value": "acquired"},
                                            {"label": "IPO", "value": "ipo"},
                                            {"label": "Closed", "value": "closed"},
                                        ],
                                        multi=True,
                                        placeholder="All statuses",
                                    ),
                                ],
                                style={"marginBottom": "16px"},
                            ),
                            # Funding Range
                            html.Div(
                                [
                                    html.Label("Min Funding ($)", className="filter-label"),
                                    dcc.Dropdown(
                                        id="explorer-min-funding",
                                        options=[
                                            {"label": "Any", "value": 0},
                                            {"label": "> $100K", "value": 100000},
                                            {"label": "> $1M", "value": 1000000},
                                            {"label": "> $10M", "value": 10000000},
                                            {"label": "> $100M", "value": 100000000},
                                        ],
                                        value=0,
                                        clearable=False,
                                    ),
                                ],
                                style={"marginBottom": "16px"},
                            ),
                            # Reset
                            html.Button(
                                "Reset Filters",
                                id="explorer-reset",
                                className="btn",
                                style={"width": "100%"},
                                n_clicks=0,
                            ),
                        ],
                        className="explorer-filters",
                    ),
                    # Right: Results
                    html.Div(
                        [
                            html.Div(id="explorer-results-count", className="explorer-results-count"),
                            html.Div(id="explorer-table-container"),
                        ],
                        className="explorer-results",
                    ),
                ],
                className="explorer-layout",
            ),
        ],
        style={"padding": "32px", "maxWidth": "1400px", "margin": "0 auto"},
    )


def register_explorer_callbacks(app, df_companies, df_funding):

    # Populate filter options
    @app.callback(
        [
            Output("explorer-country", "options"),
            Output("explorer-sector", "options"),
        ],
        Input("current-page", "data"),
    )
    def populate_filters(page):
        # Get countries sorted by company count (most relevant first)
        country_counts = df_companies["country"].value_counts()
        # Filter out raw ISO codes (3-letter uppercase that weren't mapped to names)
        # and "Unknown" entries
        valid_countries = [
            c for c in country_counts.index
            if c != "Unknown" and not (len(c) <= 3 and c == c.upper() and c.isalpha())
        ]
        country_opts = [{"label": c, "value": c} for c in valid_countries]

        sectors = sorted(df_companies["sector"].dropna().unique())
        sector_opts = [{"label": s, "value": s} for s in sectors if s != "Other"]

        return [country_opts, sector_opts]

    # Reset button callback
    @app.callback(
        [
            Output("explorer-search", "value"),
            Output("explorer-country", "value"),
            Output("explorer-sector", "value"),
            Output("explorer-status", "value"),
            Output("explorer-min-funding", "value"),
        ],
        Input("explorer-reset", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_filters(n_clicks):
        """Clear all filter inputs when Reset is clicked."""
        return ["", None, None, None, 0]

    @app.callback(
        [
            Output("explorer-results-count", "children"),
            Output("explorer-table-container", "children"),
        ],
        [
            Input("current-page", "data"),
            Input("explorer-search", "value"),
            Input("explorer-country", "value"),
            Input("explorer-sector", "value"),
            Input("explorer-status", "value"),
            Input("explorer-min-funding", "value"),
            Input("global-year-range", "value"),
        ],
    )
    def update_explorer(page, search, countries, sectors, statuses, min_funding, year_range):
        if page != "explorer":
            return ["", html.Div()]

        # Use boolean masks instead of copying the entire DataFrame
        mask = pd.Series(True, index=df_companies.index)

        # Apply filters
        if search:
            mask = mask & df_companies["name"].str.contains(search, case=False, na=False)
        if countries:
            mask = mask & df_companies["country"].isin(countries)
        if sectors:
            mask = mask & df_companies["sector"].isin(sectors)
        if statuses:
            mask = mask & df_companies["status"].isin(statuses)
        if min_funding and min_funding > 0:
            mask = mask & (df_companies["funding_total_usd"] >= min_funding)

        yr_min, yr_max = year_range or [1995, 2013]
        if "founded_year" in df_companies.columns:
            year_mask = df_companies["founded_year"].isna() | (
                (df_companies["founded_year"] >= yr_min) &
                (df_companies["founded_year"] <= yr_max)
            )
            mask = mask & year_mask

        filtered = df_companies[mask]
        total = len(filtered)

        # Prepare display data — best-funded companies first so the table opens
        # with meaningful rows instead of unfunded / unknown-location entries.
        display_cols = [
            "name", "sector", "country", "city", "status",
            "funding_total_usd", "funding_rounds", "founded_year",
        ]
        display_df = (
            filtered.sort_values("funding_total_usd", ascending=False, na_position="last")
            .head(500)[display_cols]
            .copy()
        )

        display_df["funding_total_usd"] = display_df["funding_total_usd"].fillna(0)
        display_df["funding_rounds"] = display_df["funding_rounds"].fillna(0).astype(int)
        # Clean display values: em-dash instead of "Unknown"/missing
        display_df["founded_year"] = display_df["founded_year"].apply(
            lambda y: f"{int(y)}" if pd.notna(y) and y > 0 else "—"
        )
        for col in ["country", "city", "sector"]:
            display_df[col] = display_df[col].fillna("—").replace("Unknown", "—")
        display_df["status"] = display_df["status"].fillna("operating").str.upper()

        display_df.columns = [
            "Company", "Sector", "Country", "City", "Status",
            "Total Funding ($)", "Rounds", "Founded",
        ]

        count_text = [
            html.Span("Showing "),
            html.Strong(f"{min(500, total):,}"),
            html.Span(" of "),
            html.Strong(f"{total:,}"),
            html.Span(" companies — sorted by total funding. \"—\" = not reported in the dataset."),
        ]

        table = dash_table.DataTable(
            data=display_df.to_dict("records"),
            columns=[
                {"name": c, "id": c,
                 "type": "numeric" if c in ["Total Funding ($)", "Rounds"] else "text",
                 "format": {"specifier": "$,.0f"} if c == "Total Funding ($)" else None}
                for c in display_df.columns
            ],
            sort_action="native",
            sort_mode="multi",
            page_size=20,
            page_action="native",
            style_table={"overflowX": "auto", "minWidth": "100%"},
            style_header={
                "backgroundColor": COLORS["bg_tertiary"],
                "color": COLORS["text_secondary"],
                "fontWeight": "600",
                "fontSize": "11px",
                "textTransform": "uppercase",
                "letterSpacing": "0.5px",
                "border": f"1px solid {COLORS['border']}",
                "padding": "12px 12px",
                "whiteSpace": "nowrap",
            },
            style_cell={
                "backgroundColor": COLORS["bg_card"],
                "color": COLORS["text_primary"],
                "border": f"1px solid {COLORS['border']}",
                "fontSize": "13px",
                "padding": "10px 12px",
                "textAlign": "left",
                "fontFamily": "Inter, sans-serif",
                "overflow": "hidden",
                "textOverflow": "ellipsis",
                "whiteSpace": "nowrap",
            },
            style_cell_conditional=[
                {"if": {"column_id": "Company"},
                 "minWidth": "150px", "width": "175px", "maxWidth": "200px", "fontWeight": "500"},
                {"if": {"column_id": "Sector"},
                 "minWidth": "135px", "width": "150px", "maxWidth": "165px"},
                {"if": {"column_id": "Country"},
                 "minWidth": "105px", "width": "115px", "maxWidth": "130px"},
                {"if": {"column_id": "City"},
                 "minWidth": "100px", "width": "110px", "maxWidth": "125px"},
                {"if": {"column_id": "Status"},
                 "minWidth": "100px", "width": "105px", "maxWidth": "115px",
                 "fontSize": "10.5px", "fontWeight": "600", "letterSpacing": "0.4px"},
                {"if": {"column_id": "Total Funding ($)"},
                 "minWidth": "120px", "width": "130px", "maxWidth": "145px",
                 "textAlign": "right", "fontFamily": "JetBrains Mono, monospace", "fontSize": "12.5px"},
                {"if": {"column_id": "Rounds"},
                 "minWidth": "65px", "width": "70px", "maxWidth": "80px", "textAlign": "center"},
                {"if": {"column_id": "Founded"},
                 "minWidth": "75px", "width": "80px", "maxWidth": "90px", "textAlign": "center"},
            ],
            style_data_conditional=[
                {
                    "if": {"filter_query": '{Status} = "OPERATING"', "column_id": "Status"},
                    "color": COLORS["accent_green"],
                },
                {
                    "if": {"filter_query": '{Status} = "ACQUIRED"', "column_id": "Status"},
                    "color": COLORS["accent_blue"],
                },
                {
                    "if": {"filter_query": '{Status} = "IPO"', "column_id": "Status"},
                    "color": COLORS["accent_purple"],
                },
                {
                    "if": {"filter_query": '{Status} = "CLOSED"', "column_id": "Status"},
                    "color": COLORS["accent_red"],
                },
                {
                    "if": {"filter_query": "{Total Funding ($)} = 0", "column_id": "Total Funding ($)"},
                    "color": COLORS["text_muted"],
                },
                {
                    "if": {"state": "active"},
                    "backgroundColor": COLORS["bg_tertiary"],
                },
            ],
            style_as_list_view=True,
        )

        return [count_text, table]
