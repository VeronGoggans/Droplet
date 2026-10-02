from droplet import Droplet


from dataclasses import dataclass


@dataclass
class Planet:
    name: str
    radius: int
    size: int
    type: str



earth = Planet('Earth', 4000, 10000, 'Rocky')
mars = Planet('Mars', 3500, 7000, 'Rocky')

db = Droplet()
db.open()

print(db.get_batch_as(['earth', 'mars'], Planet))
print(db.get_batch(['earth', 'mars']))

db.close()

