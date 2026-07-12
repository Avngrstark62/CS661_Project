"""
VentureScope — Global Startup Visual Analytics
Main Application Entry Point

A professional visual analytics system for exploring the global startup ecosystem.
Built with Dash + Plotly using real Crunchbase data (130K+ companies, 52K+ funding rounds).

Source: https://www.kaggle.com/datasets/justinas/startup-investments

Usage:
    python app.py
    Open http://127.0.0.1:8050
"""
import os
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd

from config import APP_TITLE, APP_HOST, APP_PORT, APP_DEBUG, DATA_PROCESSED, COLORS

# ── Load processed data ───────────────────────────────────────
print("Loading processed data...")
df_companies = pd.read_csv(os.path.join(DATA_PROCESSED, "companies.csv"), low_memory=False)
df_funding = pd.read_csv(os.path.join(DATA_PROCESSED, "funding_rounds.csv"), low_memory=False)
df_investors = pd.read_csv(os.path.join(DATA_PROCESSED, "investors.csv"), low_memory=False)
df_offices = pd.read_csv(os.path.join(DATA_PROCESSED, "offices.csv"), low_memory=False)
df_sector_summary = pd.read_csv(os.path.join(DATA_PROCESSED, "sector_summary.csv"))
df_country_summary = pd.read_csv(os.path.join(DATA_PROCESSED, "country_summary.csv"))
df_timeline = pd.read_csv(os.path.join(DATA_PROCESSED, "funding_timeline.csv"))
df_investor_summary = pd.read_csv(os.path.join(DATA_PROCESSED, "investor_summary.csv"))
df_inv_sector = pd.read_csv(os.path.join(DATA_PROCESSED, "investor_sector_matrix.csv"))
df_stage_year = pd.read_csv(os.path.join(DATA_PROCESSED, "stage_year_trends.csv"))
df_sector_year = pd.read_csv(os.path.join(DATA_PROCESSED, "sector_year_trends.csv"))
df_country_year = pd.read_csv(os.path.join(DATA_PROCESSED, "country_year_trends.csv"))

print(f"  {len(df_companies):,} companies")
print(f"  {len(df_funding):,} funding rounds")
print(f"  {len(df_investors):,} investments")
print(f"  {len(df_offices):,} office locations")

# ── One-time enrichment (avoids repeated per-callback conversions) ──
# Investment year + numeric amounts for year-range filtering
df_investors["funded_at"] = pd.to_datetime(df_investors["funded_at"], errors="coerce")
df_investors["fund_year"] = df_investors["funded_at"].dt.year
df_investors["raised_amount_usd"] = pd.to_numeric(df_investors["raised_amount_usd"], errors="coerce")
# Sector of the funded company (for the year-aware investor × sector heatmap)
df_investors["sector"] = df_investors["funded_object_id"].map(
    df_companies.set_index("id")["sector"]
)

# ── Initialize Dash App ──────────────────────────────────────
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    title=f"{APP_TITLE} — Global Startup Analytics",
    update_title="Loading...",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
        {"name": "description", "content": "VentureScope: Interactive visual analytics for the global startup ecosystem. Explore 130K+ companies, 52K+ funding rounds, and 14K+ investors."},
    ],
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

server = app.server

# ── Import page layouts ───────────────────────────────────────
from dashboard.pages.overview import create_overview_layout, register_overview_callbacks
from dashboard.pages.funding import create_funding_layout, register_funding_callbacks
from dashboard.pages.sectors import create_sectors_layout, register_sectors_callbacks
from dashboard.pages.explorer import create_explorer_layout, register_explorer_callbacks
from dashboard.pages.geo import create_geo_layout, register_geo_callbacks
from dashboard.pages.investors import create_investors_layout, register_investors_callbacks
from dashboard.pages.insights import create_insights_layout, register_insights_callbacks

# Register all callbacks
register_overview_callbacks(app, df_companies, df_funding, df_sector_summary, df_timeline)
register_funding_callbacks(app, df_funding, df_stage_year, df_sector_year, df_timeline)
register_sectors_callbacks(app, df_companies, df_funding, df_sector_summary, df_sector_year)
register_explorer_callbacks(app, df_companies, df_funding)
register_geo_callbacks(app, df_companies, df_funding, df_country_summary, df_offices, df_country_year)
register_investors_callbacks(app, df_investors, df_investor_summary, df_inv_sector)
register_insights_callbacks(app, df_companies, df_funding, df_sector_summary, df_country_summary, df_investor_summary, df_investors)

# ── Navigation items ─────────────────────────────────────────
NAV_ITEMS = [
    {"id": "overview", "label": "Overview"},
    {"id": "funding", "label": "Funding Trends"},
    {"id": "sectors", "label": "Sectors"},
    {"id": "explorer", "label": "Explorer"},
    {"id": "geo", "label": "Geo Analytics"},
    {"id": "investors", "label": "Investors"},
    {"id": "insights", "label": "Insights"},
]


def create_sidebar():
    """Create the persistent left sidebar navigation."""
    nav_links = []
    for item in NAV_ITEMS:
        nav_links.append(
            html.Button(
                [
                    html.Span(item["label"], className="nav-label"),
                ],
                id=f"nav-{item['id']}",
                className="nav-item",
                n_clicks=0,
            )
        )

    return html.Div(
        [
            # Brand
            html.Div(
                [
                    html.Div("VS", className="sidebar-brand-icon"),
                    html.Div(
                        [
                            html.Div("VentureScope", className="sidebar-brand-text"),
                            html.Div("STARTUP ANALYTICS", className="sidebar-brand-tagline"),
                        ]
                    ),
                ],
                className="sidebar-brand",
            ),
            # Navigation
            html.Div(
                [
                    html.Div("NAVIGATION", className="sidebar-section-label"),
                    *nav_links,
                ],
                className="sidebar-nav",
            ),
            # Footer
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("Data: ", style={"color": COLORS["text_muted"], "fontSize": "10px"}),
                            html.Span("Crunchbase via Kaggle", style={"color": COLORS["text_secondary"], "fontSize": "10px"}),
                        ],
                        style={"padding": "16px", "borderTop": f"1px solid {COLORS['border']}"},
                    ),
                ],
            ),
        ],
        id="sidebar",
    )


def create_topbar():
    """Create the top bar with search and global year filter."""
    # Get year range from data
    years = df_funding["funding_year"].dropna().astype(int)
    min_year = max(int(years.min()), 1995)
    max_year = int(years.max())

    return html.Div(
        [
            # Search
            html.Div(
                [
                    dcc.Input(
                        id="global-search",
                        type="text",
                        placeholder="Search startups, sectors, investors...",
                        debounce=True,
                    ),
                ],
                className="topbar-search",
            ),
            # Year Range Filter
            html.Div(
                [
                    html.Span("Year Range", className="topbar-year-label"),
                    dcc.RangeSlider(
                        id="global-year-range",
                        min=min_year,
                        max=max_year,
                        step=1,
                        value=[min_year, max_year],
                        marks={y: str(y) for y in range(min_year, max_year + 1, 3)},
                        tooltip={"placement": "bottom", "always_visible": False},
                    ),
                ],
                style={"flex": "1", "maxWidth": "500px"},
            ),
        ],
        id="topbar",
    )


# ── App Layout ────────────────────────────────────────────────
app.layout = html.Div(
    [
        dcc.Store(id="current-page", data="overview"),
        dcc.Store(id="global-search-trigger", data=""),
        html.Div(
            [
                create_sidebar(),
                html.Div(
                    [
                        create_topbar(),
                        html.Div(id="page-content"),
                    ],
                    id="main-content",
                ),
            ],
            id="app-container",
        ),
    ]
)


# ── Global Search Callback ───────────────────────────────────
@app.callback(
    Output("global-search-trigger", "data"),
    Input("global-search", "value"),
    prevent_initial_call=True,
)
def handle_global_search(search_value):
    """Store the global search term for the Explorer page to consume."""
    return search_value or ""


# ── Sync global search to explorer search ────────────────────
@app.callback(
    Output("explorer-search", "value", allow_duplicate=True),
    Input("global-search-trigger", "data"),
    prevent_initial_call=True,
)
def sync_search_to_explorer(search_value):
    """Sync the global search value to the explorer search input."""
    return search_value or ""


# ── Navigation Callback ──────────────────────────────────────
@app.callback(
    [Output("page-content", "children"),
     Output("current-page", "data")]
    + [Output(f"nav-{item['id']}", "className") for item in NAV_ITEMS],
    [Input(f"nav-{item['id']}", "n_clicks") for item in NAV_ITEMS],
    [State("current-page", "data"),
     State("global-search-trigger", "data")],
    prevent_initial_call=False,
)
def navigate(*args):
    """Handle sidebar navigation clicks."""
    clicks = args[:len(NAV_ITEMS)]
    current_page = args[-2]
    search_value = args[-1]

    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]["prop_id"] != ".":
        # A button was clicked
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        page_id = triggered_id.replace("nav-", "")
    else:
        page_id = current_page or "overview"

    # Build page content
    page_map = {
        "overview": create_overview_layout,
        "funding": create_funding_layout,
        "sectors": create_sectors_layout,
        "explorer": create_explorer_layout,
        "geo": create_geo_layout,
        "investors": create_investors_layout,
        "insights": create_insights_layout,
    }

    layout_fn = page_map.get(page_id, create_overview_layout)
    # Explorer receives the persisted global search term so a search typed on
    # any page is still applied when the user opens the Explorer.
    if page_id == "explorer":
        content = layout_fn(search_value or "")
    else:
        content = layout_fn()

    # Update active nav item classes
    nav_classes = []
    for item in NAV_ITEMS:
        if item["id"] == page_id:
            nav_classes.append("nav-item active")
        else:
            nav_classes.append("nav-item")

    return [content, page_id] + nav_classes


# ── Run ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\nVentureScope running at http://{APP_HOST}:{APP_PORT}")
    print(f"   {len(df_companies):,} companies | {len(df_funding):,} rounds | {len(df_investors):,} investments\n")
    app.run(host=APP_HOST, port=APP_PORT, debug=APP_DEBUG)
