import json
from datetime import datetime, timezone

def save_results(data, top_roi, top_cpl, top_cvr, corr_matrix):
    results = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "campaigns": data.to_dict(orient="records"),  # all metrics per campaign

    "rankings": {
        "top_roi":  top_roi[["campaign", "roi", "roas", "cvr"]].to_dict(orient="records"),
        "top_cpl":  top_cpl[["campaign", "cpl", "cpc", "roi"]].to_dict(orient="records"),
        "top_cvr":  top_cvr[["campaign", "cvr", "roi", "roas"]].to_dict(orient="records"),
        "bottom_roi": data.sort_values("roi").head(3)[["campaign", "roi", "cpc", "cvr"]].to_dict(orient="records"),
    },

    "correlations": corr_matrix["roi"].to_dict(), 
    
    "roi_summary": {                               
        "avg_roi": round(data["roi"].mean(), 2),
        "max_roi": round(data["roi"].max(), 2),
        "min_roi": round(data["roi"].min(), 2),
    }
}

    with open("data/results.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("Results saved to data/results.json")