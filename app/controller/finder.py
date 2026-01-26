"""
Query finder router.

Handles natural language to SQL query conversion endpoints.
This will be implemented later with Ollama integration.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Query"])


@router.get("/query")
async def process_query(question: str):
    """
    Process natural language question and convert to SQL.

    TODO: Implement Ollama integration
    """
    return {
        "question": question,
        "sql": "-- Not implemented yet",
        "results": [],
        "explanation": "This endpoint will be implemented with Ollama integration",
    }
