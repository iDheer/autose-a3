# Stage map

| # | Stage | Agent (model) | Artifact | Check before moving on | Who decides | On failure |
|---|---|---|---|---|---|---|
| 1 | Requirements | Planner, spec session (Sonnet 5.5) using the A1 `requirements-specifier` skill | `spec.md` | Every acceptance criterion of every MUST/SHOULD requirement is in Given/When/Then form with no `<TBD>` and no vague term; no open P1 question; verdict ≠ DRAFT; **and** the Haiku 5.5 judge rates every criterion testable | orchestrator | Stop. Post the open questions on the issue, label `autose:needs-info`. A maintainer answers and comments `/autose`. |
| 2 | Design | Planner, design session (Sonnet 5.5) using `ARCHITECTURE.md` | `design.md` | Files to modify exist; named functions/classes/methods exist (AST); files to create do not; every acceptance criterion mapped to a file and a test idea | orchestrator | One retry with the check output; then stop. |
| 3 | Implementation | Implementer (Sonnet 5.5) | `diff.patch` | Diff non-empty; only design files changed; `compileall`, `import tinydb` and `mypy tinydb` succeed | orchestrator | Retry (counts as an attempt). `design_gap` → stage 2 (once). |
| 4 | Testing | Tester (Sonnet 5.5) | `test_report.md` | Full suite passes; every acceptance criterion has a test named after it; ≥1 new test fails on the base commit | orchestrator | Failures → stage 3 (≤ 3 attempts per design); attempts used up → stage 2 (once); `test_dispute` → tester once; then stop. |
| 5 | Release | none (release step in `orchestrator.py`) | `pr.md` + PR link | PR state OPEN; CI run for the head SHA concluded `success` | orchestrator | CI failure → stage 3 once with the CI log, then stop. |
| 6 | Review | Reviewer (Opus 5.5), separate job | `review.md` | Reviewer verdict `approve` that survives the verdict rules, **or** two send-backs used up | `publish.py` (rules) → human | `approach` finding → stage 2, `code` finding → stage 3, via a new workflow run (`mode=rework`), at most twice. |

After stage 6 the workflow posts a `MERGE_READINESS_CHECK` comment and labels the PR
`autose:ready-for-human`. It never merges.
