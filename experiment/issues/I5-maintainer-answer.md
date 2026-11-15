Thanks for the questions, here are the decisions (maintainer):

1. Scope: only persistence in `JSONStorage`. `datetime.datetime` and `datetime.date` values inside documents must be written to the JSON file and come back as the same type and the same value when the database is reopened, so that normal comparisons in queries (e.g. `Query().when < datetime(2026, 1, 1)`) work after reopening.
2. Timezone-aware datetimes keep their UTC offset; naive datetimes stay naive.
3. Strings that merely look like dates (e.g. `"2026-01-01"`) must stay strings.
4. No new third-party dependencies; `MemoryStorage` needs no change.
5. No new query operators and no change to `Query`.
