from tinydb import TinyDB, where, Query
from tinydb.storages import MemoryStorage


def _db(*docs):
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple(list(docs))
    return db


def test_fr_ops_001_ac_1_append_to_existing_list():
    from tinydb.operations import append
    db = _db({'id': 7, 'tags': ['a']})
    db.update(append('tags', 'urgent'), Query().id == 7)
    assert db.get(Query().id == 7)['tags'] == ['a', 'urgent']


def test_fr_ops_001_ac_2_only_matching_changed():
    from tinydb.operations import append
    db = _db({'id': 7, 'tags': ['a']}, {'id': 8, 'tags': ['b']})
    db.update(append('tags', 'urgent'), Query().id == 7)
    assert db.get(Query().id == 8)['tags'] == ['b']
    assert db.get(Query().id == 7)['tags'] == ['a', 'urgent']


def test_fr_ops_001_ac_3_mutates_in_place():
    from tinydb.operations import append
    doc = {'tags': ['a']}
    assert append('tags', 'urgent')(doc) is None
    assert doc == {'tags': ['a', 'urgent']}


def test_fr_ops_001_ac_4_no_dedup():
    from tinydb.operations import append
    db = _db({'id': 7, 'tags': ['a']})
    db.update(append('tags', 'urgent'), Query().id == 7)
    db.update(append('tags', 'urgent'), Query().id == 7)
    assert db.get(Query().id == 7)['tags'] == ['a', 'urgent', 'urgent']


def test_fr_ops_002_ac_1_missing_field_db():
    from tinydb.operations import append
    db = _db({'id': 7})
    db.update(append('tags', 'urgent'), Query().id == 7)
    assert db.get(Query().id == 7)['tags'] == ['urgent']


def test_fr_ops_002_ac_2_missing_field_dict():
    from tinydb.operations import append
    doc = {'id': 7}
    append('tags', 'urgent')(doc)
    assert doc == {'id': 7, 'tags': ['urgent']}


def test_fr_ops_002_ac_3_mixed_documents():
    from tinydb.operations import append
    db = _db({'id': 7}, {'id': 8, 'tags': ['b']})
    db.update(append('tags', 'urgent'), Query().id.one_of([7, 8]))
    assert db.get(Query().id == 7)['tags'] == ['urgent']
    assert db.get(Query().id == 8)['tags'] == ['b', 'urgent']
