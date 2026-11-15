"""Hidden acceptance tests for I3 (search(..., limit=N))."""
from tinydb import TinyDB, Query, where
from tinydb.storages import MemoryStorage


def _db():
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'level': 'error' if i % 2 else 'info', 'i': i} for i in range(1, 8)])
    return db  # errors at doc_ids 1, 3, 5, 7


def test_h1_limit_returns_first_matches_in_search_order():
    db = _db()
    assert [d.doc_id for d in db.search(where('level') == 'error', limit=2)] == [1, 3]
    assert [d.doc_id for d in db.table('_default').search(where('level') == 'error', limit=3)] == [1, 3, 5]


def test_h2_without_limit_behaviour_is_unchanged():
    db = _db()
    assert [d.doc_id for d in db.search(where('level') == 'error')] == [1, 3, 5, 7]


def test_h3_limit_larger_than_matches_returns_all_matches():
    db = _db()
    assert [d.doc_id for d in db.search(where('level') == 'error', limit=100)] == [1, 3, 5, 7]


def test_h4_limited_and_unlimited_searches_do_not_poison_the_query_cache():
    db = _db()
    q = Query().level == 'error'
    assert len(db.search(q, limit=1)) == 1
    assert [d.doc_id for d in db.search(q)] == [1, 3, 5, 7]
    assert [d.doc_id for d in db.search(q, limit=2)] == [1, 3]
    assert len(db.search(q)) == 4
