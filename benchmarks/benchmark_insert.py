import time

from pathlib import Path

from droplet import Droplet


RUNS = 10
ENTRIES = 1_000_000

db_path = Path.cwd() / 'benchmarks'

entries = {
    f"key_{i}": i
    for i in range(ENTRIES)
}

latencies = []
db_size = None

for _ in range(RUNS):
    db = Droplet(path=db_path)
    db.open()

    start = time.perf_counter()
    db.set_many(entries)
    end = time.perf_counter()

    db.close()
    latencies.append(end - start)
    
    if db_size is None:
        db_size = db.path.stat().st_size
    
    db.path.unlink()



print(f"Inserted {len(entries):,} entries")
print(f"Runs: {RUNS}")
print(f"Average latency: {(sum(latencies) / RUNS) * 1000:.3f} ms")
print(f"Database size: {db_size / (1024 * 1024):.2f} MB")



'''
Benchmark Results

Deleted 1,000,000 entries
Runs: 10
Average latency: 508.328 ms
Database size: 26.60 MB

'''