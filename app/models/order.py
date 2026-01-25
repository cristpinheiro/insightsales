"""
Order Model.

Represents a sales order made by a customer.
Each order is handled by a seller and contains multiple products.
"""

from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.seller import Seller
    from app.models.customer import Customer
    from app.models.order_product import OrderProduct


class Order(Base):
    """
    Orders table.

    An order connects:
    - Customer (who bought)
    - Seller (who sold)
    - Products (what was bought, through order_product)

    Attributes:
        id: Unique identifier for the order
        seller_id: ID of the seller who made the sale (FK)
        customer_id: ID of the customer who bought (FK)
        date: Date and time of the order
        seller: Associated Seller object (relationship)
        customer: Associated Customer object (relationship)
        order_products: List of order items (N:N relationship)

    Usage example:
        order = Order(
            seller_id=1,
            customer_id=5,
            date=datetime.now()
        )
        session.add(order)
        await session.flush()  # To get the ID

        # Add products to the order
        item = OrderProduct(
            order_id=order.id,
            product_id=3,
            quantity=2
        )
        session.add(item)
        await session.commit()

        # Calculate order total
        total = sum(op.quantity * op.product.price
                   for op in order.order_products)
        print(f"Order total: $ {total}")
    """

    __tablename__ = "order"

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    seller_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("seller.id"), nullable=False
    )
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customer.id"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,  # Uses UTC to avoid timezone issues
    )

    # Relationships
    seller: Mapped["Seller"] = relationship("Seller", back_populates="orders")

    customer: Mapped["Customer"] = relationship("Customer", back_populates="orders")

    order_products: Mapped[List["OrderProduct"]] = relationship(
        "OrderProduct",
        back_populates="order",
        cascade="all, delete-orphan",  # Deletes items if order is deleted
    )

    # Indexes to improve performance of common queries
    __table_args__ = (
        Index("idx_order_seller", "seller_id"),  # Orders by seller
        Index("idx_order_customer", "customer_id"),  # Orders by customer
        Index("idx_order_date", "date"),  # Orders by date
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<Order(id={self.id}, date={self.date}, "
            f"seller_id={self.seller_id}, customer_id={self.customer_id})>"
        )
