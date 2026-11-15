---
title: "Searching with fragment() on a nested field returns the results of a different field"
type: bug
---
I'm storing user profiles with nested `home` and `work` addresses and searching each of them with `fragment()`. The second search gives me the result of the first one!

```python
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

db = TinyDB(storage=MemoryStorage)
db.insert({'name': 'ana', 'home': {'city': 'Pune'}, 'work': {'city': 'Delhi'}})
db.insert({'name': 'raj', 'home': {'city': 'Delhi'}, 'work': {'city': 'Pune'}})

User = Query()
print(db.search(User.home.fragment({'city': 'Pune'})))  # [ana] -> correct
print(db.search(User.work.fragment({'city': 'Pune'})))  # expected [raj], but I get [ana] again
```

If I open a fresh `TinyDB` between the two searches, the second one is correct, so it looks like some caching problem. Also `User.home.fragment({...}) == User.work.fragment({...})` is `True`, which surprised me.

tinydb 4.9.0, Python 3.12, Windows 11.
