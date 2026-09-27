from stormdb.stormdb import StormDB
import uuid


db = StormDB()

db.open()

db.set('name', 'Veron Goggans')
db.set('age', 22)
db.set('height', 1.87)
db.set('adult', False)
db.set('test', None)
db.set('ID', uuid.uuid4())
db.set('bytes', uuid.uuid4().bytes)

print(db.get('name'))
print(db.get('age'))
print(db.get('height'))
print(db.get('adult'))
print(db.get('test'))
print(db.get('ID'))
print(db.get('bytes'))

print(uuid.UUID(bytes=db.get('bytes')))

db.export_to_json()
db.close()

    

