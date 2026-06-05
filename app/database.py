from sqlalchemy import create_engine, Column, String, Integer, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import pandas as pd
import io

# Load environment variables from .env file, overriding any existing shell values
load_dotenv(override=True)

# --- Database connection setup ---

# Admin connection: used for writes, table creation, and data uploads
ADMIN_URL = os.getenv("ADMIN_DATABASE_URL")
admin_engine = create_engine(ADMIN_URL)

# Read-only connection URL: passed to the LangChain SQL agent to prevent writes
READ_ONLY_URL = os.getenv("READ_ONLY_DATABASE_URL")

# Admin DB session for APIs.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=admin_engine)

# Base class for all database models.
Base = declarative_base()


class PerformanceMetric(Base):
    """
    Model for the performance_metrics table.

    Each row corresponds to one campaign aggregated by platform.
    Raw metrics (cost, revenue, clicks, etc.) are stored alongside
    pre-calculated KPIs (roi, roas, cvr, etc.) computed during ingestion.

    Columns:
        id          -- Primary key, auto-assigned on insert.
        platform    -- Ad platform: 'google' or 'meta'.
        campaign    -- Campaign name as exported from the ad platform.
        channel     -- Traffic channel (e.g. search, display). May be NULL.
        device      -- Device type (e.g. mobile, desktop). May be NULL.
        date        -- Reporting date. May be NULL if not present in source.
        cost        -- Total ad spend in EUR.
        revenue     -- Total attributed revenue in EUR.
        conversions -- Total conversion events.
        impressions -- Total ad impressions served.
        clicks      -- Total clicks recorded.
        roi         -- Return on Investment: (revenue - cost) / cost * 100.
        roas        -- Return on Ad Spend: revenue / cost.
        cpa         -- Cost per Acquisition: cost / conversions.
        cvr         -- Conversion Rate: conversions / clicks * 100.
        cpc         -- Cost per Click: cost / clicks.
        cpl         -- Cost per Lead (equivalent to CPA in this context).
        ctr         -- Click-Through Rate: clicks / impressions * 100.
    """
    __tablename__ = 'performance_metrics'

    id          = Column(Integer, primary_key=True)
    platform    = Column(String)
    campaign    = Column(String)
    channel     = Column(String)
    device      = Column(String)
    date        = Column(Date)
    cost        = Column(Float)
    revenue     = Column(Float)
    conversions = Column(Integer)
    impressions = Column(Integer)
    clicks      = Column(Integer)
    roi         = Column(Float)
    roas        = Column(Float)
    cpa         = Column(Float)
    cvr         = Column(Float)
    cpc         = Column(Float)
    cpl         = Column(Float)
    ctr         = Column(Float)


def init_db():
    """
    Creates missing database tables. Run once at application startup.
    """
    Base.metadata.create_all(bind=admin_engine)


def process_uploaded_file(file_content: bytes, filename: str) -> pd.DataFrame:
    """
    Parses uploaded file bytes into a raw pandas DataFrame.

    Supports CSV and Excel (.xls, .xlsx) formats. Does not transform the data;
    column renaming and standardization are handled downstream by harmonize_data().

    Args:
        file_content: Raw bytes of the uploaded file.
        filename: Filename used to detect the format (CSV or Excel).

    Returns:
        DataFrame containing the raw file contents.

    Raises:
        ValueError: If the file format is unsupported.
    """
    if filename.endswith('.csv'):
        return pd.read_csv(io.BytesIO(file_content))
    elif filename.endswith(('.xls', '.xlsx')):
        return pd.read_excel(io.BytesIO(file_content))
    else:
        raise ValueError("Unsupported file format. Please use CSV or Excel.")