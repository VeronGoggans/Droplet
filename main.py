from stormdb.stormdb import StormDB


db = StormDB()

db.open()
# db.add('name', 'Veron Goggans')
print(db.get('name'))
db.close()
