from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class UploadResponse(BaseModel):
    """
    Response returned after a successful file upload and processing cycle.

    Attributes:
        status:     Outcome of the operation, e.g. 'success' or 'error'.
        message:    Human-readable description of the result.
        total_rows: Number of campaign rows persisted to the database.
        platforms:  List of ad platforms detected in the uploaded data,
                    e.g. ['google', 'meta'].
    """
    status: str
    message: str
    total_rows: int
    platforms: List[str]


class MetricsResponse(BaseModel):
    """
    Aggregate KPI summary returned by the /analytics/kpis endpoint.

    Attributes:
        total_cost:   Sum of ad spend across all campaigns in EUR.
        total_revenue: Sum of attributed revenue across all campaigns in EUR.
        avg_roi:      Average ROI across all campaigns, expressed as a percentage.
        n_total:      Total number of campaigns in the database.
        n_above_roi:  Number of campaigns with ROI at or above the average.
        pct_above:    Percentage of campaigns above average ROI.
        rankings:     Dict containing 'top_3' and 'bottom_3' campaign lists,
                      each as a list of raw campaign attribute dicts.
    """
    total_cost: float
    total_revenue: float
    avg_roi: float
    n_total: int
    n_above_roi: int
    pct_above: float
    rankings: Dict[str, List[Dict[str, Any]]]


class QueryRequest(BaseModel):
    """
    Request body for the /agent/chat endpoint.

    Attributes:
        query: Natural language question submitted by the user,
               e.g. 'Which campaign has the highest ROI?'.
    """
    query: str


class AgentResponse(BaseModel):
    """
    Response returned by the /agent/chat endpoint after the SQL agent
    processes a natural language query.

    Attributes:
        query:          The original question submitted by the user.
        response:       The agent's final answer in natural language.
        thought_process: Optional step-by-step log of the agent's reasoning,
                         including SQL queries executed and observations returned.
                         None if the agent answered directly without tool use.
    """
    query: str
    response: str
    thought_process: Optional[str] = None