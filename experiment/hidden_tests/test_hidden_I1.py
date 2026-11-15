"""Hidden acceptance tests for I1 (fragment() query cache / hash ignores the path)."""
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def _db():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'ana', 'home': {'city': 'Pune'}, 'work': {'city': 'Delhi'}})
    db.insert({'name': 'raj', 'home': {'city': 'Delhi'}, 'work': {'city': 'Pune'}})
    return db


def test_h1_second_fragment_search_on_other_path_is_not_served_from_cache():
    db, User = _db(), Query()
    assert [d['name'] for d in db.search(User.home.fragment({'city': 'Pune'}))] == ['ana']
    assert [d['name'] for d in db.search(User.work.fragment({'city': 'Pune'}))] == ['raj']


def test_h2_fragment_queries_on_different_paths_are_not_equal():
    User = Query()
    assert User.home.fragment({'city': 'Pune'}) != User.work.fragment({'city': 'Pune'})
    assert User.a.b.fragment({'x': 1}) != User.a.c.fragment({'x': 1})


def test_h3_same_fragment_query_still_equal_and_cached_and_root_fragment_works():
    db, User = _db(), Query()
    assert User.home.fragment({'city': 'Pune'}) == Query().home.fragment({'city': 'Pune'})
    q = User.home.fragment({'city': 'Pune'})
    assert db.search(q) == db.search(q)
    assert hash(q) == hash(Query().home.fragment({'city': 'Pune'}))
    assert [d['name'] for d in db.search(Query().fragment({'name': 'raj'}))] == ['raj']
