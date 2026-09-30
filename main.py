from pathlib import Path
from droplet import Droplet

db_path = Path('docs/database.dpt')
db = Droplet(path=db_path)

db.open()
print(db.view())
db.close()


