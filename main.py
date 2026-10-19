from droplet import Droplet
import time

db = Droplet()
db.open()

print(db.get_size())
db.compact()
print(db.get_size())

db.close()