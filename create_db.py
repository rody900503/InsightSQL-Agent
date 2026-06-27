import sqlite3

conn = sqlite3.connect("sales.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_name TEXT,
    product_category TEXT,
    product_name TEXT,
    quantity INTEGER,
    unit_price REAL,
    order_date TEXT,
    region TEXT
)
""")

data = [
    (1, "Alice", "Electronics", "Laptop", 2, 1200, "2026-06-01", "UK"),
    (2, "Ben", "Electronics", "Phone", 5, 800, "2026-06-03", "UK"),
    (3, "Cathy", "Furniture", "Chair", 10, 100, "2026-06-05", "Taiwan"),
    (4, "David", "Furniture", "Desk", 4, 300, "2026-06-07", "Taiwan"),
    (5, "Eva", "Electronics", "Tablet", 3, 600, "2026-06-10", "US")
]

cursor.executemany("""
INSERT OR REPLACE INTO orders
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", data)

conn.commit()
conn.close()

print("Database created successfully!")