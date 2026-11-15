# AutoSE Assignment 3: an agentic SDLC workflow (issue in, pull request out)

**Roll no.:** 2023111010

| | |
|---|---|
| Fork | https://github.com/iDheer/tinydb |
| Upstream and pinned commit | `msiemens/tinydb` @ `edff96aeb2616402e9489d46e90a592c05565621` (`edff96a`), the same commit as A2. The fork's `main` = `edff96a` + the autose commits (workflow, agent code, A1 skill, A2 `ARCHITECTURE.md`, smaller CI). |
| Workflow | [`.github/workflows/autose.yml`](https://github.com/iDheer/tinydb/blob/main/.github/workflows/autose.yml), copy in [`workflow/`](workflow/) |
| Agent framework | Claude Agent SDK for Python, `claude-agent-sdk==0.2.182` |
| Models | Planner, Implementer, Tester: `claude-sonnet-5-5` · Reviewer: `claude-opus-5-5` · Testability judge: `claude-haiku-5-5` ([ADR-006](architecture/decisions/ADR-006.md)) |
| Artifacts of every run | branch [`autose-artifacts`](https://github.com/iDheer/tinydb/tree/autose-artifacts) of the fork, plus the Actions run's uploaded artifacts |
| All runs, PRs, reviews | [`results/runs.md`](results/runs.md) |
| Report | [`report.pdf`](report.pdf) |
| Demo video | see `demo.mp4` / link below |

## How to trigger the workflow

A maintainer (OWNER, MEMBER or COLLABORATOR) does one of:

- add the label **`autose`** to an issue → stages 1–6 run;
- comment **`/autose`** on an issue → (re)start from stage 1; maintainer comments on the
  issue are passed to the spec stage as answers (this is how the vague issue continues
  after the workflow asked its questions);
- comment **`/autose review`** on an autose PR → one more independent review round.

Everyone else's issues and comments are ignored by the `gate` job. Rework rounds and the
decision experiments use `workflow_dispatch` (`mode=rework|review`, `variant=…`).

The workflow never merges. It ends with a `MERGE_READINESS_CHECK` comment and the label
`autose:ready-for-human` on the PR.

## Repository layout

```
README.md                 this file
report.pdf                the report (source in report_src/)
architecture/
  views/                  component view, sequence view (one real run), stage map
  decisions/              ADR-001 … ADR-010 (Nygard format, superseded ones kept)
workflow/                 copy of the fork's .github/workflows/ and .autose/ (agent code, prompts,
                          A1 skill, config, unit tests) and ARCHITECTURE.md
experiment/
  issues/                 the 5 issue texts (+ the maintainer's answer to the vague one)
  hidden_tests/           2–4 hidden acceptance tests per issue (never in the fork)
  reference/              my reference fixes, used only to validate the hidden tests
  seeded_prs/             5 reviewer-check PRs: diffs, PR descriptions, ground-truth labels.csv
  variants.md             what each decision-experiment variant changes
  scripts/                setup_github.sh, eval_hidden.py, collect_results.py, sync_workflow.sh
results/
  results.csv             one row per run
  runs.md                 links to every Actions run, PR and review
```

## Reproducing

1. `bash experiment/scripts/setup_github.sh` creates both repositories, the fork's `main`,
   the ruleset that protects `main`, labels, the five issues and the five seeded PRs.
2. Set a spending limit in the Anthropic Console, then `gh secret set ANTHROPIC_API_KEY --repo iDheer/tinydb`.
3. Label an issue `autose`.
4. `python -I experiment/scripts/eval_hidden.py <tinydb clone> I1 <diff.patch>` runs the
   hidden tests against a run's `diff.patch` (downloaded from `autose-artifacts`).

Unit tests of the deterministic parts (policy, gate, key proxy, checks, verdict rules):
`python -m pytest -q -c /dev/null .autose/tests` in the fork.

## AI use

This repository was built with substantial help from Claude Code (Claude Opus 5.5), in line
with the course policy: it wrote the workflow and agent code, the unit tests, the issue texts,
hidden tests, seeded PRs, and first drafts of the ADRs, views and report from my
instructions. The A1 skill and A2 `ARCHITECTURE.md` are my earlier work, reused unchanged.

> **TODO (author, before submitting):** the course requires that the ADRs and their
> reasoning are your own and that you review everything AI-generated. Rework the ADRs in
> `architecture/decisions/` in your own words, then replace this note with a statement of
> what you reviewed and changed.
