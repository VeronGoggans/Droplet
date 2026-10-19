from droplet import Droplet
from tests.test_data import generate_test_data

db = Droplet()
db.open()

# data = generate_test_data()

# for namespace, records in data.items():
#     db.set_batch(records, namespace=namespace)

# print("Total records:", db.count())
# print("Users:", len(db.get_batch(
#     ["user_1", "user_2", "user_3"],
#     namespace="users"
# )))
# print("Example user:", db.get("user_1", namespace="users"))
# print("Example product:", db.get("product_1", namespace="products"))
# print("Example order:", db.get("order_1", namespace="orders"))

# print("Values over 500:", len(db.greater_than(500)))
# print("Values below 100:", len(db.less_than(100)))
settings = db.get_namespace('settings')
for key, value in settings.items():
    print(key)
    print(value)
    print()
db.close()