---
title: "Feature request: limit the number of results returned by search()"
type: feature
---
I have a table with ~50k log entries and most of the time I only need the first few matches (to show a preview in a small CLI). Right now I do `db.search(q)[:10]`, which builds the full list every time.

Could `search()` take an optional `limit` argument? Something like

```python
db.search(Query().level == 'error', limit=10)
```

returning at most 10 matching documents, in the same order `search()` returns them today. Without `limit` it should behave exactly as it does now.
