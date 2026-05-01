import pandas as pd
from typing import Tuple


REQUIRED_COLUMNS = ["campaign", "impressions", "clicks", "cost", "conversions", "revenue"]
NUMERIC_COLUMNS  = ["impressions", "clicks", "cost", "conversions", "revenue"]


def validate_campaigns(df: pd.DataFrame) -> Tuple[bool, list]:
    """
    Validates a campaign DataFrame.
    Returns (is_valid, list_of_errors).
    """
    errors = []

    # 1) Required columns exist
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")
        return False, errors  # no point checking further

    # 2) Not empty
    if df.empty:
        errors.append("File is empty — no campaigns found.")
        return False, errors

    # 3) No missing values
    for col in REQUIRED_COLUMNS:
        nulls = df[col].isnull().sum()
        if nulls > 0:
            errors.append(f"'{col}' has {nulls} missing value(s).")

    # 4) Numeric columns are positive (avoid division by zero)
    for col in NUMERIC_COLUMNS:
        bad = (df[col] <= 0).sum()
        if bad > 0:
            errors.append(f"'{col}' has {bad} zero or negative value(s) — will cause division errors.")

    # 5) Campaign names are unique only if there is no date breakdown.
    if "date" in df.columns:
        parsed_dates = pd.to_datetime(df["date"], errors="coerce", infer_datetime_format=True)
        if parsed_dates.isna().any():
            errors.append(f"'date' has {int(parsed_dates.isna().sum())} invalid value(s).")
        else:
            duplicate_pairs = df[parsed_dates.notna()].duplicated(subset=["campaign", "date"], keep=False)
            dupes = df.loc[duplicate_pairs, ["campaign", "date"]].drop_duplicates()
            if not dupes.empty:
                issues = [f"{row['campaign']} @ {row['date']}" for row in dupes.to_dict("records")[:10]]
                suffix = ", ..." if len(dupes) > 10 else ""
                errors.append(f"Duplicate campaign+date rows: {', '.join(issues)}{suffix}")
    else:
        dupes = df[df.duplicated("campaign", keep=False)]["campaign"].unique()
        if len(dupes) > 0:
            errors.append(f"Duplicate campaign names: {list(dupes)}")

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_cross_platform_dates(
    google_df: pd.DataFrame,
    meta_df: pd.DataFrame,
    date_col: str = "date"
) -> Tuple[bool, list]:
    """
    Validates date coverage between the Google and Meta files.
    Returns (is_valid, issues). is_valid is False only for fatal issues
    such as missing or invalid date values. Date mismatches are returned
    as warnings in the issues list.
    """
    issues = []

    if google_df is None or meta_df is None:
        return True, []

    for platform_name, df in [("Google", google_df), ("Meta", meta_df)]:
        if date_col not in df.columns:
            issues.append(f"{platform_name} file missing required '{date_col}' column.")

    if issues:
        return False, issues

    google_dates = pd.to_datetime(google_df[date_col], errors="coerce", infer_datetime_format=True)
    meta_dates = pd.to_datetime(meta_df[date_col], errors="coerce", infer_datetime_format=True)

    if google_dates.isna().any():
        issues.append(f"Google file has {int(google_dates.isna().sum())} invalid {date_col} value(s).")
    if meta_dates.isna().any():
        issues.append(f"Meta file has {int(meta_dates.isna().sum())} invalid {date_col} value(s).")
    if issues:
        return False, issues

    google_unique = set(google_dates.dt.date.unique())
    meta_unique = set(meta_dates.dt.date.unique())

    google_only = sorted(google_unique - meta_unique)
    meta_only = sorted(meta_unique - google_unique)

    if google_only:
        text = ", ".join(str(d) for d in google_only[:10])
        if len(google_only) > 10:
            text += ", ..."
        issues.append(
            f"Dates present in Google but missing in Meta: {text}."
        )

    if meta_only:
        text = ", ".join(str(d) for d in meta_only[:10])
        if len(meta_only) > 10:
            text += ", ..."
        issues.append(
            f"Dates present in Meta but missing in Google: {text}."
        )

    return True, issues


def validate_and_raise(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates and raises ValueError if data is invalid.
    """
    is_valid, errors = validate_campaigns(df)

    if not is_valid:
        error_list = "\n".join(f"  - {e}" for e in errors)
        raise ValueError(f"Data validation failed:\n{error_list}")

    print(f"Data validation passed — {len(df)} campaigns ready.")
    return df