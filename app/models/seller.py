"""
Seller Model.

Represents a company seller.
A seller can have multiple customers and multiple orders.
"""

from typing import List, TYPE_CHECKING
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.order import Order


class Seller(Base):
    """
    Sellers table.

    Attributes:
        id: Unique identifier for the seller
        name: Full name of the seller
        customers: List of associated customers (relationship)
        orders: List of orders made (relationship)

    Usage example:
        seller = Seller(name="John Silva")
        session.add(seller)
        await session.commit()

        # Access seller's customers
        print(f"Seller {seller.name} has {len(seller.customers)} customers")
    """

    __tablename__ = "seller"

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    # Relationships (defined here, but connect with other tables)
    # back_populates must match the attribute name in the other class
    customers: Mapped[List["Customer"]] = relationship(
        "Customer",
        back_populates="seller",
        cascade="all, delete-orphan",  # Deletes customers if seller is deleted
    )

    orders: Mapped[List["Order"]] = relationship("Order", back_populates="seller")

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Seller(id={self.id}, name='{self.name}')>"
