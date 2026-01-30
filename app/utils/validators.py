import re
from typing import Tuple


class SQLValidator:
    @staticmethod
    def validate_sql_security(sql: str) -> Tuple[bool, str]:
        errors = ""

        if not sql:
            errors = errors + "Empty query.\n"

        sql_upper = sql.upper().strip()

        # Check dangerous operations
        dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER"]
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                errors = errors + "Dangerous operations detected: " + keyword + ".\n"

        if "SELECT" not in sql_upper:
            errors = errors + "Only SELECT queries are allowed.\n"

        if errors:
            return False, errors.strip()
        return True, "OK"

    @staticmethod
    def validate_sql_syntax(sql: str) -> Tuple[bool, str]:
        errors = ""
        """Basic syntax validations"""
        if not sql.strip().endswith(";"):
            sql = sql.strip() + ";"

        required_elements = ["FROM"]
        sql_upper = sql.upper()

        if not all(element in sql_upper for element in required_elements):
            errors = errors + "Query incomplete - missing required elements.\n"

        if errors:
            return False, errors.strip()

        return True, "OK"

    @staticmethod
    def sanitize_sql(sql: str) -> str:
        """Clean and format SQL query"""
        # Remove multiple spaces
        sql = re.sub(r"\s+", " ", sql).strip()
        # Remove everything before first SELECT
        select_match = re.search(r"\bSELECT\b", sql, re.IGNORECASE)
        if select_match:
            sql = sql[select_match.start() :]

        # Ensure semicolon at end
        if not sql.endswith(";"):
            sql += ";"

        return sql
