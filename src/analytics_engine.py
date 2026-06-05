import pandas as pd
from app.database import admin_engine
import numpy as np

def run_analysis(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        raise ValueError("Dataframe is empty or None")

    df = df.copy()

    df_grouped = df.groupby(["campaign", "platform"]).agg({
        "cost": "sum",
        "revenue": "sum",
        "conversions": "sum",
        "clicks": "sum",
        "impressions": "sum"
    }).reset_index()


    df_grouped["roi"]   = calculate_roi(df_grouped["revenue"], df_grouped["cost"])
    df_grouped["roas"]  = calculate_roas(df_grouped["revenue"], df_grouped["cost"])
    df_grouped["cvr"]   = calculate_cvr(df_grouped["conversions"], df_grouped["clicks"])
    df_grouped["cpl"]   = calculate_cpl(df_grouped["conversions"], df_grouped["cost"]) 
    df_grouped["cpc"]   = calculate_cpc(df_grouped["cost"], df_grouped["clicks"])
    df_grouped["ctr"]   = calculate_ctr(df_grouped["clicks"], df_grouped["impressions"])


    df_grouped = df_grouped.round(2)


    top_roi = df_grouped.sort_values("roi", ascending=False).head(3).copy()
    bottom_roi = df_grouped.sort_values("roi", ascending=True).head(3).copy()
    top_cpl = df_grouped.sort_values("cpl").head(3).copy()
    top_cvr = df_grouped.sort_values("cvr", ascending=False).head(3).copy()

    return {
        "df": df_grouped, 
        "top_roi": top_roi,
        "bottom_roi": bottom_roi,
        "top_cpl": top_cpl,
        "top_cvr": top_cvr
    }


def calculate_cvr(conversions, clicks):
    return (conversions / clicks.replace(0, np.nan) * 100).fillna(0)

def calculate_cpl(conversions, cost):
    return cost / conversions

def calculate_roi(revenue, cost):
    return (revenue - cost) / cost 

def calculate_cpc(cost, clicks):
    return cost / clicks

def calculate_roas(revenue, cost):
    return revenue / cost

def calculate_ctr(clicks, impressions):
    return clicks / impressions * 100

def calculate_cpa(cost, conversions):
    return cost / conversions




def upload_to_sql(df: pd.DataFrame):
    if df is None or df.empty:
        return False

    try:

        df.to_sql('performance_metrics', con=admin_engine, if_exists='replace', index=False)
        print("✅ Data successfully uploaded using Administrator privileges.")
        return True
    except Exception as e:
        print(f"❌ Critical Error during upload: {e}")
        return False