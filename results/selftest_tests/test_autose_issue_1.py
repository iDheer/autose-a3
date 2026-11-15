from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

ANA = {'name': 'ana', 'home': {'city': 'Pune'}, 'work': {'city': 'Delhi'}}
RAJ = {'name': 'raj', 'home': {'city': 'Delhi'}, 'work': {'city': 'Pune'}}


def _db():
    db = TinyDB(storage=MemoryStorage)
    db.insert(ANA)
    db.insert(RAJ)
    return db


def test_fr_qry_001_ac_1_other_field_after_cached_search():
    db = _db()
    User = Query()
    db.search(User.home.fragment({'city': 'Pune'}))
    assert db.search(User.work.fragment({'city': 'Pune'})) == [RAJ]


def test_fr_qry_001_ac_2_fresh_search():
    db = _db()
    assert db.search(Query().home.fragment({'city': 'Pune'})) == [ANA]


def test_fr_qry_001_ac_3_reverse_order():
    db = _db()
    User = Query()
    db.search(User.work.fragment({'city': 'Pune'}))
    assert db.search(User.home.fragment({'city': 'Pune'})) == [ANA]


def test_fr_qry_001_ac_4_repeated_search():
    db = _db()
    assert db.search(Query().home.fragment({'city': 'Pune'})) == [ANA]
    assert db.search(Query().home.fragment({'city': 'Pune'})) == [ANA]


def test_fr_qry_002_equality_depends_on_path():
    User = Query()
    a = User.home.fragment({'city': 'Pune'})
    assert a != User.work.fragment({'city': 'Pune'})
    b = Query().home.fragment({'city': 'Pune'})
    assert a == b and hash(a) == hash(b)
