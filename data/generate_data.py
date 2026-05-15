"""
RetailIQ – Synthetic Data Generator
Generates realistic retail sales & customer data for analytics.
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

fake = Faker("en_IN")
np.random.seed(42)
random.seed(42)

# ── Constants ─────────────────────────────────────────────────────────────────
N_CUSTOMERS   = 2_000
N_PRODUCTS    = 150
N_STORES      = 12
N_TRANSACTIONS = 50_000
START_DATE    = datetime(2022, 1, 1)
END_DATE      = datetime(2024, 12, 31)

CATEGORIES = {
    "Electronics":    ["Smartphone", "Laptop", "Tablet", "Headphones", "Smart Watch",
                       "Camera", "Speaker", "Charger", "Power Bank", "Earbuds"],
    "Clothing":       ["T-Shirt", "Jeans", "Dress", "Jacket", "Shoes", "Kurta",
                       "Saree", "Formal Shirt", "Shorts", "Sweater"],
    "Groceries":      ["Rice", "Wheat Flour", "Cooking Oil", "Sugar", "Salt",
                       "Pulses", "Spices", "Tea", "Coffee", "Biscuits"],
    "Home & Kitchen": ["Pressure Cooker", "Non-Stick Pan", "Mixer Grinder",
                       "Dinner Set", "Water Bottle", "Storage Box", "Curtains",
                       "Bedsheet", "Pillow", "Lamp"],
    "Beauty":         ["Face Wash", "Moisturizer", "Lipstick", "Shampoo",
                       "Conditioner", "Perfume", "Sunscreen", "Nail Polish",
                       "Foundation", "Serum"],
    "Sports":         ["Yoga Mat", "Dumbbells", "Running Shoes", "Cricket Bat",
                       "Football", "Badminton Racket", "Cycling Gloves",
                       "Water Sipper", "Gym Bag", "Jump Rope"],
    "Books":          ["Self-Help Book", "Novel", "Textbook", "Children's Book",
                       "Biography", "Recipe Book", "Business Book",
                       "Science Book", "History Book", "Poetry Collection"],
    "Toys":           ["Board Game", "Puzzle", "Action Figure", "Doll",
                       "LEGO Set", "Remote Car", "Art Kit", "Building Blocks",
                       "Card Game", "Stuffed Animal"],
}

CITIES = ["Hyderabad", "Mumbai", "Delhi", "Bengaluru", "Chennai",
          "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
          "Chandigarh", "Kochi"]

PAYMENT_METHODS  = ["UPI", "Credit Card", "Debit Card", "Cash", "Net Banking", "Wallet"]
RETURN_REASONS   = ["Defective Product", "Wrong Item", "Changed Mind",
                    "Size Issue", "Quality Issue"]
CHANNELS         = ["In-Store", "Online", "Mobile App"]

# ── Helpers ───────────────────────────────────────────────────────────────────
def random_date(start: datetime, end: datetime) -> datetime:
    delta = (end - start).days
    # Add seasonality: Q4 + festival months get higher weight
    month_weights = [1,1,1,1,1,1,1,1,1.3,1.8,2.2,2.0]
    dates = [start + timedelta(days=i) for i in range(delta)]
    weights = [month_weights[d.month - 1] for d in dates]
    total = sum(weights)
    weights = [w / total for w in weights]
    return np.random.choice(dates, p=weights)  # type: ignore


# ── 1. Customers ──────────────────────────────────────────────────────────────
def generate_customers() -> pd.DataFrame:
    print("Generating customers …")
    records = []
    segments = np.random.choice(
        ["Premium", "Regular", "Budget"],
        size=N_CUSTOMERS,
        p=[0.20, 0.55, 0.25]
    )
    for i in range(N_CUSTOMERS):
        city = random.choice(CITIES)
        seg  = segments[i]
        records.append({
            "customer_id":    f"CUST{i+1:05d}",
            "name":           fake.name(),
            "email":          fake.email(),
            "phone":          fake.phone_number(),
            "city":           city,
            "state":          fake.state(),
            "age":            random.randint(18, 70),
            "gender":         random.choice(["Male", "Female", "Other"]),
            "segment":        seg,
            "join_date":      (START_DATE - timedelta(days=random.randint(0, 730))).date(),
            "is_loyalty_member": random.random() < (0.7 if seg == "Premium" else 0.35),
        })
    return pd.DataFrame(records)


# ── 2. Products ───────────────────────────────────────────────────────────────
def generate_products() -> pd.DataFrame:
    print("Generating products …")
    records = []
    pid = 1
    for cat, items in CATEGORIES.items():
        for item in items:
            base_price = {
                "Electronics": random.uniform(500, 80_000),
                "Clothing":    random.uniform(199, 5_000),
                "Groceries":   random.uniform(30, 500),
                "Home & Kitchen": random.uniform(199, 8_000),
                "Beauty":      random.uniform(99, 3_000),
                "Sports":      random.uniform(199, 10_000),
                "Books":       random.uniform(99, 999),
                "Toys":        random.uniform(199, 4_000),
            }[cat]
            records.append({
                "product_id":   f"PROD{pid:04d}",
                "product_name": item,
                "category":     cat,
                "brand":        fake.company().split()[0],
                "unit_price":   round(base_price, 2),
                "cost_price":   round(base_price * random.uniform(0.45, 0.70), 2),
                "stock_qty":    random.randint(10, 500),
                "supplier_city": random.choice(CITIES),
            })
            pid += 1
    return pd.DataFrame(records)


# ── 3. Stores ─────────────────────────────────────────────────────────────────
def generate_stores() -> pd.DataFrame:
    print("Generating stores …")
    records = []
    for i, city in enumerate(CITIES):
        records.append({
            "store_id":   f"STR{i+1:03d}",
            "store_name": f"RetailIQ {city}",
            "city":       city,
            "region":     ("South" if city in ["Hyderabad","Bengaluru","Chennai","Kochi"]
                           else "West" if city in ["Mumbai","Pune","Ahmedabad"]
                           else "East" if city in ["Kolkata"]
                           else "North"),
            "size_sqft":  random.randint(2_000, 15_000),
            "manager":    fake.name(),
            "open_date":  (START_DATE - timedelta(days=random.randint(180, 1800))).date(),
        })
    return pd.DataFrame(records)


# ── 4. Transactions ───────────────────────────────────────────────────────────
def generate_transactions(customers: pd.DataFrame,
                           products: pd.DataFrame,
                           stores: pd.DataFrame) -> pd.DataFrame:
    print("Generating transactions …")
    cust_ids  = customers["customer_id"].tolist()
    prod_ids  = products["product_id"].tolist()
    store_ids = stores["store_id"].tolist()
    price_map = products.set_index("product_id")["unit_price"].to_dict()
    cost_map  = products.set_index("product_id")["cost_price"].to_dict()

    records = []
    for i in range(N_TRANSACTIONS):
        prod_id   = random.choice(prod_ids)
        unit_price = price_map[prod_id]
        quantity   = random.choices([1,2,3,4,5], weights=[50,25,12,8,5])[0]
        discount_pct = random.choices([0,5,10,15,20,25], weights=[40,20,18,10,8,4])[0]
        discount_amt = round(unit_price * quantity * discount_pct / 100, 2)
        total_amt    = round(unit_price * quantity - discount_amt, 2)
        cost_amt     = round(cost_map[prod_id] * quantity, 2)
        profit       = round(total_amt - cost_amt, 2)
        tx_date      = random_date(START_DATE, END_DATE)

        records.append({
            "transaction_id": f"TXN{i+1:07d}",
            "customer_id":    random.choice(cust_ids),
            "product_id":     prod_id,
            "store_id":       random.choice(store_ids),
            "date":           tx_date.date(),
            "month":          tx_date.month,
            "year":           tx_date.year,
            "quarter":        f"Q{(tx_date.month-1)//3+1}",
            "quantity":       quantity,
            "unit_price":     unit_price,
            "discount_pct":   discount_pct,
            "discount_amt":   discount_amt,
            "total_amount":   total_amt,
            "cost_amount":    cost_amt,
            "profit":         profit,
            "payment_method": random.choice(PAYMENT_METHODS),
            "channel":        random.choice(CHANNELS),
            "is_returned":    random.random() < 0.05,
            "return_reason":  random.choice(RETURN_REASONS) if random.random() < 0.05 else None,
            "rating":         random.choices([1,2,3,4,5], weights=[3,5,15,40,37])[0],
        })

    return pd.DataFrame(records)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    out = os.path.join(os.path.dirname(__file__))

    customers    = generate_customers()
    products     = generate_products()
    stores       = generate_stores()
    transactions = generate_transactions(customers, products, stores)

    customers.to_csv(f"{out}/customers.csv",    index=False)
    products.to_csv(f"{out}/products.csv",      index=False)
    stores.to_csv(f"{out}/stores.csv",          index=False)
    transactions.to_csv(f"{out}/transactions.csv", index=False)

    print("\n✅ Data generation complete!")
    print(f"   Customers   : {len(customers):,}")
    print(f"   Products    : {len(products):,}")
    print(f"   Stores      : {len(stores):,}")
    print(f"   Transactions: {len(transactions):,}")
    print(f"   Total Revenue: ₹{transactions['total_amount'].sum():,.0f}")
    print(f"   Total Profit : ₹{transactions['profit'].sum():,.0f}")


if __name__ == "__main__":
    main()
