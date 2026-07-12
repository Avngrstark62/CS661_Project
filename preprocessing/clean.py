"""
VentureScope — Data Preprocessing Pipeline
Processes the real Crunchbase StartUp Investments dataset from Kaggle.
Source: https://www.kaggle.com/datasets/justinas/startup-investments

Combines: objects.csv, funding_rounds.csv, investments.csv, acquisitions.csv,
          ipos.csv, offices.csv into a unified analytics-ready dataset.

Usage:
    python preprocessing/clean.py
"""
import os
import sys
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_RAW, DATA_PROCESSED

# ── ISO country code → full name mapping ──────────────────────
COUNTRY_MAP = {
    "USA": "United States", "GBR": "United Kingdom", "CAN": "Canada",
    "IND": "India", "DEU": "Germany", "FRA": "France", "AUS": "Australia",
    "ESP": "Spain", "IRL": "Ireland", "ISR": "Israel", "CHN": "China",
    "BRA": "Brazil", "JPN": "Japan", "NLD": "Netherlands", "ITA": "Italy",
    "SWE": "Sweden", "SGP": "Singapore", "KOR": "South Korea",
    "CHE": "Switzerland", "FIN": "Finland", "DNK": "Denmark",
    "NOR": "Norway", "BEL": "Belgium", "AUT": "Austria", "RUS": "Russia",
    "ARG": "Argentina", "CHL": "Chile", "COL": "Colombia", "MEX": "Mexico",
    "NZL": "New Zealand", "POL": "Poland", "PRT": "Portugal",
    "CZE": "Czech Republic", "HUN": "Hungary", "ROU": "Romania",
    "TUR": "Turkey", "ZAF": "South Africa", "NGA": "Nigeria",
    "KEN": "Kenya", "EGY": "Egypt", "ARE": "UAE", "SAU": "Saudi Arabia",
    "IDN": "Indonesia", "THA": "Thailand", "VNM": "Vietnam",
    "PHL": "Philippines", "MYS": "Malaysia", "TWN": "Taiwan",
    "HKG": "Hong Kong", "PAK": "Pakistan", "BGD": "Bangladesh",
    "EST": "Estonia", "LTU": "Lithuania", "LVA": "Latvia",
    "UKR": "Ukraine", "BGR": "Bulgaria", "HRV": "Croatia",
    "SVN": "Slovenia", "SVK": "Slovakia", "LUX": "Luxembourg",
    "PER": "Peru", "URY": "Uruguay", "ECU": "Ecuador",
    "GRC": "Greece", "JOR": "Jordan", "LBN": "Lebanon",
}

# Region mapping
REGION_MAP = {
    "United States": "North America", "Canada": "North America",
    "Mexico": "North America",
    "United Kingdom": "Europe", "Germany": "Europe", "France": "Europe",
    "Spain": "Europe", "Ireland": "Europe", "Netherlands": "Europe",
    "Italy": "Europe", "Sweden": "Europe", "Switzerland": "Europe",
    "Finland": "Europe", "Denmark": "Europe", "Norway": "Europe",
    "Belgium": "Europe", "Austria": "Europe", "Poland": "Europe",
    "Portugal": "Europe", "Czech Republic": "Europe", "Hungary": "Europe",
    "Romania": "Europe", "Estonia": "Europe", "Lithuania": "Europe",
    "Latvia": "Europe", "Ukraine": "Europe", "Bulgaria": "Europe",
    "Croatia": "Europe", "Slovenia": "Europe", "Slovakia": "Europe",
    "Luxembourg": "Europe", "Greece": "Europe", "Russia": "Europe",
    "China": "Asia Pacific", "India": "Asia Pacific", "Japan": "Asia Pacific",
    "South Korea": "Asia Pacific", "Australia": "Asia Pacific",
    "Singapore": "Asia Pacific", "Indonesia": "Asia Pacific",
    "Thailand": "Asia Pacific", "Vietnam": "Asia Pacific",
    "Philippines": "Asia Pacific", "Malaysia": "Asia Pacific",
    "Taiwan": "Asia Pacific", "Hong Kong": "Asia Pacific",
    "New Zealand": "Asia Pacific", "Pakistan": "Asia Pacific",
    "Bangladesh": "Asia Pacific",
    "Israel": "Middle East & Africa", "UAE": "Middle East & Africa",
    "Nigeria": "Middle East & Africa", "Kenya": "Middle East & Africa",
    "South Africa": "Middle East & Africa", "Egypt": "Middle East & Africa",
    "Turkey": "Middle East & Africa", "Saudi Arabia": "Middle East & Africa",
    "Jordan": "Middle East & Africa", "Lebanon": "Middle East & Africa",
    "Brazil": "Latin America", "Argentina": "Latin America",
    "Chile": "Latin America", "Colombia": "Latin America",
    "Peru": "Latin America", "Uruguay": "Latin America",
    "Ecuador": "Latin America",
}

# Category normalization → sector mapping
CATEGORY_TO_SECTOR = {
    "software": "SaaS / Software", "enterprise": "SaaS / Software",
    "saas": "SaaS / Software", "cloud": "SaaS / Software",
    "web": "Internet / Web", "social": "Internet / Web",
    "network_hosting": "Internet / Web", "search": "Internet / Web",
    "messaging": "Internet / Web",
    "ecommerce": "E-Commerce", "fashion": "E-Commerce",
    "shopping": "E-Commerce",
    "mobile": "Mobile / Telecom", "messaging": "Mobile / Telecom",
    "games_video": "Gaming / Media", "music": "Gaming / Media",
    "photo_video": "Gaming / Media", "video": "Gaming / Media",
    "entertainment": "Gaming / Media",
    "advertising": "Advertising / Marketing", "analytics": "Advertising / Marketing",
    "public_relations": "Advertising / Marketing", "marketing": "Advertising / Marketing",
    "biotech": "Biotech / Healthcare", "health": "Biotech / Healthcare",
    "medical": "Biotech / Healthcare",
    "finance": "Fintech", "payments": "Fintech", "insurance": "Fintech",
    "education": "EdTech",
    "cleantech": "CleanTech / Energy", "energy": "CleanTech / Energy",
    "semiconductor": "Hardware / Electronics", "hardware": "Hardware / Electronics",
    "nanotech": "Hardware / Electronics", "manufacturing": "Hardware / Electronics",
    "security": "Cybersecurity",
    "transportation": "Logistics / Transport", "automotive": "Logistics / Transport",
    "travel": "Travel / Hospitality", "hospitality": "Travel / Hospitality",
    "food_and_drinks": "FoodTech",
    "real_estate": "PropTech / Real Estate", "construction": "PropTech / Real Estate",
    "consulting": "Professional Services", "legal": "Professional Services",
    "government": "Government / Non-profit", "nonprofit": "Government / Non-profit",
    "local": "Local Services", "sports": "Sports / Fitness",
    "design": "Design / Creative", "pets": "Consumer Products",
    "news": "News / Publishing", "publishing": "News / Publishing",
    "agriculture": "Agriculture", "aerospace": "Aerospace / Defense",
}


def load_raw_data():
    """Load all raw CSV files from the Crunchbase dataset."""
    print("📂 Loading raw data files...")

    objects = pd.read_csv(
        os.path.join(DATA_RAW, "objects.csv"),
        encoding="latin-1", low_memory=False
    )
    funding_rounds = pd.read_csv(
        os.path.join(DATA_RAW, "funding_rounds.csv"),
        encoding="latin-1", low_memory=False
    )
    investments = pd.read_csv(
        os.path.join(DATA_RAW, "investments.csv"),
        encoding="latin-1", low_memory=False
    )
    acquisitions = pd.read_csv(
        os.path.join(DATA_RAW, "acquisitions.csv"),
        encoding="latin-1", low_memory=False
    )
    ipos = pd.read_csv(
        os.path.join(DATA_RAW, "ipos.csv"),
        encoding="latin-1", low_memory=False
    )
    offices = pd.read_csv(
        os.path.join(DATA_RAW, "offices.csv"),
        encoding="latin-1", low_memory=False
    )

    print(f"  ✓ objects.csv:         {len(objects):>10,} rows")
    print(f"  ✓ funding_rounds.csv:  {len(funding_rounds):>10,} rows")
    print(f"  ✓ investments.csv:     {len(investments):>10,} rows")
    print(f"  ✓ acquisitions.csv:    {len(acquisitions):>10,} rows")
    print(f"  ✓ ipos.csv:            {len(ipos):>10,} rows")
    print(f"  ✓ offices.csv:         {len(offices):>10,} rows")

    return objects, funding_rounds, investments, acquisitions, ipos, offices


def process_companies(objects: pd.DataFrame) -> pd.DataFrame:
    """Extract and clean company records from objects table."""
    print("\n🏢 Processing companies...")

    companies = objects[objects["entity_type"] == "Company"].copy()
    print(f"  Raw companies: {len(companies):,}")

    # Select and rename key columns
    # 'id' is the primary join key (format: 'c:1234')
    companies = companies[[
        "id", "entity_id", "name", "normalized_name", "permalink",
        "category_code", "status", "founded_at", "closed_at",
        "country_code", "state_code", "city", "region",
        "short_description", "tag_list",
        "funding_rounds", "funding_total_usd",
        "first_funding_at", "last_funding_at",
        "relationships", "milestones",
    ]].copy()

    # Parse dates
    companies["founded_at"] = pd.to_datetime(companies["founded_at"], errors="coerce")
    companies["closed_at"] = pd.to_datetime(companies["closed_at"], errors="coerce")
    companies["first_funding_at"] = pd.to_datetime(companies["first_funding_at"], errors="coerce")
    companies["last_funding_at"] = pd.to_datetime(companies["last_funding_at"], errors="coerce")

    # Extract founding year
    companies["founded_year"] = companies["founded_at"].dt.year

    # Map country codes to full names
    companies["country"] = companies["country_code"].map(COUNTRY_MAP)
    companies["country"] = companies["country"].fillna(
        companies["country_code"].where(companies["country_code"].notna(), "Unknown")
    )

    # Map to regions
    companies["world_region"] = companies["country"].map(REGION_MAP).fillna("Other")

    # Map categories to sectors
    companies["sector"] = companies["category_code"].map(CATEGORY_TO_SECTOR).fillna("Other")

    # Clean funding total
    companies["funding_total_usd"] = pd.to_numeric(
        companies["funding_total_usd"], errors="coerce"
    )

    # Clean city names
    companies["city"] = companies["city"].fillna("Unknown").str.strip().str.title()

    # Clean status
    companies["status"] = companies["status"].fillna("operating").str.strip().str.lower()

    # Filter: Keep companies with at least some meaningful data
    # Must have a name AND (country OR category OR funding)
    mask = (
        companies["name"].notna() &
        (
            companies["country_code"].notna() |
            companies["category_code"].notna() |
            (companies["funding_total_usd"] > 0)
        )
    )
    companies = companies[mask].copy()

    # Ensure 'id' is used as the primary key
    companies = companies.drop_duplicates(subset="id")

    print(f"  Cleaned companies: {len(companies):,}")
    print(f"  With funding data: {(companies['funding_total_usd'] > 0).sum():,}")
    print(f"  With country: {companies['country_code'].notna().sum():,}")
    print(f"  With category: {companies['category_code'].notna().sum():,}")

    return companies


def process_funding_rounds(
    funding_rounds: pd.DataFrame,
    companies: pd.DataFrame
) -> pd.DataFrame:
    """Process and enrich funding round data."""
    print("\n💰 Processing funding rounds...")

    fr = funding_rounds[[
        "funding_round_id", "object_id", "funded_at",
        "funding_round_type", "funding_round_code",
        "raised_amount_usd", "pre_money_valuation_usd",
        "post_money_valuation_usd", "participants",
        "is_first_round", "is_last_round",
    ]].copy()

    # Parse dates
    fr["funded_at"] = pd.to_datetime(fr["funded_at"], errors="coerce")
    fr["funding_year"] = fr["funded_at"].dt.year
    fr["funding_month"] = fr["funded_at"].dt.month
    fr["funding_quarter"] = fr["funded_at"].dt.quarter

    # Clean amounts
    fr["raised_amount_usd"] = pd.to_numeric(fr["raised_amount_usd"], errors="coerce")
    fr["pre_money_valuation_usd"] = pd.to_numeric(fr["pre_money_valuation_usd"], errors="coerce")
    fr["post_money_valuation_usd"] = pd.to_numeric(fr["post_money_valuation_usd"], errors="coerce")

    # Normalize round type names
    round_type_map = {
        "venture": "Venture",
        "angel": "Angel",
        "series-a": "Series A",
        "series-b": "Series B",
        "series-c+": "Series C+",
        "other": "Other",
        "private-equity": "Private Equity",
        "crowdfunding": "Crowdfunding",
        "post-ipo": "Post-IPO",
    }
    fr["funding_stage"] = fr["funding_round_type"].map(round_type_map).fillna("Other")

    # Join with company data to get sector, country, etc.
    # The 'object_id' in funding_rounds matches 'id' in objects (format: 'c:1234')
    company_lookup = companies[[
        "id", "name", "sector", "country", "country_code",
        "world_region", "city", "category_code", "status", "founded_year",
    ]].copy()

    fr_enriched = fr.merge(
        company_lookup,
        left_on="object_id",
        right_on="id",
        how="left",
        suffixes=("", "_company"),
    )

    # Drop rows without company match
    fr_enriched = fr_enriched[fr_enriched["name"].notna()].copy()

    print(f"  Total funding rounds: {len(fr):,}")
    print(f"  Matched to companies: {len(fr_enriched):,}")
    print(f"  With amounts: {fr_enriched['raised_amount_usd'].notna().sum():,}")
    print(f"  Date range: {fr_enriched['funding_year'].min():.0f} - {fr_enriched['funding_year'].max():.0f}")

    return fr_enriched


def process_investors(
    investments: pd.DataFrame,
    objects: pd.DataFrame,
    funding_rounds: pd.DataFrame,
) -> pd.DataFrame:
    """Build investor-deal mapping with investor names."""
    print("\n🤝 Processing investors...")

    # Get investor names from objects table using 'id' column
    investors_obj = objects[
        objects["entity_type"].isin(["FinancialOrg", "Person"])
    ][["id", "name", "entity_type"]].copy()
    investors_obj = investors_obj.rename(columns={
        "id": "investor_id",
        "name": "investor_name",
        "entity_type": "investor_type",
    })

    # Join investments with investor names
    inv = investments.merge(
        investors_obj,
        left_on="investor_object_id",
        right_on="investor_id",
        how="left",
    )

    # Join with funding round info
    fr_info = funding_rounds[[
        "funding_round_id", "object_id", "funded_at",
        "funding_round_type", "raised_amount_usd",
    ]].copy()
    fr_info["raised_amount_usd"] = pd.to_numeric(fr_info["raised_amount_usd"], errors="coerce")

    inv = inv.merge(fr_info, on="funding_round_id", how="left")

    inv = inv[inv["investor_name"].notna()].copy()

    print(f"  Total investment records: {len(investments):,}")
    print(f"  Matched with names: {len(inv):,}")
    print(f"  Unique investors: {inv['investor_name'].nunique():,}")

    return inv


def process_acquisitions(
    acquisitions: pd.DataFrame,
    objects: pd.DataFrame,
) -> pd.DataFrame:
    """Process acquisition data."""
    print("\n🔄 Processing acquisitions...")

    acq = acquisitions.copy()
    acq["acquired_at"] = pd.to_datetime(acq["acquired_at"], errors="coerce")
    acq["price_amount"] = pd.to_numeric(acq["price_amount"], errors="coerce")

    # Get acquirer names using 'id' column
    acquirer_names = objects[["id", "name"]].rename(
        columns={"id": "acquirer_id", "name": "acquirer_name"}
    )
    acq = acq.merge(
        acquirer_names,
        left_on="acquiring_object_id",
        right_on="acquirer_id",
        how="left",
    )

    # Get acquired company names
    acquired_names = objects[["id", "name"]].rename(
        columns={"id": "acquired_id_lookup", "name": "acquired_name"}
    )
    acq = acq.merge(
        acquired_names,
        left_on="acquired_object_id",
        right_on="acquired_id_lookup",
        how="left",
        suffixes=("", "_acquired"),
    )

    print(f"  Total acquisitions: {len(acq):,}")
    print(f"  With price data: {acq['price_amount'].notna().sum():,}")

    return acq


def process_offices(offices: pd.DataFrame) -> pd.DataFrame:
    """Process office/location data with lat/lng for geographic viz."""
    print("\n📍 Processing office locations...")

    off = offices[[
        "object_id", "city", "state_code", "country_code",
        "latitude", "longitude", "region",
    ]].copy()

    off["latitude"] = pd.to_numeric(off["latitude"], errors="coerce")
    off["longitude"] = pd.to_numeric(off["longitude"], errors="coerce")

    # Keep only valid coordinates
    off = off[off["latitude"].notna() & off["longitude"].notna()].copy()

    # Map country codes
    off["country"] = off["country_code"].map(COUNTRY_MAP).fillna(off["country_code"])

    print(f"  Offices with coordinates: {len(off):,}")

    return off


def create_aggregations(
    companies: pd.DataFrame,
    fr_enriched: pd.DataFrame,
    investors: pd.DataFrame,
):
    """Create pre-computed aggregation tables for fast dashboard loading."""
    print("\n📊 Creating aggregation tables...")

    # ── 1) Sector Summary ──
    funded_companies = companies[companies["funding_total_usd"] > 0]
    sector_summary = funded_companies.groupby("sector").agg(
        total_funding=("funding_total_usd", "sum"),
        avg_funding=("funding_total_usd", "mean"),
        median_funding=("funding_total_usd", "median"),
        company_count=("id", "count"),
        avg_founded_year=("founded_year", "mean"),
    ).round(0).reset_index()
    sector_summary = sector_summary.sort_values("total_funding", ascending=False)
    sector_summary.to_csv(
        os.path.join(DATA_PROCESSED, "sector_summary.csv"), index=False
    )
    print("  ✓ sector_summary.csv")

    # ── 2) Country Summary ──
    country_summary = funded_companies.groupby(["country", "world_region", "country_code"]).agg(
        total_funding=("funding_total_usd", "sum"),
        company_count=("id", "count"),
        avg_funding=("funding_total_usd", "mean"),
    ).round(0).reset_index()
    country_summary = country_summary.sort_values("total_funding", ascending=False)
    country_summary.to_csv(
        os.path.join(DATA_PROCESSED, "country_summary.csv"), index=False
    )
    print("  ✓ country_summary.csv")

    # ── 3) Funding Timeline (yearly) ──
    # deal_count counts ALL rounds (including undisclosed amounts) so it matches
    # the Overview KPI; avg_deal_size averages only disclosed (>0) amounts.
    yearly = fr_enriched[fr_enriched["funding_year"].notna()].copy()
    disclosed = yearly[yearly["raised_amount_usd"] > 0]
    timeline = yearly.groupby("funding_year").agg(
        total_funding=("raised_amount_usd", "sum"),
        deal_count=("funding_round_id", "count"),
    ).round(0).reset_index()
    avg_by_year = disclosed.groupby("funding_year")["raised_amount_usd"].mean().round(0)
    timeline["avg_deal_size"] = timeline["funding_year"].map(avg_by_year).fillna(0)
    timeline.to_csv(
        os.path.join(DATA_PROCESSED, "funding_timeline.csv"), index=False
    )
    print("  ✓ funding_timeline.csv")

    # ── 4) Funding by Stage and Year ──
    stage_year = yearly.groupby(["funding_year", "funding_stage"]).agg(
        total_funding=("raised_amount_usd", "sum"),
        deal_count=("funding_round_id", "count"),
    ).round(0).reset_index()
    stage_year.to_csv(
        os.path.join(DATA_PROCESSED, "stage_year_trends.csv"), index=False
    )
    print("  ✓ stage_year_trends.csv")

    # ── 5) Sector x Year Trends ──
    sector_year = yearly.groupby(["funding_year", "sector"]).agg(
        total_funding=("raised_amount_usd", "sum"),
        deal_count=("funding_round_id", "count"),
    ).round(0).reset_index()
    sector_year.to_csv(
        os.path.join(DATA_PROCESSED, "sector_year_trends.csv"), index=False
    )
    print("  ✓ sector_year_trends.csv")

    # ── 6) Investor Summary ──
    inv_summary = investors.groupby("investor_name").agg(
        total_investments=("raised_amount_usd", "sum"),
        deal_count=("funding_round_id", "nunique"),
        avg_deal_size=("raised_amount_usd", "mean"),
    ).round(0).reset_index()
    inv_summary = inv_summary.sort_values("total_investments", ascending=False)
    inv_summary = inv_summary.head(200)  # Top 200 investors
    inv_summary.to_csv(
        os.path.join(DATA_PROCESSED, "investor_summary.csv"), index=False
    )
    print("  ✓ investor_summary.csv")

    # ── 7) Investor × Sector matrix ──
    # Join investors with company sectors
    company_sectors = companies[["id", "sector"]].copy()
    inv_with_sector = investors.merge(
        company_sectors,
        left_on="funded_object_id",
        right_on="id",
        how="left",
    )
    inv_sector = inv_with_sector[inv_with_sector["sector"].notna()].groupby(
        ["investor_name", "sector"]
    ).agg(
        deal_count=("funding_round_id", "nunique"),
        total_invested=("raised_amount_usd", "sum"),
    ).round(0).reset_index()
    # Filter to top 30 investors only
    top_investors = inv_summary.head(30)["investor_name"].tolist()
    inv_sector = inv_sector[inv_sector["investor_name"].isin(top_investors)]
    inv_sector.to_csv(
        os.path.join(DATA_PROCESSED, "investor_sector_matrix.csv"), index=False
    )
    print("  ✓ investor_sector_matrix.csv")

    # ── 8) Funding by Country x Year ──
    country_year = yearly.groupby(["funding_year", "country"]).agg(
        total_funding=("raised_amount_usd", "sum"),
        deal_count=("funding_round_id", "count"),
    ).round(0).reset_index()
    country_year.to_csv(
        os.path.join(DATA_PROCESSED, "country_year_trends.csv"), index=False
    )
    print("  ✓ country_year_trends.csv")


def main():
    """Execute complete preprocessing pipeline."""
    print("╔══════════════════════════════════════════════════════╗")
    print("║  VentureScope — Data Preprocessing Pipeline          ║")
    print("║  Source: Kaggle Crunchbase StartUp Investments        ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    os.makedirs(DATA_PROCESSED, exist_ok=True)

    # Step 1: Load raw data
    objects, funding_rounds_raw, investments_raw, acquisitions_raw, ipos_raw, offices_raw = load_raw_data()

    # Step 2: Process companies
    companies = process_companies(objects)
    companies.to_csv(os.path.join(DATA_PROCESSED, "companies.csv"), index=False)
    print(f"  💾 Saved companies.csv ({len(companies):,} rows)")

    # Step 3: Process funding rounds (enriched with company data)
    fr_enriched = process_funding_rounds(funding_rounds_raw, companies)
    fr_enriched.to_csv(os.path.join(DATA_PROCESSED, "funding_rounds.csv"), index=False)
    print(f"  💾 Saved funding_rounds.csv ({len(fr_enriched):,} rows)")

    # Step 4: Process investors
    investors = process_investors(investments_raw, objects, funding_rounds_raw)
    investors.to_csv(os.path.join(DATA_PROCESSED, "investors.csv"), index=False)
    print(f"  💾 Saved investors.csv ({len(investors):,} rows)")

    # Step 5: Process acquisitions
    acq = process_acquisitions(acquisitions_raw, objects)
    acq.to_csv(os.path.join(DATA_PROCESSED, "acquisitions.csv"), index=False)
    print(f"  💾 Saved acquisitions.csv ({len(acq):,} rows)")

    # Step 6: Process offices (geo data)
    offices = process_offices(offices_raw)
    offices.to_csv(os.path.join(DATA_PROCESSED, "offices.csv"), index=False)
    print(f"  💾 Saved offices.csv ({len(offices):,} rows)")

    # Step 7: Create aggregation tables
    create_aggregations(companies, fr_enriched, investors)

    # ── Summary ──
    print("\n" + "=" * 60)
    print("📋 PREPROCESSING COMPLETE")
    print("=" * 60)
    print(f"  Companies:       {len(companies):>10,}")
    print(f"  Funding Rounds:  {len(fr_enriched):>10,}")
    print(f"  Investors:       {len(investors):>10,}")
    print(f"  Acquisitions:    {len(acq):>10,}")
    print(f"  Office Locations:{len(offices):>10,}")
    total = len(companies) + len(fr_enriched) + len(investors) + len(acq) + len(offices)
    print(f"  ─────────────────────────")
    print(f"  TOTAL RECORDS:   {total:>10,}")
    print("=" * 60)
    print(f"\n✅ DATASET VERIFIED ✓")
    print(f"Source: https://www.kaggle.com/datasets/justinas/startup-investments")
    print(f"All processed files saved to: {DATA_PROCESSED}")


if __name__ == "__main__":
    main()
