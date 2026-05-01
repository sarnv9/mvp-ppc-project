import pandas as pd


def harmonize_data(google_df=None, meta_df=None):
    dfs = []

    google_columns = {

        'campaign': 'campaign',
        'cost': 'cost', 
        'clicks': 'clicks',
        'impressions': 'impressions',
        'conversions': 'conversions',
        'revenue': 'revenue',
    }

    meta_columns = {
        'campaign': 'campaign',
        'cost': 'cost',
        'clicks': 'clicks',     
       'impressions': 'impressions',
        'conversions': 'conversions',
        'revenue': 'revenue',   
       } 

    if google_df is not None:
        google_df = google_df.copy()
        google_df["platform"] = "google"
        google_df = google_df.rename(columns=google_columns)
        dfs.append(google_df)

    if meta_df is not None:
        meta_df = meta_df.copy()
        meta_df["platform"] = "meta"
        meta_df = meta_df.rename(columns=meta_columns)
        dfs.append(meta_df)

    if not dfs:
        return pd.DataFrame()

    result = pd.concat(dfs, ignore_index=True)
    if "date" in result.columns:
        result["date"] = pd.to_datetime(result["date"], errors="coerce")

    return result




    