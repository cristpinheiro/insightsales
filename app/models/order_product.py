"""
OrderProduct Model.

Intermediate table that implements the N:N relationship between Order and Product.
Stores which products are in each order and in what quantity.
"""

from typing import TYPE_CHECKING
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.order import Order
from app.models.product import Product


class OrderProduct(Base):
    """
    Associative table between Order and Product.

    This table resolves the many-to-many relationship:
    - An order can have multiple products
    - A product can be in multiple orders

    The primary key is COMPOSITE (order_id + product_id), ensuring
    that the same product doesn't appear twice in the same order.

    Attributes:
        order_id: Order ID (part of composite PK, FK)
        product_id: Product ID (part of composite PK, FK)
        quantity: How many units of the product in the order
        order: Associated Order object (relationship)
        product: Associated Product object (relationship)

    Usage example:
        # Add 5 notebooks to order 10
        item = OrderProduct(
            order_id=10,
            product_id=3,  # Notebook ID
            quantity=5
        )
        session.add(item)
        await session.commit()

        # Calculate this item's value
        item_value = item.quantity * item.product.price
        print(f"Value: $ {item_value}")

        # Access order and product information
        print(f"Order #{item.order.id} - {item.quantity}x {item.product.name}")

    Note about Composite Primary Key:
        The combination of order_id + product_id must be unique.
        This prevents duplicates like:
        - Order 1, Product 3, Quantity 2 ✅
        - Order 1, Product 3, Quantity 5 ❌ (duplicate!)

        If you need to change the quantity, do UPDATE, not INSERT.
    """

    __tablename__ = "order_product"

    # Composite primary key (both fields are PK and FK at the same time)
    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("order.id", ondelete="CASCADE"),  # Deletes if order is deleted
        primary_key=True,
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("product.id"), primary_key=True
    )

    # Quantity of the product in the order
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Relationships (to easily access related objects)
    order: Mapped["Order"] = relationship("Order", back_populates="order_products")

    product: Mapped["Product"] = relationship(
        "Product", back_populates="order_products"
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<OrderProduct(order_id={self.order_id}, "
            f"product_id={self.product_id}, quantity={self.quantity})>"
        )
