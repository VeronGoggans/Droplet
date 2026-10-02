
![Droplet Logo](docs/droplet-logo.png)
# Droplet

**Small. Simple. Persistent.**

Droplet is a lightweight, file-backed key-value database for Python, designed to provide simple, persistent data storage without the complexity of a traditional database. 

Droplet stores your data locally in a single file and provides a small, straightforward API.

## Features

* 🔑 Key-value storage
* 💾 Persistent file-based storage
* 🐍 Built for Python
* 📦 Support for common Python types
* 🔄 CRUD operations
* 📝 Export data to JSON

## Example

```python
from droplet import Droplet

db = Droplet()

db.open()

db.set("name", "Droplet")
db.set("type", "key/value")

print(db.get("name"))
print(db.get("type"))

db.close()
```

## Vision

Droplet is intended to stay **small, simple, and useful**.

Droplet aims to be a lightweight database for Python projects that need persistent local storage without wanting to introduce a full database server or a complicated database layer.

**Planned features include:**

* Transactions
* Import from JSON support 
* TTL / expiring values

## Status

Droplet is currently an **early-stage project under active development**. The API and file format may change as the project evolves.

More documentation and examples will be added as the project matures.

## License

MIT
