from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class UploadResponse(BaseModel):
    status: str
    message: str
    total_rows: int
    platforms: List[str]

class MetricsResponse(BaseModel):
    total_cost: float
    total_revenue: float
    avg_roi: float
    n_total: int
    n_above_roi: int
    pct_above: float
    rankings: Dict[str, List[Dict[str, Any]]]

class QueryRequest(BaseModel):
    query: str


class AgentResponse(BaseModel):
    query: str
    response: str
    thought_process: Optional[str] = None