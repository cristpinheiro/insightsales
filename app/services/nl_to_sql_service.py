import ollama
import logging
from typing import Iterator, Mapping, Tuple, List, Dict, Any, Union

from app.utils.validators import SQLValidator
from app.services.database_service import DatabaseService
from app.config import MODEL_NAME, MAX_RETRIES

logger = logging.getLogger(__name__)


class NLToSQLService:
    def __init__(self, db_config: dict):
        self.client = ollama.Client()
        self.model_name = MODEL_NAME
        self.max_retries = MAX_RETRIES
        self.db_service = DatabaseService(db_config)
        self.validator = SQLValidator()

    def _extract_response_content(
        self, response: Union[Mapping[str, Any], Iterator[Mapping[str, Any]]]
    ) -> str:
        if isinstance(response, Iterator):
            full_response = ""
            for chunk in response:
                if isinstance(chunk, dict) and "message" in chunk:
                    full_response += chunk["message"].get("content", "")
            return full_response.strip()
        else:
            return response["message"]["content"].strip()

    def generate_sql(self, question: str) -> str:
        """Generate SQL query using LLM - fresh session every time"""
        messages: List[ollama.Message] = [{"role": "user", "content": question}]

        response = self.client.chat(
            model=self.model_name,
            messages=messages,
            stream=False,
            options={"temperature": 0.1, "num_predict": 400},
        )

        return self._extract_response_content(response)

    def fix_sql_with_context(self, question: str, bad_sql: str, error: str) -> str:
        """Fix SQL with context from the same request"""
        messages: List[ollama.Message] = [
            {"role": "user", "content": question},
            {"role": "assistant", "content": bad_sql},
            {
                "role": "user",
                "content": f"The above SQL is incorrect. Error: {error}. Please fix it.",
            },
        ]

        response = self.client.chat(
            model=self.model_name,
            messages=messages,
            stream=False,
            options={"temperature": 0.2, "num_predict": 400},
        )

        return self._extract_response_content(response)

    def process_query_with_retry(
        self, question: str
    ) -> Tuple[str, List[Dict[str, Any]], float, int, bool, str]:
        """Process query with automatic retries"""
        retry_count = 0
        last_error = ""
        sql_query = ""

        while retry_count < self.max_retries:
            try:
                # Generate SQL (fresh session every time)
                sql_query = self.generate_sql(question)

                # Validate SQL
                is_secure, security_error = self.validator.validate_sql_security(
                    sql_query
                )
                if not is_secure:
                    raise ValueError(f"Security validation failed: {security_error}")

                is_valid, syntax_error = self.validator.validate_sql_syntax(sql_query)
                if not is_valid:
                    raise ValueError(f"Syntax validation failed: {syntax_error}")

                # Sanitize SQL
                sql_query = self.validator.sanitize_sql(sql_query)

                # Execute query
                results, execution_time = self.db_service.execute_query(sql_query)

                return sql_query, results, execution_time, retry_count, True, ""

            except Exception as e:
                retry_count += 1
                last_error = str(e)
                logger.warning(f"Attempt {retry_count} failed: {e}")

                if retry_count < self.max_retries:
                    try:
                        # Try to fix with context (same request session)
                        sql_query = self.fix_sql_with_context(
                            question, sql_query, last_error
                        )
                        logger.info(f"LLM suggested fix for attempt {retry_count + 1}")
                    except Exception as fix_error:
                        logger.error(f"LLM fix failed: {fix_error}")
                        continue
                else:
                    break

        return sql_query, [], 0.0, retry_count, False, last_error
