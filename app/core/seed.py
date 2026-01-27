"""
Database seeding utilities.

Functions to populate the database with sample data for testing and development.
"""

from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.database import Seller, Customer, Product, Order, OrderProduct


async def seed_sellers(db: AsyncSession) -> list[Seller]:
    """Create sample sellers."""
    sellers_data = [
        {"name": "John Smith"},
        {"name": "Maria Garcia"},
        {"name": "Robert Johnson"},
        {"name": "Ana Silva"},
        {"name": "Michael Brown"},
        {"name": "Sarah Davis"},
        {"name": "Carlos Rodriguez"},
        {"name": "Emily Wilson"},
        {"name": "James Martinez"},
        {"name": "Patricia Anderson"},
        {"name": "David Taylor"},
        {"name": "Jennifer Thomas"},
        {"name": "Christopher Moore"},
        {"name": "Linda Jackson"},
        {"name": "Daniel White"},
        {"name": "Barbara Harris"},
        {"name": "Matthew Clark"},
        {"name": "Jessica Lewis"},
        {"name": "Anthony Walker"},
        {"name": "Susan Hall"},
    ]

    sellers = []
    for data in sellers_data:
        seller = Seller(**data)
        db.add(seller)
        sellers.append(seller)

    await db.flush()
    print(f"✅ Created {len(sellers)} sellers")
    return sellers


async def seed_customers(db: AsyncSession, sellers: list[Seller]) -> list[Customer]:
    """Create sample customers linked to sellers."""
    customer_names = [
        "Tech Corp",
        "Global Industries",
        "StartUp Inc",
        "Mega Store",
        "Small Business LLC",
        "Enterprise Solutions",
        "Local Shop",
        "Big Company",
        "Medium Corp",
        "Tiny Business",
        "Digital Ventures",
        "Retail Chain",
        "Marketing Agency",
        "Construction Co",
        "Healthcare Plus",
        "Finance Group",
        "Education Center",
        "Food Services",
        "Transport Ltd",
        "Energy Systems",
        "Manufacturing Co",
        "Real Estate Inc",
        "Insurance Partners",
        "Legal Associates",
        "Consulting Firm",
        "Design Studio",
        "Software House",
        "Hardware Store",
        "Fashion Boutique",
        "Sports Equipment",
        "Auto Parts",
        "Electronics Shop",
        "Furniture World",
        "Garden Center",
        "Pet Supplies",
        "Book Store",
        "Music Shop",
        "Art Gallery",
        "Travel Agency",
        "Hotel Chain",
        "Restaurant Group",
        "Cafe Network",
        "Bakery Delights",
        "Grocery Market",
        "Pharmacy Plus",
        "Beauty Salon",
        "Fitness Center",
        "Dental Clinic",
        "Veterinary Care",
        "Home Services",
    ]

    customers_data = []
    for i, name in enumerate(customer_names):
        # Distribute customers across sellers
        seller_id = sellers[i % len(sellers)].id
        customers_data.append({"name": name, "seller_id": seller_id})

    customers = []
    for data in customers_data:
        customer = Customer(**data)
        db.add(customer)
        customers.append(customer)

    await db.flush()
    print(f"✅ Created {len(customers)} customers")
    return customers


async def seed_products(db: AsyncSession) -> list[Product]:
    """Create sample products."""
    products_data = [
        {"name": "Laptop", "price": Decimal("999.99")},
        {"name": "Mouse", "price": Decimal("29.99")},
        {"name": "Keyboard", "price": Decimal("79.99")},
        {"name": "Monitor", "price": Decimal("299.99")},
        {"name": "Headphones", "price": Decimal("149.99")},
        {"name": "Webcam", "price": Decimal("89.99")},
        {"name": "USB Cable", "price": Decimal("9.99")},
        {"name": "Desk Chair", "price": Decimal("199.99")},
        {"name": "Desk Lamp", "price": Decimal("39.99")},
        {"name": "Notebook", "price": Decimal("4.99")},
        {"name": "Desktop Computer", "price": Decimal("1299.99")},
        {"name": "Tablet", "price": Decimal("499.99")},
        {"name": "Smartphone", "price": Decimal("799.99")},
        {"name": "Printer", "price": Decimal("249.99")},
        {"name": "Scanner", "price": Decimal("179.99")},
        {"name": "External Hard Drive", "price": Decimal("119.99")},
        {"name": "SSD 1TB", "price": Decimal("139.99")},
        {"name": "RAM 16GB", "price": Decimal("89.99")},
        {"name": "Graphics Card", "price": Decimal("599.99")},
        {"name": "Motherboard", "price": Decimal("199.99")},
        {"name": "Power Supply", "price": Decimal("79.99")},
        {"name": "PC Case", "price": Decimal("69.99")},
        {"name": "Cooling Fan", "price": Decimal("29.99")},
        {"name": "Router", "price": Decimal("99.99")},
        {"name": "Network Switch", "price": Decimal("149.99")},
        {"name": "USB Hub", "price": Decimal("34.99")},
        {"name": "HDMI Cable", "price": Decimal("19.99")},
        {"name": "Microphone", "price": Decimal("129.99")},
        {"name": "Speakers", "price": Decimal("159.99")},
        {"name": "Wireless Mouse", "price": Decimal("39.99")},
    ]

    products = []
    for data in products_data:
        product = Product(**data)
        db.add(product)
        products.append(product)

    await db.flush()
    print(f"✅ Created {len(products)} products")
    return products


async def seed_orders(
    db: AsyncSession, sellers: list[Seller], customers: list[Customer]
) -> list[Order]:
    """Create sample orders."""
    today = date.today()

    orders_data = []
    # Create 100 orders distributed over the last 90 days
    for i in range(100):
        seller_idx = i % len(sellers)
        customer_idx = i % len(customers)
        days_ago = (i * 90) // 100  # Distribute evenly over 90 days

        orders_data.append(
            {
                "seller_id": sellers[seller_idx].id,
                "customer_id": customers[customer_idx].id,
                "date": today - timedelta(days=days_ago),
            }
        )

    orders = []
    for data in orders_data:
        order = Order(**data)
        db.add(order)
        orders.append(order)

    await db.flush()
    print(f"✅ Created {len(orders)} orders")
    return orders


async def seed_order_products(
    db: AsyncSession, orders: list[Order], products: list[Product]
) -> list[OrderProduct]:
    """Create sample order-product associations."""
    import random

    order_products_data = []

    # Each order will have 2-5 products
    for order in orders:
        num_products = random.randint(2, 5)
        # Select random products for this order
        selected_products = random.sample(products, num_products)

        for product in selected_products:
            quantity = random.randint(1, 10)
            order_products_data.append(
                {
                    "order_id": order.id,
                    "product_id": product.id,
                    "quantity": quantity,
                }
            )

    order_products = []
    for data in order_products_data:
        order_product = OrderProduct(**data)
        db.add(order_product)
        order_products.append(order_product)

    await db.flush()
    print(f"✅ Created {len(order_products)} order-product associations")
    return order_products


async def seed_database(db: AsyncSession) -> None:
    """
    Populate database with sample data.

    This function creates sample data for all tables in the correct order
    to respect foreign key constraints.

    Usage:
        from app.core.seed import seed_database
        from app.core.database import get_db

        async with get_db() as db:
            await seed_database(db)
    """
    print("\n" + "=" * 60)
    print("🌱 Seeding database with sample data...")
    print("=" * 60 + "\n")

    # Check if data already exists
    result = await db.execute(select(Seller))
    if result.scalars().first():
        print("⚠️  Database already contains data. Skipping seed.")
        return

    # Seed in order of dependencies
    sellers = await seed_sellers(db)
    customers = await seed_customers(db, sellers)
    products = await seed_products(db)
    orders = await seed_orders(db, sellers, customers)
    await seed_order_products(db, orders, products)

    # Commit all changes
    await db.commit()

    print("\n" + "=" * 60)
    print("✅ Database seeded successfully!")
    print("=" * 60)


async def clear_database(db: AsyncSession) -> None:
    """
    Clear all data from database tables.

    ⚠️ WARNING: This deletes all data but keeps table structure!
    Use only in development/testing.
    """
    print("\n" + "=" * 60)
    print("🗑️  Clearing all database data...")
    print("=" * 60 + "\n")

    # Delete in reverse order of dependencies
    await db.execute(OrderProduct.__table__.delete())
    print("✅ Cleared order_product")

    await db.execute(Order.__table__.delete())
    print("✅ Cleared order")

    await db.execute(Customer.__table__.delete())
    print("✅ Cleared customer")

    await db.execute(Product.__table__.delete())
    print("✅ Cleared product")

    await db.execute(Seller.__table__.delete())
    print("✅ Cleared seller")

    await db.commit()

    print("\n" + "=" * 60)
    print("✅ Database cleared successfully!")
    print("=" * 60)


# Standalone script execution
if __name__ == "__main__":
    import asyncio
    from app.core.database import AsyncSessionLocal

    async def main():
        async with AsyncSessionLocal() as db:
            await seed_database(db)

    asyncio.run(main())
