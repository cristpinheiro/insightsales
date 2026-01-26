"""
SQL execution service.

Handles safe SQL query validation and execution with protection
against SQL injection and unauthorized operations.
"""

from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


class SQLService:
    """Service for safe SQL query validation and execution."""

    DANGEROUS_KEYWORDS = {
        "DROP",
        "DELETE",
        "UPDATE",
        "INSERT",
        "ALTER",
        "CREATE",
        "TRUNCATE",
        "GRANT",
        "REVOKE",
        "EXEC",
        "EXECUTE",
        "CALL",
    }

    def validate_sql(self, sql: str) -> tuple[bool, Optional[str]]:
        """Validate SQL query for safety. Returns (is_valid, error_message)."""
        if not sql or not sql.strip():
            return False, "Empty SQL query"

        sql_upper = sql.upper()

        if not sql_upper.strip().startswith("SELECT"):
            return False, "Only SELECT queries are allowed"

        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword in sql_upper:
                return False, f"Operation not allowed: {keyword}"

        statements = sql.split(";")
        if len(statements) > 2 or (len(statements) == 2 and statements[1].strip()):
            return False, "Multiple queries are not allowed"

        return True, None

    async def execute_query(
        self, db: AsyncSession, sql: str, max_rows: int = 1000
    ) -> dict[str, Any]:
        """Execute SQL query safely and return results."""
        is_valid, error_message = self.validate_sql(sql)
        if not is_valid:
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "error": error_message,
            }

        try:
            sql_with_limit = self._add_limit_if_missing(sql, max_rows)
            result = await db.execute(text(sql_with_limit))
            rows = result.fetchall()

            data = [dict(zip(result.keys(), row)) for row in rows] if rows else []

            return {
                "success": True,
                "data": data,
                "row_count": len(data),
                "error": None,
            }

        except Exception as e:
            error_msg = str(e)
            if "relation" in error_msg and "does not exist" in error_msg:
                error_msg = "Table not found. Check the table name."
            elif "column" in error_msg and "does not exist" in error_msg:
                error_msg = "Column not found. Check the column names."

            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "error": f"Query execution error: {error_msg}",
            }

    def _add_limit_if_missing(self, sql: str, max_rows: int) -> str:
        """Add LIMIT clause if not present in query."""
        if "LIMIT" in sql.upper():
            return sql
        
        return f"{sql.rstrip().rstrip(';')} LIMIT {max_rows}"

    def format_results_for_display(self, results: list[dict]) -> str:
        """Format query results for human-readable display."""
        if not results:
            return "No results found."

        columns = list(results[0].keys())
        output = [f"Total results: {len(results)}\n"]

        for i, row in enumerate(results[:10], 1):
            output.append(f"Result {i}:")
            for col in columns:
                output.append(f"  {col}: {row[col]}")
            output.append("")

        if len(results) > 10:
            output.append(f"... and {len(results) - 10} more results")

        return "\n".join(output)


# Global instance
sql_service = SQLService()
