---
title: "one_of() with a generator only matches some of the documents"
type: bug
---
The docstring of `Query.one_of` says it checks whether the value "is contained in a list or generator", so I passed a generator of allowed tags:

```python
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

db = TinyDB(storage=MemoryStorage)
db.insert_multiple([{'tag': 'a'}, {'tag': 'b'}, {'tag': 'a'}, {'tag': 'c'}])

allowed = (t for t in ['a', 'b'])
print(db.search(Query().tag.one_of(allowed)))
# expected: [{'tag': 'a'}, {'tag': 'b'}, {'tag': 'a'}]
# actual:   [{'tag': 'a'}, {'tag': 'b'}]
```

With a list it works fine. In my real code the allowed values come from another generator expression, so I'd rather not have to remember to wrap it in `list()`.
