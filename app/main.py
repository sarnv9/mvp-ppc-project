import pandas as pd
from src.analytics_engine import run_analysis
from utils.save_recommendations import save_recommendations
from utils.save_results import save_results
 

def main():
    data = pd.read_csv("data/sample_data.csv")

    result = run_analysis(data)
    
    save_results(
        result["df"],
        result["top_roi"],
        result["top_cpl"],
        result["top_cvr"],
        result["corr_matrix"]
    )

    save_recommendations(result["df"])



if __name__ == "__main__":
    main()

