import pandas as pd

from utils.validation import validate_campaigns, validate_cross_platform_dates


def make_row(campaign, date):
    return {
        "campaign": campaign,
        "impressions": 1000,
        "clicks": 100,
        "cost": 500.0,
        "conversions": 10,
        "revenue": 1200.0,
        "date": date,
    }


def test_cross_platform_dates_match():
    google_df = pd.DataFrame([
        make_row("google-campaign", "2025-06-01"),
        make_row("google-campaign-2", "2025-06-02"),
    ])
    meta_df = pd.DataFrame([
        make_row("meta-campaign", "2025-06-01"),
        make_row("meta-campaign-2", "2025-06-02"),
    ])

    valid, issues = validate_cross_platform_dates(google_df, meta_df)

    assert valid is True
    assert issues == []


def test_cross_platform_dates_missing_date_column():
    google_df = pd.DataFrame([
        make_row("google-campaign", "2025-06-01"),
    ])
    meta_df = pd.DataFrame([
        {
            "campaign": "meta-campaign",
            "impressions": 1000,
            "clicks": 100,
            "cost": 500.0,
            "conversions": 10,
            "revenue": 1200.0,
        }
    ])

    valid, issues = validate_cross_platform_dates(google_df, meta_df)

    assert valid is False
    assert "missing required 'date' column" in issues[0].lower()


def test_cross_platform_dates_mismatch():
    google_df = pd.DataFrame([
        make_row("google-campaign", "2025-06-01"),
        make_row("google-campaign-2", "2025-06-03"),
    ])
    meta_df = pd.DataFrame([
        make_row("meta-campaign", "2025-06-01"),
        make_row("meta-campaign-2", "2025-06-02"),
    ])

    valid, issues = validate_cross_platform_dates(google_df, meta_df)

    assert valid is True
    assert any("missing in Meta" in issue for issue in issues)
    assert any("missing in Google" in issue for issue in issues)


def test_validate_campaigns_allows_date_level_campaign_duplicates():
    google_df = pd.DataFrame([
        make_row("Search-Competitor", "2025-06-01"),
        make_row("Search-Competitor", "2025-06-02"),
    ])

    valid, errors = validate_campaigns(google_df)

    assert valid is True
    assert errors == []


def test_validate_campaigns_flags_duplicate_campaign_date_rows():
    google_df = pd.DataFrame([
        make_row("Search-Competitor", "2025-06-01"),
        make_row("Search-Competitor", "2025-06-01"),
    ])

    valid, errors = validate_campaigns(google_df)

    assert valid is False
    assert any("Duplicate campaign+date rows" in error for error in errors)
