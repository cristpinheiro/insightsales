"""
Product Model.

Represents a catalog product.
Products can be in multiple orders.
"""

from decimal import Decimal
from typing import TYPE_CHECKING, List
from sqlalchemy import Integer, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.order_product import OrderProduct


class Product(Base):
    """
    Products table.

    Stores the catalog of products available for sale.

    Attributes:
        id: Unique identifier for the product
        name: Product name/description
        price: Unit price (uses Decimal for monetary precision)
        order_products: List of relationships with orders (N:N)

    Usage example:
        product = Product(
            name="Dell Inspiron Notebook",
            price=Decimal("3500.00")
        )
        session.add(product)
        await session.commit()

        # Calculate total sold
        total = sum(op.quantity * product.price
                   for op in product.order_products)
        print(f"Total sold: $ {total}")

    Note about Decimal:
        We use Decimal instead of float to avoid rounding errors
        in monetary values. Example:
        - float: 0.1 + 0.2 = 0.30000000000000004 ❌
        - Decimal: 0.1 + 0.2 = 0.3 ✅
    """

    __tablename__ = "product"

    # Columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),  # 10 total digits, 2 decimal places
        nullable=False,  # Example: 99999999.99
    )

    # N:N relationship with Order (through order_product table)
    order_products: Mapped[List["OrderProduct"]] = relationship(
        "OrderProduct", back_populates="product"
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
