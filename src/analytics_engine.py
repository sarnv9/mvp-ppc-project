import pandas as pd
from app.database import engine, init_db
import numpy as np

def run_analysis(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        raise ValueError("Dataframe is empty or None")

    df = df.copy()

    df["cvr"]  = calculate_cvr(df["conversions"], df["clicks"])
    df["cpl"]  = calculate_cpl(df["conversions"], df["cost"])
    df["roi"]  = calculate_roi(df["revenue"], df["cost"])
    df["cpc"]  = calculate_cpc(df["cost"], df["clicks"])
    df["roas"] = calculate_roas(df["revenue"], df["cost"])
    df["ctr"]  = calculate_ctr(df["clicks"], df["impressions"])
    df = df.round({"roi": 2, "cvr": 2, "cpl": 2, "cpc": 2, "roas": 2, "ctr": 2})

    top_roi = df.sort_values("roi", ascending=False).head(3).copy()
    bottom_roi = df.sort_values("roi", ascending=True).head(3).copy()
    top_cpl = df.sort_values("cpl").head(3).copy()
    top_cvr = df.sort_values("cvr", ascending=False).head(3).copy()

    numeric = df.select_dtypes(include="number")
    corr_matrix = numeric.corr()

    platform_stats = df.groupby("platform").agg({"cost": "sum", "conversions": "sum"})
    platform_stats["cpa"] = platform_stats["cost"] / platform_stats["conversions"].replace(0, np.nan)
    platform_stats["cpa"] = platform_stats["cpa"].fillna(0)

    if {"google", "meta"}.issubset(platform_stats.index):
        g_cpa = platform_stats.loc["google", "cpa"]
        m_cpa = platform_stats.loc["meta", "cpa"]

        if g_cpa < m_cpa:
            diff = ((m_cpa - g_cpa) / m_cpa) * 100 if m_cpa != 0 else 0
            advice_text = f"Google is more efficient. Shift budget to Google; its CPA is {round(diff, 1)}% lower than Meta."
        else:
            diff = ((g_cpa - m_cpa) / g_cpa) * 100 if g_cpa != 0 else 0
            advice_text = f"Meta is more efficient. Shift budget to Meta; its CPA is {round(diff, 1)}% lower than Google."
        advice_type = "success"
    else:
        advice_text = "Insufficient data for cross-platform comparison."
        advice_type = "warning"

    return {
        "df": df,
        "top_roi": top_roi,
        "bottom_roi": bottom_roi,
        "top_cpl": top_cpl,
        "top_cvr": top_cvr,
        "corr_matrix": corr_matrix,
        "platform_stats": platform_stats,
        "strategic_advice": advice_text,
        "advice_type": advice_type,
        "advice_text": advice_text,
    }


def calculate_cvr(conversions, clicks):
    return (conversions / clicks.replace(0, np.nan) * 100).fillna(0)

def calculate_cpl(conversions, cost):
    return cost / conversions

def calculate_roi(revenue, cost):
    return (revenue - cost) / cost * 100

def calculate_cpc(cost, clicks):
    return cost / clicks

def calculate_roas(revenue, cost):
    return revenue / cost

def calculate_ctr(clicks, impressions):
    return clicks / impressions * 100

def calculate_cpa(cost, conversions):
    return cost / conversions



def upload_to_sql(df: pd.DataFrame):
    """
    Toma el DataFrame resultante de run_analysis y lo persiste en PostgreSQL.
    """
    if df is None or df.empty:
        print("El DataFrame está vacío. No se subirá nada a la DB.")
        return False

    try:
        init_db()
        # This operation requires DROP/CREATE permissions
        df.to_sql('performance_metrics', con=admin_engine, if_exists='replace', index=False)
        return True
    except Exception as e:
        # If this fails with "permission denied", it means you are using the wrong user
        print(f"❌ Error: {e}")
        return False