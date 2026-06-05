import pandas as pd


def harmonize_data(google_df=None, meta_df=None):

    """
    Merges Google Ads and Meta Ads DataFrames into a single unified schema.

    Each source DataFrame is independently normalized: column names are
    lowercased and stripped, a platform identifier is added, and columns
    are renamed to the unified schema. Both sources are then concatenated.

    At least one DataFrame must be provided. If only one is supplied,
    the result contains only that platform's data.

    Args:
        google_df: Raw DataFrame from a Google Ads CSV export. Optional.
        meta_df:   Raw DataFrame from a Meta Ads CSV export. Optional.

    Returns:
        A unified pandas DataFrame with normalized column names and a
        'platform' column identifying the data source ('google' or 'meta').
        The 'date' column is parsed to datetime if present.
        Returns an empty DataFrame if both inputs are None.
    """
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
        # Normalize column names to lowercase to match the mapping keys
        g.columns = [str(c).strip().lower() for c in g.columns]
        g["platform"] = "google"
        g = g.rename(columns=google_columns)
        dfs.append(g)

    if meta_df is not None:
        m = meta_df.copy()
        # Normalize column names to lowercase to match the mapping keys
        m.columns = [str(c).strip().lower() for c in m.columns]
        m["platform"] = "meta"
        m = m.rename(columns=meta_columns)
        dfs.append(m)

# Return empty DataFrame if no valid input was provided
    if not dfs:
        return pd.DataFrame()

    result = pd.concat(dfs, ignore_index=True)

# Parse date column to datetime; invalid entries become NaT
    if "date" in result.columns:
        result["date"] = pd.to_datetime(result["date"], errors="coerce")

    return result




    