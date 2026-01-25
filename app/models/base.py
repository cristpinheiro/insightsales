"""
SQLAlchemy Base for all models.

This file defines the Base class that all models will inherit from.
It's important that all models use the SAME Base instance.
"""

from sqlalchemy.orm import declarative_base

# Base is the parent class of all models
# ALL models must inherit from this same instance
Base = declarative_base()
