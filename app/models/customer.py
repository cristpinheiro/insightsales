"""
Customer Model.

Represents a company customer.
Each customer is associated with a specific seller.
"""

from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.seller import Seller
    from app.models.order import Order


class Customer(Base):
    """
    Customers table.

    Each customer:
    - Belongs to a seller (seller_id)
    - Can make multiple orders

    Attributes:
        id: Unique identifier for the customer
        name: Customer's name/company name
        seller_id: ID of the responsible seller (FK)
        seller: Associated Seller object (relationship)
        orders: List of customer orders (relationship)

    Usage example:
        customer = Customer(
            name="XYZ Company Ltd",
            seller_id=1
        )
        session.add(customer)
        await session.commit()

        # Access the customer's seller
        print(f"Customer served by: {customer.seller.name}")
    """

    __tablename__ = "customer"

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    seller_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("seller.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    seller: Mapped["Seller"] = relationship("Seller", back_populates="customers")

    orders: Mapped[List["Order"]] = relationship("Order", back_populates="customer")

    # Index to improve performance on queries by seller
    # Useful for queries like: "SELECT * FROM customer WHERE seller_id = ?"
    __table_args__ = (Index("idx_customer_seller", "seller_id"),)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<Customer(id={self.id}, name='{self.name}', seller_id={self.seller_id})>"
        )
