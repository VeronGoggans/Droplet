import time
from src.droplet.database import Database



db = Database()

start = time.perf_counter()

db.open()

db.set_many({
    'apples': 100,
    'berries': 200,
    'Kiwis': 200,
    'strawberries': 50,
    'bananas': 70,
    'peaches': 120
})
print(db.greater_than_or_equal(value=100))
print(db.less_than_or_equal(value=100))
print(db.where(value=200))
print(db.view())

db.close()

end = time.perf_counter()

print(f"Took {end - start:.6f} seconds")

