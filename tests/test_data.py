
from uuid import uuid4
from random import Random

rng = Random(42)


def generate_test_data():
    data = {}

    # 30 users: dictionaries, strings, integers, booleans, lists
    names = [
        "Lucia", "Jason", "Emma", "Oliver", "Sophia",
        "Noah", "Mia", "Lucas", "Amelia", "Ethan",
        "Isabella", "James", "Charlotte", "Henry", "Lily",
        "Benjamin", "Grace", "Leo", "Ella", "Daniel",
        "Chloe", "Alexander", "Zoe", "Samuel", "Aria",
        "Oscar", "Freya", "Jack", "Ruby", "Thomas",
    ]

    cities = [
        "Amsterdam", "Rotterdam", "Utrecht", "Eindhoven",
        "The Hague", "Breda", "Tilburg", "Groningen",
        "Leiden", "Nijmegen",
    ]

    users = {}
    for i, name in enumerate(names, start=1):
        users[f"user_{i}"] = {
            "id": i,
            "uuid": uuid4(),
            "name": name,
            "email": f"{name.lower()}@example.com",
            "age": rng.randint(18, 65),
            "active": i % 4 != 0,
            "city": rng.choice(cities),
            "roles": ["user"] if i % 3 else ["user", "moderator"],
            "score": round(rng.uniform(0, 100), 2),
        }

    data["users"] = users

    # 30 products: prices, stock, categories, availability
    categories = ["Electronics", "Books", "Home", "Clothing", "Sports"]
    products = {}

    for i in range(1, 31):
        products[f"product_{i}"] = {
            "id": i,
            "name": f"Product {i:03}",
            "category": categories[(i - 1) % len(categories)],
            "price": round(rng.uniform(4.99, 999.99), 2),
            "stock": rng.randint(0, 250),
            "available": i % 7 != 0,
            "tags": ["featured", "sale"] if i % 5 == 0 else ["standard"],
        }

    data["products"] = products

    # 30 orders: mixed IDs, numbers, booleans, lists and dictionaries
    orders = {}
    statuses = ["pending", "paid", "shipped", "delivered", "cancelled"]

    for i in range(1, 31):
        orders[f"order_{i}"] = {
            "id": i,
            "order_number": f"ORD-{2026}{i:04}",
            "user_id": rng.randint(1, 30),
            "total": round(rng.uniform(15, 1500), 2),
            "status": statuses[(i - 1) % len(statuses)],
            "paid": i % 5 != 0,
            "item_ids": [
                rng.randint(1, 30)
                for _ in range(rng.randint(1, 4))
            ],
            "shipping": {
                "city": rng.choice(cities),
                "express": i % 3 == 0,
            },
        }

    data["orders"] = orders

    # 20 settings: strings, booleans, integers, floats and lists
    settings = {}
    for i in range(1, 21):
        settings[f"setting_{i}"] = {
            "theme": ["light", "dark", "system"][i % 3],
            "notifications": i % 2 == 0,
            "font_size": 12 + (i % 9),
            "zoom": round(0.8 + (i % 5) * 0.1, 2),
            "shortcuts": ["Ctrl+S", "Ctrl+P"] if i % 2 else [],
        }

    data["settings"] = settings

    # 20 counters: integers and floats
    counters = {}
    for i in range(1, 21):
        counters[f"counter_{i}"] = {
            "value": i * 10,
            "increment": i,
            "ratio": round(i / 3, 4),
            "enabled": i % 2 == 0,
        }

    data["counters"] = counters

    # 20 miscellaneous values: primitive types and UUIDs
    misc = {}
    for i in range(1, 21):
        misc[f"misc_{i}"] = [
            f"sample_{i}",
            i * 5,
            i % 2 == 0,
            round(i * 1.25, 2),
            uuid4(),
        ]

    data["misc"] = misc

    return data
