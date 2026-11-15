"""Hidden acceptance tests for I4 (operations.append)."""
from tinydb import TinyDB, Query
from tinydb.operations import append
from tinydb.storages import MemoryStorage


def test_h1_append_adds_value_to_existing_list():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'id': 7, 'tags': ['a']})
    db.update(append('tags', 'urgent'), Query().id == 7)
    assert db.get(Query().id == 7)['tags'] == ['a', 'urgent']


def test_h2_append_creates_list_when_field_is_missing():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'id': 1})
    db.update(append('tags', 'x'), Query().id == 1)
    assert db.get(Query().id == 1)['tags'] == ['x']


def test_h3_only_matching_documents_change_and_change_is_persisted(tmp_path):
    path = tmp_path / 'db.json'
    with TinyDB(path) as db:
        db.insert_multiple([{'id': 1, 'tags': []}, {'id': 2, 'tags': ['k']}])
        db.update(append('tags', 'new'), Query().id == 2)
    with TinyDB(path) as db:
        assert db.get(Query().id == 1)['tags'] == []
        assert db.get(Query().id == 2)['tags'] == ['k', 'new']
