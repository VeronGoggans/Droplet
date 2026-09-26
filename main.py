from stormdb.stormdb import StormDB
import uuid


db = StormDB()

# db.open()

# db.set('name', 'Veron Goggans')
# db.set('age', 22)
# db.set('height', 1.87)
# db.set('adult', False)
# db.set('test', None)
# db.set('ID', uuid.uuid4())

# print(db.get('name'))
# print(db.get('age'))
# print(db.get('height'))
# print(db.get('adult'))
# print(db.get('test'))
# print(db.get('ID'))

# db.close()

db.open()
db.export_to_json()

