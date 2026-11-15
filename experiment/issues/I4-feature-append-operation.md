---
title: "Add an update operation that appends a value to a list field"
type: feature
---
Most of my documents have a `tags` list, and to add a tag I currently write my own transform every time:

```python
def add_tag(tag):
    def transform(doc):
        doc['tags'].append(tag)
    return transform

db.update(add_tag('urgent'), Query().id == 7)
```

It would be nice to have this built in next to `increment`, `add`, `set` and friends in `tinydb.operations`, e.g.

```python
from tinydb.operations import append
db.update(append('tags', 'urgent'), Query().id == 7)
```

If a matching document doesn't have the field yet, it should be created as a list containing just that value.
