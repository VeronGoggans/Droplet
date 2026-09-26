from pathlib import Path
from stormdb.stormdb import StormDB


# path = Path("stormdb.json")
db = StormDB(path=True)

db.open()

db.add('database-type', 'Key Value')
db.add('persistant', False)

db.update('persistant', True)
print(db.get('database-type'))

db.close()
