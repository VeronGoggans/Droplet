from pathlib import Path
from droplet import Droplet

db_path = Path('docs/database.droplet')
db = Droplet(path=db_path)

db.open()
# db.set_many({
#     'username-1': 'Bob',
#     'username-2': 'bill',
#     'username-3': 'ben' 
# })
print(db.get_many(['username-1', 'username-2', 'username-3']))
print(db.compare_and_set('username-1', 'Bob', 'Bobby'))
print(db.compare_and_set('username-1', 'Bob', 'Jenkins'))
db.close()
