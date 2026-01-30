import logging
from typing import List, Dict, Any, Tuple
import time
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class DatabaseService:
    def __init__(self, db_config: dict):
        self.db_config = db_config

    def execute_query(self, query: str) -> Tuple[List[Dict[str, Any]], float]:
        """Execute query and return results with execution time"""
        start_time = time.time()
        results = []

        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]

            conn.commit()

        except Exception as e:
            logger.error(f"Database error: {e}")
            raise
        finally:
            if "conn" in locals():
                cursor.close()
                conn.close()

        execution_time = time.time() - start_time
        return results, execution_time

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            conn = psycopg2.connect(**self.db_config)
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
