import pandas as pd
import numpy as np


def run_analysis(df: pd.DataFrame) -> dict:
    """
    Aggregates raw campaign data and computes all KPIs.

    Groups the input DataFrame by campaign and platform, sums raw metrics,
    and derives performance indicators. Also returns pre-sorted ranking
    subsets used by the dashboard.

    Args:
        df: Harmonized DataFrame containing at minimum the columns:
            campaign, platform, cost, revenue, conversions, clicks, impressions.

    Returns:
        A dict with the following keys:
            'df'         -- Full aggregated DataFrame with all KPIs.
            'top_roi'    -- Top 3 campaigns by ROI.
            'bottom_roi' -- Bottom 3 campaigns by ROI.
            'top_cpl'    -- Top 3 campaigns by lowest CPL (most efficient).
            'top_cvr'    -- Top 3 campaigns by highest CVR.

    Raises:
        ValueError: If the input DataFrame is None or empty.
    """
    if df is None or df.empty:
        raise ValueError("Dataframe is empty or None")

    df = df.copy()

    # Aggregate raw metrics per campaign-platform combination
    df_grouped = df.groupby(["campaign", "platform"]).agg({
        "cost": "sum",
        "revenue": "sum",
        "conversions": "sum",
        "clicks": "sum",
        "impressions": "sum"
    }).reset_index()

    # Compute derived KPIs from aggregated totals
    df_grouped["roi"]  = calculate_roi(df_grouped["revenue"], df_grouped["cost"])
    df_grouped["roas"] = calculate_roas(df_grouped["revenue"], df_grouped["cost"])
    df_grouped["cvr"]  = calculate_cvr(df_grouped["conversions"], df_grouped["clicks"])
    df_grouped["cpl"]  = calculate_cpl(df_grouped["conversions"], df_grouped["cost"])
    df_grouped["cpc"]  = calculate_cpc(df_grouped["cost"], df_grouped["clicks"])
    df_grouped["ctr"]  = calculate_ctr(df_grouped["clicks"], df_grouped["impressions"])

    # Round all values to 2 decimal places for clean storage and display
    df_grouped = df_grouped.round(2)

    # Pre-compute ranking subsets for the dashboard
    top_roi    = df_grouped.sort_values("roi", ascending=False).head(3).copy()
    bottom_roi = df_grouped.sort_values("roi", ascending=True).head(3).copy()
    top_cpl    = df_grouped.sort_values("cpl").head(3).copy()
    top_cvr    = df_grouped.sort_values("cvr", ascending=False).head(3).copy()

    return {
        "df": df_grouped,
        "top_roi": top_roi,
        "bottom_roi": bottom_roi,
        "top_cpl": top_cpl,
        "top_cvr": top_cvr
    }


def calculate_roi(revenue: pd.Series, cost: pd.Series) -> pd.Series:
    """
    Calculates Return on Investment as a percentage.
    Formula: (revenue - cost) / cost * 100
    """
    return (revenue - cost) / cost * 100


def calculate_roas(revenue: pd.Series, cost: pd.Series) -> pd.Series:
    """
    Calculates Return on Ad Spend as a ratio.
    Formula: revenue / cost
    """
    return revenue / cost


def calculate_cvr(conversions: pd.Series, clicks: pd.Series) -> pd.Series:
    """
    Calculates Conversion Rate as a percentage.
    Formula: conversions / clicks * 100
    Zero-click campaigns are set to 0 to avoid division errors.
    """
    return (conversions / clicks.replace(0, np.nan) * 100).fillna(0)


def calculate_cpl(conversions: pd.Series, cost: pd.Series) -> pd.Series:
    """
    Calculates Cost per Lead (equivalent to CPA in this context).
    Formula: cost / conversions
    """
    return cost / conversions


def calculate_cpc(cost: pd.Series, clicks: pd.Series) -> pd.Series:
    """
    Calculates Cost per Click.
    Formula: cost / clicks
    """
    return cost / clicks


def calculate_ctr(clicks: pd.Series, impressions: pd.Series) -> pd.Series:
    """
    Calculates Click-Through Rate as a percentage.
    Formula: clicks / impressions * 100
    """
    return clicks / impressions * 100


def calculate_cpa(cost: pd.Series, conversions: pd.Series) -> pd.Series:
    """
    Calculates Cost per Acquisition.
    Formula: cost / conversions
    """
    return cost / conversions
