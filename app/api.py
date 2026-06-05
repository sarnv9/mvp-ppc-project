from fastapi import FastAPI, File, HTTPException, UploadFile
from src.analytics_engine import run_analysis
from app.database import admin_engine, PerformanceMetric, process_uploaded_file
from app.schemas import UploadResponse, MetricsResponse, QueryRequest, AgentResponse
from src.harmonize import harmonize_data
from sqlalchemy.orm import Session
from sqlalchemy import func, Integer, Float, String, Date
from src.prompt_templates import get_sql_agent
from typing import Optional
import pandas as pd


app = FastAPI(
    title="Ad-Agent AI API",
    description="Scalable backend for strategic campaign optimization (TFM)",
    version="1.0.0"
)


@app.get("/")
def read_root():
    """Health check endpoint. Returns API status."""
    return {
        "status": "ok",
        "message": "Ad-Agent AI backend is operational and ready."
    }


@app.post("/upload-all", response_model=UploadResponse)
async def upload_all_data(
    google_file: Optional[UploadFile] = File(None),
    meta_file: Optional[UploadFile] = File(None)
):
    """
    Ingests Google Ads and/or Meta Ads CSV files, harmonizes them into a
    unified schema, runs KPI analysis, and persists the results to PostgreSQL.

    At least one file must be provided. If only one platform is uploaded,
    existing data for that platform is replaced while the other is preserved.

    Args:
        google_file: Optional CSV export from Google Ads.
        meta_file: Optional CSV export from Meta Ads.

    Returns:
        UploadResponse with status, message, row count, and platform list.

    Raises:
        HTTPException 400: If no files are provided.
        HTTPException 500: If any processing or database error occurs.
    """
    try:
        google_df = None
        meta_df = None

        # Read uploaded files into DataFrames
        if google_file:
            google_content = await google_file.read()
            google_df = process_uploaded_file(google_content, google_file.filename)

        if meta_file:
            meta_content = await meta_file.read()
            meta_df = process_uploaded_file(meta_content, meta_file.filename)

        if google_df is None and meta_df is None:
            raise HTTPException(status_code=400, detail="Please upload at least one file.")

        # Harmonize both sources into a single unified DataFrame
        df_harmonized = harmonize_data(google_df=google_df, meta_df=meta_df)
        if df_harmonized.empty:
            raise ValueError("Data harmonization failed.")

        # Run KPI analysis (ROI, ROAS, CVR, CPL, CPC, CTR)
        df_final = run_analysis(df_harmonized)["df"]

        # --- Type coercion ---
        # Ensure numeric columns have correct dtypes before writing to SQL.
        # Pandas may infer object dtype when NULLs are present.
        int_cols = ['conversions', 'impressions', 'clicks']
        float_cols = ['cost', 'revenue', 'roi', 'roas', 'cpa', 'cvr', 'cpc', 'cpl', 'ctr']

        for col in int_cols + float_cols:
            if col in df_final.columns:
                if df_final[col].dtype == object:
                    # Strip thousands separators (e.g. "1,234" → "1234")
                    df_final[col] = df_final[col].astype(str).str.replace(',', '', regex=False)
                df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0)

        # Drop id if present — PostgreSQL will assign it via the model
        if 'id' in df_final.columns:
            df_final = df_final.drop(columns=['id'])

        # --- Align columns with SQLAlchemy model ---
        # Add any missing model columns as NULL/0 so the schema is always complete.
        model_columns = [c.name for c in PerformanceMetric.__table__.columns]

        for col in model_columns:
            if col == 'id':
                continue
            if col not in df_final.columns:
                df_final[col] = 0.0 if col in float_cols + int_cols else None

        # Assign sequential IDs and enforce column order
        df_final = df_final.reset_index(drop=True)
        df_final.insert(0, 'id', range(1, len(df_final) + 1))
        df_final = df_final[model_columns]

        # Create table if it does not exist (first run)
        PerformanceMetric.__table__.create(admin_engine, checkfirst=True)

        # Write to PostgreSQL with explicit dtype mapping to prevent
        # pandas from inferring TEXT for nullable numeric columns
        df_final.to_sql(
            name='performance_metrics',
            con=admin_engine,
            if_exists='replace',
            index=False,
            dtype={
                'id': Integer,
                'campaign_id': String,
                'campaign': String,
                'platform': String,
                'date': Date,
                'cost': Float,
                'revenue': Float,
                'roi': Float,
                'roas': Float,
                'conversions': Float,
                'clicks': Float,
                'impressions': Float
            }
        )

        return {
            "status": "success",
            "message": "Data successfully synchronized",
            "total_rows": len(df_final),
            "platforms": df_final['platform'].unique().tolist()
        }

    except Exception as e:
        print(f"Error in upload-all: {e}")
        raise HTTPException(status_code=500, detail=f"Process Error: {str(e)}")


@app.get("/analytics/kpis", response_model=MetricsResponse)
async def get_kpi_summary():
    """
    Returns aggregate KPI metrics and campaign rankings.

    Computes total spend, total revenue, average ROI, and the number of
    campaigns performing above the ROI average. Also returns the top 3
    and bottom 3 campaigns ranked by ROI.

    Returns:
        MetricsResponse containing KPI totals and ranked campaign lists.

    Raises:
        HTTPException 404: If no data exists in the database.
    """
    with Session(admin_engine) as session:

        # Aggregate totals across all campaigns
        metrics = session.query(
            func.sum(PerformanceMetric.cost).label("total_cost"),
            func.sum(PerformanceMetric.revenue).label("total_revenue"),
            func.avg(PerformanceMetric.roi).label("avg_roi"),
            func.count(PerformanceMetric.campaign).label("n_total")
        ).first()

        if not metrics or metrics.total_cost is None:
            raise HTTPException(status_code=404, detail="No data available")

        avg_roi = float(metrics.avg_roi)
        n_total = int(metrics.n_total)

        # Count campaigns that beat the average ROI
        n_above_roi = session.query(PerformanceMetric).filter(
            PerformanceMetric.roi >= avg_roi
        ).count()

        # Fetch top and bottom performers by ROI
        top_3_query = session.query(PerformanceMetric).order_by(
            PerformanceMetric.roi.desc()
        ).limit(3).all()

        bottom_3_query = session.query(PerformanceMetric).order_by(
            PerformanceMetric.roi.asc()
        ).limit(3).all()

        def to_clean_dict(row):
            """Strip SQLAlchemy internal state before serializing."""
            d = row.__dict__.copy()
            d.pop('_sa_instance_state', None)
            return d

        return {
            "total_cost": float(metrics.total_cost),
            "total_revenue": float(metrics.total_revenue),
            "avg_roi": avg_roi,
            "n_total": n_total,
            "n_above_roi": n_above_roi,
            "pct_above": (n_above_roi / n_total * 100) if n_total > 0 else 0,
            "rankings": {
                "top_3": [to_clean_dict(r) for r in top_3_query],
                "bottom_3": [to_clean_dict(r) for r in bottom_3_query]
            }
        }


@app.get("/analytics/charts/spend-vs-revenue")
async def get_chart_spend_revenue():
    """
    Returns the top 10 campaigns by revenue with their associated spend,
    used to render the Spend vs Revenue bar chart in the dashboard.
    """
    with Session(admin_engine) as session:
        results = session.query(
            PerformanceMetric.campaign,
            func.sum(PerformanceMetric.cost).label("cost"),
            func.sum(PerformanceMetric.revenue).label("revenue")
        ).group_by(PerformanceMetric.campaign) \
         .order_by(func.sum(PerformanceMetric.revenue).desc()) \
         .limit(10).all()

        return [
            {"campaign": r.campaign, "cost": float(r.cost), "revenue": float(r.revenue)}
            for r in results
        ]


@app.get("/analytics/charts/roi-by-campaign")
async def get_chart_roi_data():
    """
    Calculates ROI per campaign from raw cost and revenue totals.
    ROI is expressed as a percentage: (revenue - cost) / cost * 100.

    Returns campaigns sorted by ROI descending, used for the horizontal
    bar chart in the dashboard.
    """
    with Session(admin_engine) as session:
        results = session.query(
            PerformanceMetric.campaign,
            PerformanceMetric.platform,
            func.sum(PerformanceMetric.cost).label("total_cost"),
            func.sum(PerformanceMetric.revenue).label("total_revenue")
        ).group_by(PerformanceMetric.campaign, PerformanceMetric.platform).all()

        output = []
        for r in results:
            # Recalculate ROI from raw totals to avoid pre-aggregated column drift
            roi = ((r.total_revenue - r.total_cost) / r.total_cost * 100) if r.total_cost > 0 else 0
            output.append({
                "campaign": r.campaign,
                "platform": r.platform,
                "roi": roi
            })

        return sorted(output, key=lambda x: x['roi'], reverse=True)


@app.get("/analytics/charts/quadrants")
async def get_chart_quadrants():
    """
    Returns campaign data for the Budget vs ROI strategic quadrant scatter plot.

    Each point represents a campaign with its total spend, recalculated ROI,
    and conversion volume (used as bubble size). Campaigns are colored by platform.
    """
    with Session(admin_engine) as session:
        results = session.query(
            PerformanceMetric.campaign,
            PerformanceMetric.platform,
            func.sum(PerformanceMetric.cost).label("cost"),
            func.sum(PerformanceMetric.revenue).label("revenue"),
            func.sum(PerformanceMetric.conversions).label("conversions")
        ).group_by(PerformanceMetric.campaign, PerformanceMetric.platform).all()

        return [
            {
                "campaign": r.campaign,
                "platform": r.platform,
                "cost": float(r.cost),
                "roi": ((float(r.revenue) - float(r.cost)) / float(r.cost) * 100) if r.cost > 0 else 0,
                "conversions": int(r.conversions)
            }
            for r in results
        ]


@app.post("/agent/chat", response_model=AgentResponse)
async def chat_with_agent(request: QueryRequest):
    """
    Processes a natural language query through the SQL AI agent.

    The agent translates the user's question into SQL, queries the
    performance_metrics table, and returns a strategic analysis response.
    Intermediate reasoning steps (tool calls and observations) are captured
    and returned as a thought process log for transparency.

    Args:
        request: QueryRequest containing the user's natural language question.

    Returns:
        AgentResponse with the original query, final answer, and reasoning log.

    Raises:
        HTTPException 500: If the agent fails to process the query.
    """
    try:
        agent = get_sql_agent()
        result = agent.invoke({"input": request.query})
        intermediate_steps = result.get("intermediate_steps", [])

        # Build a human-readable log of the agent's reasoning process
        thought_log = ""
        if intermediate_steps:
            for action, observation in intermediate_steps:
                thought_log += f"Action: {action.tool}\n"
                thought_log += f"Action Input: {action.tool_input}\n"
                thought_log += f"Observation: {observation}\n\n"
        else:
            thought_log = "The agent provided a direct response without querying the database."

        return {
            "query": request.query,
            "response": result["output"],
            "thought_process": thought_log
        }

    except Exception as e:
        print(f"Agent error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent Error: {str(e)}")