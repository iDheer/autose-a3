"""Hidden acceptance tests for I5 (datetime/date round-trip in JSONStorage), as decided in
the maintainer's answer (experiment/issues/I5-maintainer-answer.md)."""
from datetime import date, datetime, timedelta, timezone

from tinydb import TinyDB, Query


def test_h1_naive_datetime_round_trips_and_is_queryable_after_reopen(tmp_path):
    path = tmp_path / 'db.json'
    when = datetime(2025, 12, 24, 18, 30, 5)
    with TinyDB(path) as db:
        db.insert({'event': 'x', 'when': when})
    with TinyDB(path) as db:
        got = db.all()[0]['when']
        assert isinstance(got, datetime) and got == when and got.tzinfo is None
        assert len(db.search(Query().when < datetime(2026, 1, 1))) == 1


def test_h2_date_stays_a_date(tmp_path):
    path = tmp_path / 'db.json'
    with TinyDB(path) as db:
        db.insert({'day': date(2026, 3, 1)})
    with TinyDB(path) as db:
        got = db.all()[0]['day']
        assert type(got) is date and got == date(2026, 3, 1)


def test_h3_timezone_aware_datetime_keeps_offset(tmp_path):
    path = tmp_path / 'db.json'
    ist = timezone(timedelta(hours=5, minutes=30))
    when = datetime(2026, 1, 2, 9, 0, tzinfo=ist)
    with TinyDB(path) as db:
        db.insert({'when': when})
    with TinyDB(path) as db:
        got = db.all()[0]['when']
        assert got == when and got.utcoffset() == timedelta(hours=5, minutes=30)


def test_h4_date_like_strings_stay_strings(tmp_path):
    path = tmp_path / 'db.json'
    with TinyDB(path) as db:
        db.insert({'s': '2026-01-01', 't': '2026-01-01T10:00:00'})
    with TinyDB(path) as db:
        doc = db.all()[0]
        assert doc['s'] == '2026-01-01' and isinstance(doc['s'], str)
        assert doc['t'] == '2026-01-01T10:00:00' and isinstance(doc['t'], str)
