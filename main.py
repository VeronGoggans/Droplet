from stormdb.stormdb import StormDB


db = StormDB()

db.open()

db.add('name', 'Veron Goggans')
db.add('age', 22)
db.add('height', 1.87)
db.add('adult', True)

print(db.get('name'))
print(db.get('age'))
print(db.get('height'))
print(db.get('adult'))

db.close()


