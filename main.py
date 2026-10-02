from droplet import Droplet


db = Droplet()
db.open()
print(db.get('2adb12e2-c2af-4445-8324-8d051224cb03'))
db.close()
