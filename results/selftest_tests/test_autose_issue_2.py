from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def _db(*tags):
    db = TinyDB(storage=MemoryStorage)
    db.insert_multiple([{'tag': t} for t in tags])
    return db


def test_fr_query_001_ac_1_generator_search():
    db = _db('a', 'b', 'a', 'c')
    allowed = (t for t in ['a', 'b'])
    assert db.search(Query().tag.one_of(allowed)) == [
        {'tag': 'a'}, {'tag': 'b'}, {'tag': 'a'}]


def test_fr_query_001_ac_2_generator_direct_calls():
    q = Query().tag.one_of(t for t in ['a', 'b'])
    results = [q({'tag': t}) for t in ['a', 'b', 'a', 'c']]
    assert results == [True, True, True, False]


def test_fr_query_001_ac_3_generator_count():
    db = _db('a', 'a', 'b')
    assert db.count(Query().tag.one_of(t for t in ['a', 'b'])) == 3


def test_fr_query_002_ac_1_list_search():
    db = _db('a', 'b', 'a', 'c')
    assert db.search(Query().tag.one_of(['a', 'b'])) == [
        {'tag': 'a'}, {'tag': 'b'}, {'tag': 'a'}]


def test_fr_query_002_ac_2_list_direct_calls():
    q = Query().key1.one_of(['value 1', 'value 2'])
    assert q({'key1': 'value 1'}) is True
    assert q({'key1': 'value 3'}) is False


def test_fr_query_002_ac_3_list_reused():
    db = _db('a', 'c')
    q = Query().tag.one_of(['a', 'b'])
    assert db.search(q) == [{'tag': 'a'}]
    assert db.search(q) == [{'tag': 'a'}]
