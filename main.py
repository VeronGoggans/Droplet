import time
from stormdb.stormdb import Database



db = Database()

start = time.perf_counter()

db.open()
db.close()

end = time.perf_counter()

print(f"Took {end - start:.6f} seconds")