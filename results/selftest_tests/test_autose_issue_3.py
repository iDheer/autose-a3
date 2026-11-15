from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def make_table(key='n'):
    table = TinyDB(storage=MemoryStorage).table('t')
    for i in range(1, 6):
        table.insert({'n': i})
    return table


def ids(docs):
    return [d.doc_id for d in docs]


def test_fr_srch_001_ac_1_limit_length():
    t = make_table()
    assert len(t.search(Query().n >= 1, limit=2)) == 2


def test_fr_srch_001_ac_2_limit_with_cached_query():
    t = make_table()
    cond = Query().n >= 1
    t.search(cond)
    assert t.search(cond, limit=2) == [{'n': 1}, {'n': 2}]


def test_fr_srch_001_ac_3_limit_one():
    t = make_table()
    res = t.search(Query().n >= 1, limit=1)
    assert len(res) == 1
    assert res[0].doc_id == 1 and res[0] == {'n': 1}


def test_fr_srch_002_ac_1_order():
    t = make_table()
    res = t.search(Query().n >= 1, limit=3)
    assert ids(res) == [1, 2, 3]
    assert res == [{'n': 1}, {'n': 2}, {'n': 3}]


def test_fr_srch_002_ac_2_prefix_of_unlimited():
    cond = Query().n >= 1
    a = make_table().search(cond, limit=3)
    b = make_table().search(cond)[:3]
    assert a == b and ids(a) == ids(b)


def test_fr_srch_003_ac_1_unlimited():
    res = make_table().search(Query().n >= 3)
    assert ids(res) == [3, 4, 5]
    assert res == [{'n': 3}, {'n': 4}, {'n': 5}]


def test_fr_srch_003_ac_2_fresh_list():
    t = make_table()
    cond = Query().n >= 1
    r1 = t.search(cond)
    r2 = t.search(cond)
    assert ids(r1) == ids(r2) == [1, 2, 3, 4, 5]
    assert r1 is not r2


def test_fr_srch_004_ac_1_limited_does_not_poison_cache():
    t = make_table()
    cond = Query().n >= 1
    t.search(cond, limit=2)
    assert ids(t.search(cond)) == [1, 2, 3, 4, 5]


def test_fr_srch_005_ac_1_limit_larger_than_matches():
    res = make_table().search(Query().n <= 3, limit=10)
    assert ids(res) == [1, 2, 3]
    assert res == [{'n': 1}, {'n': 2}, {'n': 3}]


def test_fr_srch_005_ac_2_limit_equal_matches():
    assert ids(make_table().search(Query().n <= 3, limit=3)) == [1, 2, 3]


def make_db():
    db = TinyDB(storage=MemoryStorage)
    for i in range(1, 6):
        db.insert({'level': 'error', 'n': i})
    return db


def test_fr_srch_006_ac_1_db_limit():
    res = make_db().search(Query().level == 'error', limit=2)
    assert res == [{'level': 'error', 'n': 1}, {'level': 'error', 'n': 2}]


def test_fr_srch_006_ac_2_db_unlimited():
    res = make_db().search(Query().level == 'error')
    assert [d['n'] for d in res] == [1, 2, 3, 4, 5]
