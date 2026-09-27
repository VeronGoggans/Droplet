from stormdb.stormdb import Database
import uuid


db = Database()

db.open()



print(db.get('name'))
print(db.get('age'))




db.delete('height')
print(db.get('height'))

db.export()
db.close()


    

