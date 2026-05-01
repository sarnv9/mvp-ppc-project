from fastapi import FastAPI, File, HTTPException, UploadFile
import io
import pandas as pd
from src.analytics_engine import run_analysis
from app.schemas import FeedbackRequest

app = FastAPI()
LAST_RESULT = None  

@app.post("/submit_campaign/")
async def submit_campaign(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {e}")
    
    result = run_analysis(df)

# api.py
# from src.harmonize import harmonize_data

# @app.post("/submit_campaign/")
# def submit(google_file, meta_file):
#     df = harmonize_data(google_df, meta_df)
#     return run_analysis(df)

    global LAST_RESULT
    LAST_RESULT = {
    "total_campaigns": len(result["df"]),
    "roi_summary": {
        "avg_roi": round(result["df"]["roi"].mean(), 2),
        "max_roi": round(result["df"]["roi"].max(), 2),
        "min_roi": round(result["df"]["roi"].min(), 2),
    },
    "rankings": {
        "top_roi": result["top_roi"][["campaign", "roi", "roas"]].to_dict(orient="records"),
        "top_cvr": result["top_cvr"][["campaign", "cvr", "roi"]].to_dict(orient="records"),
        "top_cpl": result["top_cpl"][["campaign", "cpl", "roi"]].to_dict(orient="records"),
    }
}

    return {"message": "Campaign data processed successfully", "summary": LAST_RESULT["roi_summary"]}

@app.get("/view_metrics/")
def view_metrics():
    if LAST_RESULT is None:
        raise HTTPException(status_code=404, detail="No metrics available. Please upload a CSV file first.")
    return LAST_RESULT

FEEDBACK_LOG = []

@app.post("/feedback/")
def submit_feedback(feedback: FeedbackRequest):
    entry = {
        "campaign": feedback.campaign,
        "decision": feedback.decision,
        "comment": feedback.comment,
    }
    FEEDBACK_LOG.append(entry)
    return {
        "message": f"Feedback '{feedback.decision}' recorded for '{feedback.campaign}'",
        "total_feedback": len(FEEDBACK_LOG)
    }

@app.get("/feedback/")
def view_feedback():
    return {
        "total": len(FEEDBACK_LOG),
        "feedback": FEEDBACK_LOG
    }