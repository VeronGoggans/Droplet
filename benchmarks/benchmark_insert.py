import time

from pathlib import Path
from droplet import Database 



db_path = Path.cwd() / 'benchmarks'

db = Database(path=db_path)
entries = {
    f"key_{i}": i
    for i in range(1000000)
}


db.open()
start = time.perf_counter()

db.set_many(entries)

end = time.perf_counter()
db.close()


print(f"Inserted {len(entries)} entries")
print(f"Took {(end - start) * 1000:.3f} ms")

db.path.unlink()