"""
Query finder router.

Handles natural language to SQL query conversion endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.ollama_service import OllamaService
from app.services.sql_service import sql_service

router = APIRouter(prefix="/api", tags=["Query"])

ollama_service = OllamaService()


@router.get("/query")
async def process_query(question: str, db: AsyncSession = Depends(get_db)):
    """
    Process natural language question and convert to SQL.

    Steps:
    1. Generate SQL using Ollama (model has schema in Modelfile)
    2. Validate and execute SQL
    3. Return results
    """
    # Generate SQL from question (model already has schema context)
    sql_result = await ollama_service.generate_sql(question)

    if sql_result["error"]:
        return {
            "question": question,
            "sql": None,
            "results": [],
            "row_count": 0,
            "error": sql_result["explanation"],
        }

    sql = sql_result["sql"]

    # Execute SQL query
    exec_result = await sql_service.execute_query(db, sql)

    return {
        "question": question,
        "sql": sql,
        "results": exec_result["data"],
        "row_count": exec_result["row_count"],
        "error": exec_result.get("error"),
        "success": exec_result["success"],
    }
