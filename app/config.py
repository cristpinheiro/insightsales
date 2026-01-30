import os

# Database Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "your_database"),
    "user": os.getenv("DB_USER", "your_user"),
    "password": os.getenv("DB_PASSWORD", "your_password"),
    "port": os.getenv("DB_PORT", "5432"),
}

# Model Configuration
MODEL_NAME = os.getenv("MODEL_NAME", "insightsales")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# API Configuration
API_TITLE = "NL to SQL API"
API_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
