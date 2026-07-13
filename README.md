# VentureScope — Global Startup Visual Analytics

> *"See the Startup Universe. Clearly."*

A professional-grade visual analytics system for exploring the global startup ecosystem. Built for the **CS661 Visual Analytics** course project at IIT Kanpur.

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)
![Dash](https://img.shields.io/badge/Dash-2.18-blue?style=flat-square)
![Plotly](https://img.shields.io/badge/Plotly-5.24-blue?style=flat-square)
![Data](https://img.shields.io/badge/Records-379K+-green?style=flat-square)

---

## Overview

VentureScope transforms the Crunchbase startup investment dataset into an interactive visual analytics experience. Instead of static dashboards, it provides a **multi-page application** with 7 distinct analytical views, interactive filtering, drill-down capabilities, and data-driven storytelling.

### Key Features
- **Command Center** — KPI cards, funding velocity, sector allocation, and global heatmap
- **Funding Trends** — Time-series analysis with stage breakdown and YoY growth
- **Sector Intelligence** — Treemap, sector comparison, and growth trajectories
- **Startup Explorer** — Filterable table with 130K+ companies, search, and detail panels
- **Geo Analytics** — Interactive choropleth, city-level bubbles, and regional comparison
- **Investor Intelligence** — Investor × sector heatmap, rankings, and portfolio analysis
- **Insights & Stories** — Auto-generated narratives, success rates, Pareto analysis, and a dedicated **India Spotlight** deep-dive

### Interaction Model
Every chart shares one client-side interaction layer (`assets/interactions.js`): hovering an element highlights it and dims the rest, the sector donut pops the hovered slice out and updates its center label, legends are interactive (hover to highlight, click to toggle, double-click to isolate), clicks lock a selection, and transitions animate in the 300–400 ms range. A single global **Year Range** slider is the one source of truth — it filters every KPI, chart, map, table, and insight on every page and persists across navigation.

---

## Dataset

| Source | Description | Records |
|--------|-------------|---------|
| [Kaggle: StartUp Investments (Crunchbase)](https://www.kaggle.com/datasets/justinas/startup-investments) | Real startup investment data | 720K+ raw |

**After preprocessing:**

| Table | Records | Key Fields |
|-------|---------|------------|
| Companies | 130,150 | Name, sector, country, status, funding, founded year |
| Funding Rounds | 52,527 | Amount, stage, date, company details |
| Investments | 74,421 | Investor name, funded company, round details |
| Office Locations | 112,718 | City, country, latitude, longitude |
| **Total** | **379,378** | |

---

## Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd CS661

# Install dependencies
pip install -r requirements.txt

# Download dataset (requires Kaggle account)
python data/download_data.py

# Run preprocessing
python preprocessing/clean.py

# Launch the application
python app.py
```

The app will be available at **http://127.0.0.1:8050**

---

## Project Structure

```
CS661/
├── data/
│   ├── raw/                     # Original Crunchbase CSVs (11 files)
│   ├── processed/               # Cleaned & aggregated data
│   └── download_data.py         # Dataset acquisition script
├── preprocessing/
│   ├── __init__.py
│   └── clean.py                 # Data cleaning & feature engineering
├── analytics/
│   └── __init__.py
├── dashboard/
│   ├── components/              # Reusable UI components
│   ├── pages/
│   │   ├── overview.py          # Command Center
│   │   ├── funding.py           # Funding Trends
│   │   ├── sectors.py           # Sector Intelligence
│   │   ├── explorer.py          # Startup Explorer
│   │   ├── geo.py               # Geographic Analytics
│   │   ├── investors.py         # Investor Network
│   │   └── insights.py          # Story Mode
│   └── utils/
├── assets/
│   ├── style.css                # Custom light theme CSS
│   └── interactions.js          # Shared chart interaction layer (hover/dim/legend/donut popout)
├── notebooks/
│   └── eda_analysis.ipynb       # Exploratory Data Analysis
├── report/
│   ├── final_report.tex         # LaTeX final report (source)
│   └── figures/                 # Screenshots embedded in the report
├── proposal/
│   └── proposal.tex             # LaTeX proposal
├── qa/
│   ├── QA_REPORT.md             # Full audit & validation report
│   ├── qa_smoke_test.py         # Playwright test suite (31 checks)
│   └── qa_results.txt           # Latest test run
├── deliverables/
│   ├── report/                  # Compiled report PDF
│   ├── presentation/            # Demo slide deck (.pptx)
│   ├── screenshots_final/       # Fresh per-page screenshots
│   └── recordings_final/        # Walkthrough recordings (.mp4/.webm)
├── app.py                       # Main application entry
├── config.py                    # Configuration & design tokens
├── requirements.txt
└── README.md
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend + Visualization | Dash 2.18 + Plotly 5.24 |
| Layout / Styling | Dash Bootstrap Components + Custom CSS |
| Data Processing | Pandas 2.2 + NumPy 1.26 |
| Static Visualization | Matplotlib + Seaborn (report) |

---

## Visual Analytics Tasks

1. **Overview Analysis** — At-a-glance ecosystem health with KPI cards and sparklines
2. **Temporal Analysis** — Funding evolution over time with stage and sector breakdowns
3. **Sector Analysis** — Proportional allocation via treemap, comparative bar charts
4. **Entity Exploration** — Granular company-level search, filter, and sort
5. **Geographic Analysis** — Spatial distribution via choropleth and city-level bubbles
6. **Investor Analysis** — Investor behavior heatmap and portfolio composition
7. **Narrative Analysis** — Auto-generated insights, success/failure patterns, and an India-focused deep-dive

---

## Team

| Member | Roll Number | Responsibility |
|--------|-------------|----------------|
| Shamit Kamble | 228070999 | Data Processing |
| Moin Khan | 251090413 | Data Processing |
| Priyanshu Gupta | 220826 | Analytics Visualization Development |
| Harsh Bhati | 200408 | Analytics Visualization Development |
| Abhijeet Singh Thakur | 220029 | Application Development and Integration |
| Yashwanth Naik | 231046 | Application Development and Integration |
| Sai Dishanth | 220282 | User Interface Design and Styling |
| Lobsang Dhiki | 251110045 | User Interface Design and Styling |
| Lohit | 210564 | Testing and Deployment |

---

## License

This project uses the [Crunchbase StartUp Investments](https://www.kaggle.com/datasets/justinas/startup-investments) dataset from Kaggle (CC BY-NC-SA 4.0).

Built for CS661: Visual Analytics, IIT Kanpur, July 2026.
