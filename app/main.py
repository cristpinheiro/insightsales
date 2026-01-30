from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
import logging  # noqa: E402

from app.schemas.schemas import QueryResponse, QueryRequest  # noqa: E402
from app.services.nl_to_sql_service import NLToSQLService  # noqa: E402
from app.config import DB_CONFIG, API_TITLE, API_VERSION, DEBUG  # noqa: E402


# Logging configuration
logging.basicConfig(level=logging.INFO if not DEBUG else logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize application
app = FastAPI(title=API_TITLE, version=API_VERSION, debug=DEBUG)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize service
nl_to_sql_service = NLToSQLService(DB_CONFIG)


@app.get("/health")
async def health_check():
    """Check if API is working"""
    db_connected = nl_to_sql_service.db_service.test_connection()
    return {
        "status": "healthy",
        "database_connected": db_connected,
        "debug_mode": DEBUG,
    }


@app.post("/query", response_model=QueryResponse)
async def process_natural_language_query(request: QueryRequest):
    """Process natural language question and return results"""
    try:
        logger.info(f"Processing query: {request.question}")

        sql_query, results, execution_time, retry_count, success, error_msg = (
            nl_to_sql_service.process_query_with_retry(request.question)
        )

        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to process query after {retry_count} attempts: {error_msg}",
            )

        return QueryResponse(
            sql_query=sql_query,
            results=results,
            execution_time=execution_time,
            retry_count=retry_count,
            success=success,
            error_message=error_msg if not success else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
