# Decision experiments: what each variant changes

Two ADRs are tested. Every variant is selected with a `workflow_dispatch` input of
`autose.yml`, so baseline and variant run the same code, the same models and the same
budgets. Only the named difference changes.

## Experiment A: reviewer independence (ADR-008, ADR-003)

**Question.** Does keeping the reviewer ignorant of the implementation side (no spec, no
design, no PR description) make it catch more defects, at the price of more false alarms?

| | `baseline` (isolated) | `informed` |
|---|---|---|
| Reviewer sees | issue, diff, repo at PR head | the same **plus** the PR description (the implementer's own summary of the change), and `spec.md` / `design.md` when they exist |
| Everything else | Opus 5.5, same prompt, same tools, same verdict rules | identical |

**Subjects.** The five seeded PRs in `seeded_prs/` (2 correct, 3 with a known defect: a
subtle code bug, a cache-poisoning bug, a wrong approach). Each PR description is written
the way an over-confident implementer would write it: it claims the change is complete and
tested, and for S3 it says caching is unchanged, which is exactly the defect.

**Runs.** 5 PRs × 2 variants × 1 trial = 10 reviews
(`gh workflow run autose.yml -f mode=review -f experiment=A -f issue=<I> -f pr=<PR> -f variant=<v>`).

**Measures** (ground truth in `seeded_prs/labels.csv`): verdict correct (approve for S1/S5,
request changes for S2–S4); defect named (a finding that identifies the actual defect);
route correct (S4 → design, S2/S3 → implement); false alarms (blocker/major findings on S1/S5);
cost and turns.

## Experiment B: separate tester vs. implementer writes its own tests (ADR-001)

**Question.** Does splitting testing into a separate agent that never sees the implementer's
reasoning produce tests that catch more problems, and is it worth the extra session?

| | `baseline` (separate tester) | `selftest` |
|---|---|---|
| Stage 4 tests written by | Tester agent: acceptance criteria + design, no implementer context | the Implementer, in the same session as the code |
| Implementer may write | design files | design files **and** `tests/test_autose_issue_N.py` |
| Stage-4 check | identical (suite passes, AC coverage, ≥1 new test fails on base) | identical |
| Branch | `autose/issue-N` | `autose/issue-N-selftest` |

**Subjects.** The four well-specified issues I1–I4 (the vague I5 is excluded because stage 1
stops it by design). Variant runs use `stop_after=test`, so they produce `diff.patch` and
`test_report.md` but no PR and no review (cost control). The baseline numbers come from the
main runs.

**Measures.** Hidden acceptance tests passed by the stage-4 diff; number of stage-3/4
iterations; how many of the agent's own tests fail on the base commit; **test strength**:
do the agent's tests catch the known-defective seeded implementation of the same issue
(S2 for I2, S3 for I3, S4 for I4), i.e. does at least one agent test fail when run against
that implementation instead of the agent's own? Cost and tokens per run.

Negative or null results are reported as such.
