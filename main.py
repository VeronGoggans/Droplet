from droplet import Database

db = Database()
db.open()
db.set('hello', 'world')
key = db.get('hello')
db.close()

print(key)

