from src.droplet import Droplet

db = Droplet()
db.open()
db.set('hello', 'world')
key = db.get('hello')
db.close()

print(key)

