from datetime import datetime, timezone
import json
import pandas as pd

def save_recommendations(data):
    recommendations = []

    for _, row in data.iterrows():
        actions = []

        if row["roi"] < 0:
            actions.append({
                "issue": "Negative ROI",
                "action": "Pause this campaign immediately",
                "priority": "high"
            })
        if row["cpc"] > data["cpc"].mean() * 1.3:
            actions.append({
                "issue": "CPC 30% above average",
                "action": "Reduce max bid or refine targeting",
                "priority": "medium"
            })
        if row["cvr"] < data["cvr"].mean() * 0.7:
            actions.append({
                "issue": "CVR 30% below average",
                "action": "Review landing page or audience match",
                "priority": "medium"
            })
        if row["roas"] > data["roas"].mean() * 1.2:
            actions.append({
                "issue": "High ROAS",
                "action": "Increase budget to scale",
                "priority": "high"
            })

        if actions:
            recommendations.append({
                "campaign": row["campaign"],
                "roi": round(row["roi"], 2),
                "actions": actions
            })

    with open("data/recommendations.json", "w") as f:
        json.dump({"generated_at": datetime.now(timezone.utc).isoformat(),
                   "recommendations": recommendations}, f, indent=2)

    print("Recommendations saved to data/recommendations.json")