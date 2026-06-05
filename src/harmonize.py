import pandas as pd


def harmonize_data(google_df=None, meta_df=None):
    dfs = []

    google_columns = {
        'campaign_id': 'campaign_id',
        'campaign': 'campaign',
        'channel': 'channel',
        'device': 'device',
        'impressions': 'impressions',
        'clicks': 'clicks',
        'conversions': 'conversions',
        'cost': 'cost',
        'revenue': 'revenue',
        'date': 'date'
    }

    meta_columns = {
    'campaign id': 'campaign_id', 
    'campaign name': 'campaign',
    'channel': 'channel',
    'device': 'device',
    'impressions': 'impressions',
    'link clicks': 'clicks',
    'results': 'conversions',
    'amount spent (eur)': 'cost',
    'revenue': 'revenue',
    'reporting starts': 'date'
}

    if google_df is not None:
        g = google_df.copy()
        g.columns = [str(c).strip().lower() for c in g.columns]
        g["platform"] = "google"
        g = g.rename(columns=google_columns)
        dfs.append(g)

    if meta_df is not None:
        m = meta_df.copy()
        m.columns = [str(c).strip().lower() for c in m.columns]
        m["platform"] = "meta"
        m = m.rename(columns=meta_columns)
        dfs.append(m)

    if not dfs:
        return pd.DataFrame()

    result = pd.concat(dfs, ignore_index=True)

    if "date" in result.columns:
        result["date"] = pd.to_datetime(result["date"], errors="coerce")

    return result




    