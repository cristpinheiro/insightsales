from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    sql_query: str
    results: List[Dict[str, Any]]
    execution_time: float
    retry_count: int
    success: bool
    error_message: Optional[str] = None


class ValidationError(BaseModel):
    is_valid: bool
    error_message: str
