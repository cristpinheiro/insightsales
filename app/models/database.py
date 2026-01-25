"""
Centralized model imports.

This file facilitates importing models in other modules.
Instead of importing from each individual file, you can do:

    from app.models.database import Seller, Customer, Product, Order, OrderProduct

Models have been separated into individual files for better organization:
"""

# Import Base first
from app.models.base import Base

# Import all models (order matters because of relationships!)
from app.models.seller import Seller
from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order
from app.models.order_product import OrderProduct

# List of all models (useful for creating tables)
__all__ = ["Base", "Seller", "Customer", "Product", "Order", "OrderProduct"]


# ============================================================================
# SCHEMA DIAGRAM
# ============================================================================
"""
RELATIONSHIPS BETWEEN TABLES:

┌─────────────────┐
│   Seller        │
│ ─────────────── │
│ • id (PK)       │◄──────┐
│ • name          │       │
└─────────────────┘       │
                          │
                          │ seller_id (FK)
                          │
┌─────────────────┐       │
│   Customer      │       │
│ ─────────────── │       │
│ • id (PK)       │       │
│ • name          │       │
│ • seller_id     │───────┘
└─────────────────┘
        │
        │ customer_id (FK)
        │
        ▼
┌─────────────────┐
│   Order         │
│ ─────────────── │
│ • id (PK)       │◄───────────────┐
│ • seller_id     │                │
│ • customer_id   │                │ order_id (FK)
│ • date          │                │
└─────────────────┘        ┌───────────────────┐
                           │  OrderProduct     │
┌─────────────────┐        │ ───────────────── │
│   Product       │        │ • order_id (PK)   │
│ ─────────────── │        │ • product_id (PK) │
│ • id (PK)       │◄───────│ • quantity        │
│ • name          │        └───────────────────┘
│ • price         │                │
└─────────────────┘                │ product_id (FK)
"""
