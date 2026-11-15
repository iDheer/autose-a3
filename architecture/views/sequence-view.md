# Sequence view: one real run (issue #1, run 43717026729)

Issue [#1](https://github.com/iDheer/tinydb/issues/1) ("Searching with fragment() on a nested
field returns the results of a different field") went from trigger to `MERGE_READINESS_CHECK`
in **5 minutes 18 seconds** of wall-clock time on 2026-11-15 (all times UTC, from the job logs of
[run 43717026729](https://github.com/iDheer/tinydb/actions/runs/43717026729)). Result: PR
[#12](https://github.com/iDheer/tinydb/pull/12), approved by the reviewer and passing all 3 hidden
tests. The model cost was $0.31 for stages 1–5 and $0.23 for the review.

An earlier attempt on the same issue ([run 43716337981](https://github.com/iDheer/tinydb/actions/runs/43716337981))
stopped at stage 3 because the SDK sandbox could not start on the runner; see [ADR-011](../decisions/ADR-011.md).
This run is the first one after that fix. It was started by `workflow_dispatch` (`issue=1, mode=start`)
because the issue already carried the `autose` label.

```mermaid
sequenceDiagram
    autonumber
    actor M as Maintainer
    participant G as gate job
    participant O as orchestrator (build job)
    participant P as key proxy
    participant PL as Planner (Sonnet 5.5)
    participant J as Judge (Haiku 5.5)
    participant I as Implementer (Sonnet 5.5)
    participant T as Tester (Sonnet 5.5)
    participant CI as ci.yml
    participant R as Reviewer job (Opus 5.5, read-only token)
    participant PB as publish job
    participant S as autose-artifacts branch

    M->>G: 13:03:57 workflow_dispatch issue=1 mode=start
    G->>G: gate.py: run=true, mode=start, round=1
    G-->>O: 13:04:08 start build job (needs: gate)
    O->>O: 13:04:30 pop secrets from env, start key proxy, probe bwrap jail
    O->>O: 13:04:32 branch autose/issue-1 at base 13eca00
    Note over O,J: Stage 1 Requirements (A1 skill)
    O->>PL: spec attempt 1 (issue in untrusted block)
    PL-->>O: 13:05:12 spec.json (5 turns, $0.073)
    O->>J: is each AC testable?
    J-->>O: 13:05:16 FR-QRY-002.AC-1 not testable (Given relies on unstated data)
    O->>O: check_spec FAILED, retry 1 of 1, feedback = judge reason
    O->>PL: spec attempt 2 + feedback
    PL-->>O: 13:05:53 spec.json (6 turns, $0.077)
    O->>J: testable?
    J-->>O: 13:05:57 all ACs testable
    O->>O: check_spec PASSED → spec.md
    Note over O,PL: Stage 2 Design (A2 ARCHITECTURE.md)
    O->>PL: spec.md + ARCHITECTURE.md
    PL-->>O: 13:06:12 design.json (5 turns, $0.063)
    O->>O: check_design: Query.fragment exists (AST), every AC mapped → PASSED
    Note over O,I: Stage 3 Implementation
    O->>I: spec.md + design.md, writable = {tinydb/queries.py}
    I->>P: model calls with dummy key (proxy adds the real token)
    I->>I: Bash "pytest … | tail" DENIED by policy hook (pipe)
    I->>I: python -m pytest -q, python -m mypy tinydb (inside bwrap, no network)
    I-->>O: 13:06:21 status done (7 turns, $0.046)
    O->>O: check_impl: only declared files changed, compileall, import, mypy → PASSED (diff.patch)
    Note over O,T: Stage 4 Testing
    O->>T: spec ACs + design (not the implementer's reasoning)
    T->>T: writes tests/test_autose_issue_1.py, runs pytest in the jail
    T-->>O: 13:06:32 4 tests (6 turns, $0.046)
    O->>O: check_tests: 232 passed, every AC covered, 2 of 4 new tests fail on base → PASSED
    Note over O,CI: Stage 5 Release
    O->>O: secret scan of the diff → clean; push autose/issue-1; open PR #12 (pr.md)
    O->>CI: 13:06:41 workflow_dispatch ci.yml on autose/issue-1
    CI-->>O: 13:07:18 success (4 jobs)
    O->>S: 13:07:26 save run dir (spec, design, diff, test report, logs, run.json) + state.json
    O-->>R: start review job (needs: build, pr=12)
    Note over R: Stage 6 Review: issue + diff + repo at PR head only
    R->>R: 13:07:58 checkout refs/pull/12/head, gh issue view 1 → issue.json
    R->>R: reads diff, runs python -m pytest -q (232 passed), writes 5-test probe in scratch
    R-->>PB: 13:08:53 raw=approve → rules: no major findings, full suite run, evidence for every requirement → approve (11 turns, $0.232)
    PB->>M: 13:09:04 PR review (COMMENT type, never an approval) with findings: 1 minor, 1 nit
    PB->>S: review-round-1.md/json, state.json (status handover)
    PB->>M: 13:09:15 MERGE_READINESS_CHECK comment + label autose:ready-for-human
    Note over M: A person decides whether to merge. autose never merges.
```

## What the run shows

- **A check sent work back.** The testability judge rejected one acceptance criterion whose
  Given relied on data that only the issue mentioned. The deterministic `check_spec` turned that
  into a retry with the judge's reason as feedback, and the second spec passed.
- **The policy hook denied two commands.** The implementer and the tester each tried
  `pytest … | tail`. The hook rejected the pipe, and both agents reran the plain command, which
  then ran inside the bubblewrap jail.
- **The reviewer only saw its allowed inputs.** It checked out `refs/pull/12/head` with a
  read-only token. It ran the full suite itself and wrote its own probe tests. Its
  requirement table cites that evidence.
- **Tokens for stages 1–5:** 40 uncached input, 16,593 output, 254,338 cache-read and 56,702
  cache-write tokens.
