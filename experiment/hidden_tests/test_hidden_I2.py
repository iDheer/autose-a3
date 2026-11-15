"""Hidden acceptance tests for I2 (one_of() with a generator)."""
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def _db():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'tag': 'a'}, {'tag': 'b'}, {'tag': 'a'}, {'tag': 'c'}])
    return db


def test_h1_generator_matches_every_matching_document():
    db = _db()
    res = db.search(Query().tag.one_of(t for t in ['a', 'b']))
    assert [d.doc_id for d in res] == [1, 2, 3]


def test_h2_generator_query_can_be_evaluated_many_times():
    q = Query().tag.one_of(t for t in ['a', 'b'])
    assert [q({'tag': v}) for v in ('a', 'b', 'a', 'b', 'c', 'a')] == [True, True, True, True, False, True]


def test_h3_lists_tuples_and_sets_still_work_and_repeat_search_is_stable():
    db = _db()
    for items in (['a', 'b'], ('a', 'b'), {'a', 'b'}):
        assert [d.doc_id for d in db.search(Query().tag.one_of(items))] == [1, 2, 3]
    q = Query().tag.one_of(iter(['c']))
    assert [d.doc_id for d in db.search(q)] == [4]
    assert [d.doc_id for d in db.search(q)] == [4]
