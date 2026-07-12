"""
VentureScope — Configuration
Centralized settings for the entire application.
"""
import os

# ── Paths ──────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_RAW = os.path.join(BASE_DIR, "data", "raw")
DATA_PROCESSED = os.path.join(BASE_DIR, "data", "processed")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# ── Application ───────────────────────────────────────────────
APP_TITLE = "VentureScope"
APP_TAGLINE = "Global Startup Analytics"
APP_HOST = "127.0.0.1"
APP_PORT = 8050
# Keep False for demos/production: True shows the floating Dash dev-tools
# (callback graph / error) button in the bottom-right corner.
APP_DEBUG = False

# ── Design Tokens (Light Theme) ──────────────────────────────
COLORS = {
    "bg_primary":     "#f8f9fb",
    "bg_secondary":   "#ffffff",
    "bg_tertiary":    "#f1f3f5",
    "bg_card":        "#ffffff",
    "border":         "#e2e5ea",
    "border_light":   "#d0d5dc",
    "text_primary":   "#1a1d23",
    "text_secondary": "#5a6170",
    "text_muted":     "#8b919e",
    "accent_blue":    "#2563eb",
    "accent_purple":  "#7c3aed",
    "accent_cyan":    "#0891b2",
    "accent_green":   "#059669",
    "accent_red":     "#dc2626",
    "accent_amber":   "#d97706",
    "accent_pink":    "#db2777",
    "white":          "#ffffff",
}

# Plotly-compatible color sequence for charts
CHART_COLORS = [
    "#2563eb",  # Blue
    "#7c3aed",  # Purple
    "#0891b2",  # Cyan
    "#059669",  # Green
    "#d97706",  # Amber
    "#dc2626",  # Red
    "#db2777",  # Pink
    "#ea580c",  # Orange
    "#0d9488",  # Teal
    "#9333ea",  # Violet
    "#4f46e5",  # Indigo
    "#65a30d",  # Lime
]

# Gradient pairs for charts
GRADIENTS = {
    "blue_purple": ["#2563eb", "#7c3aed"],
    "cyan_blue":   ["#0891b2", "#2563eb"],
    "green_cyan":  ["#059669", "#0891b2"],
    "amber_red":   ["#d97706", "#dc2626"],
    "pink_purple": ["#db2777", "#7c3aed"],
}

# ── Chart Defaults ────────────────────────────────────────────
PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {
            "family": "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
            "color": COLORS["text_secondary"],
            "size": 12,
        },
        "title": {
            "font": {
                "family": "Inter, sans-serif",
                "color": COLORS["text_primary"],
                "size": 16,
            },
            "x": 0,
            "xanchor": "left",
        },
        "xaxis": {
            "gridcolor": "#ebedf0",
            "linecolor": COLORS["border"],
            "zerolinecolor": "#ebedf0",
            "showgrid": True,
            "gridwidth": 1,
        },
        "yaxis": {
            "gridcolor": "#ebedf0",
            "linecolor": COLORS["border"],
            "zerolinecolor": "#ebedf0",
            "showgrid": True,
            "gridwidth": 1,
        },
        "colorway": CHART_COLORS,
        "hoverlabel": {
            "bgcolor": "#ffffff",
            "bordercolor": COLORS["border"],
            "font": {
                "family": "Inter, sans-serif",
                "color": COLORS["text_primary"],
                "size": 13,
            },
        },
        "legend": {
            "bgcolor": "rgba(0,0,0,0)",
            "font": {"color": COLORS["text_secondary"]},
        },
        "margin": {"l": 50, "r": 20, "t": 50, "b": 40},
    }
}


def apply_template(**overrides):
    """Return a merged layout dict from PLOTLY_TEMPLATE with overrides.
    
    Handles deep merge for nested keys (margin, legend, xaxis, yaxis, etc.)
    to avoid duplicate keyword argument errors with update_layout().
    """
    import copy
    base = copy.deepcopy(PLOTLY_TEMPLATE["layout"])
    for k, v in overrides.items():
        if isinstance(v, dict) and k in base and isinstance(base[k], dict):
            base[k].update(v)
        else:
            base[k] = v
    return base

# ── Data Constants ────────────────────────────────────────────
SECTORS = [
    "SaaS / Software", "Internet / Web", "Advertising / Marketing",
    "E-Commerce", "Gaming / Media", "Biotech / Healthcare",
    "Mobile / Telecom", "Professional Services", "Hardware / Electronics",
    "Fintech", "CleanTech / Energy", "EdTech", "Cybersecurity",
    "News / Publishing", "Logistics / Transport", "Travel / Hospitality",
    "FoodTech", "PropTech / Real Estate", "Design / Creative",
    "Government / Non-profit", "Local Services", "Consumer Products",
    "Sports / Fitness", "Agriculture", "Aerospace / Defense",
]

FUNDING_STAGES = [
    "Angel", "Venture", "Series A", "Series B", "Series C+",
    "Private Equity", "Crowdfunding", "Post-IPO", "Other",
]

COUNTRIES = [
    "United States", "China", "India", "United Kingdom", "Germany",
    "France", "Canada", "Israel", "Singapore", "Brazil",
    "Japan", "South Korea", "Australia", "Sweden", "Netherlands",
    "Indonesia", "Nigeria", "UAE", "Switzerland", "Ireland",
    "Spain", "Italy", "Mexico", "Kenya", "South Africa",
    "Poland", "Estonia", "Finland", "Norway", "Denmark",
    "Belgium", "Austria", "Czech Republic", "New Zealand", "Colombia",
    "Chile", "Argentina", "Thailand", "Vietnam", "Philippines",
    "Egypt", "Turkey", "Saudi Arabia", "Malaysia", "Taiwan",
    "Portugal", "Romania", "Hungary", "Pakistan", "Bangladesh",
]

REGIONS = {
    "North America": ["United States", "Canada", "Mexico"],
    "Europe": ["United Kingdom", "Germany", "France", "Sweden", "Netherlands",
               "Switzerland", "Ireland", "Spain", "Italy", "Poland", "Estonia",
               "Finland", "Norway", "Denmark", "Belgium", "Austria",
               "Czech Republic", "Portugal", "Romania", "Hungary"],
    "Asia Pacific": ["China", "India", "Japan", "South Korea", "Australia",
                     "Singapore", "Indonesia", "Thailand", "Vietnam",
                     "Philippines", "Malaysia", "Taiwan", "New Zealand",
                     "Pakistan", "Bangladesh"],
    "Middle East & Africa": ["Israel", "UAE", "Nigeria", "Kenya",
                             "South Africa", "Egypt", "Turkey", "Saudi Arabia"],
    "Latin America": ["Brazil", "Colombia", "Chile", "Argentina"],
}

# Country → ISO Alpha-3 code mapping for choropleth
COUNTRY_ISO = {
    "United States": "USA", "China": "CHN", "India": "IND",
    "United Kingdom": "GBR", "Germany": "DEU", "France": "FRA",
    "Canada": "CAN", "Israel": "ISR", "Singapore": "SGP",
    "Brazil": "BRA", "Japan": "JPN", "South Korea": "KOR",
    "Australia": "AUS", "Sweden": "SWE", "Netherlands": "NLD",
    "Indonesia": "IDN", "Nigeria": "NGA", "UAE": "ARE",
    "Switzerland": "CHE", "Ireland": "IRL", "Spain": "ESP",
    "Italy": "ITA", "Mexico": "MEX", "Kenya": "KEN",
    "South Africa": "ZAF", "Poland": "POL", "Estonia": "EST",
    "Finland": "FIN", "Norway": "NOR", "Denmark": "DNK",
    "Belgium": "BEL", "Austria": "AUT", "Czech Republic": "CZE",
    "New Zealand": "NZL", "Colombia": "COL", "Chile": "CHL",
    "Argentina": "ARG", "Thailand": "THA", "Vietnam": "VNM",
    "Philippines": "PHL", "Egypt": "EGY", "Turkey": "TUR",
    "Saudi Arabia": "SAU", "Malaysia": "MYS", "Taiwan": "TWN",
    "Portugal": "PRT", "Romania": "ROU", "Hungary": "HUN",
    "Pakistan": "PAK", "Bangladesh": "BGD",
}

INVESTORS = [
    "Sequoia Capital", "Andreessen Horowitz", "Accel Partners",
    "Tiger Global", "SoftBank Vision Fund", "Y Combinator",
    "Lightspeed Venture", "Benchmark Capital", "Kleiner Perkins",
    "Founders Fund", "GGV Capital", "Index Ventures",
    "Insight Partners", "General Catalyst", "Bessemer Venture",
    "Khosla Ventures", "NEA", "Greylock Partners",
    "Battery Ventures", "Redpoint Ventures", "Union Square Ventures",
    "First Round Capital", "500 Startups", "Techstars",
    "Social Capital", "Coatue Management", "Ribbit Capital",
    "QED Investors", "Tencent Holdings", "Alibaba Group",
    "Goldman Sachs", "JPMorgan Chase", "Fidelity Investments",
    "DST Global", "Hillhouse Capital", "Temasek Holdings",
    "GIC Private Ltd", "Abu Dhabi Investment", "Mubadala Capital",
    "Naspers / Prosus",
]
