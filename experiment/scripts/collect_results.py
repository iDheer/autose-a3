"""Collect every real run from the fork's `autose-artifacts` branch into results/.

usage: python -I collect_results.py <tinydb_clone_with_fork_remote> [--no-hidden]

Reads issue-N/state.json + run.json + review-round-*.json (main runs and experiment B) and
experiments/A/*/verdict.json (seeded-PR reviews), runs the hidden tests on every diff.patch
with eval_hidden.py, and writes results/results.csv, results/experiment_A.csv and
results/summary.json. Nothing is invented: a field the artifacts do not contain stays empty.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results"
FORK = "https://github.com/iDheer/tinydb.git"
ISSUE_ID = {1: "I1", 2: "I2", 3: "I3", 4: "I4", 5: "I5"}
KIND = {"I1": "bug", "I2": "bug", "I3": "feature", "I4": "feature", "I5": "vague"}
COLS = ["run_id", "issue", "kind", "variant", "round", "status", "stage_reached", "impl_attempts",
        "design_revisions", "tester_runs", "pr", "ci", "review_verdict", "review_route", "hidden_passed",
        "hidden_total", "suite_failed", "cost_usd", "input_tokens", "output_tokens", "cache_read_tokens",
        "run_url"]
STAGES = ["spec", "design", "implement", "test", "release", "review"]


def sh(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8")


def fetch_artifacts(dest: Path) -> Path:
    if not (dest / ".git").exists():
        sh(["git", "-c", "core.autocrlf=false", "clone", "-q", "--single-branch", "--branch", "autose-artifacts", FORK, str(dest)])
    else:
        sh(["git", "fetch", "-q", "origin", "autose-artifacts"], dest)
        sh(["git", "reset", "-q", "--hard", "origin/autose-artifacts"], dest)
    return dest


def load(p: Path, default=None):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def hidden(clone: Path, iid: str, patch: Path) -> dict:
    out = RESULTS / "hidden" / f"{patch.parent.name}-{iid}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists():
        sh([sys.executable, "-I", str(ROOT / "experiment/scripts/eval_hidden.py"), str(clone), iid,
            str(patch), "--json", str(out)])
    return load(out, {}) or {}


def main() -> int:
    clone = Path(sys.argv[1]).resolve()
    do_hidden = "--no-hidden" not in sys.argv
    art = fetch_artifacts(Path(sys.argv[2]).resolve() if len(sys.argv) > 2 and not sys.argv[2].startswith("--")
                          else ROOT / "_artifacts")
    rows, tot = [], {"cost_usd": 0.0, "input_tokens": 0, "output_tokens": 0, "cache_read_tokens": 0,
                     "cache_creation_tokens": 0, "runs": 0, "reviews": 0}
    for sp in sorted(art.glob("issue-*/state.json"), key=lambda p: int(p.parent.name.split("-")[1])):
        state = load(sp, {})
        n = int(sp.parent.name.split("-")[1])
        iid = ISSUE_ID.get(n, f"#{n}")
        reviews = {r["round"]: r for r in state.get("reviews", [])}
        for r in state.get("runs", []):
            d = art / r["dir"]
            rj = load(d / "run.json", {}) or {}
            c, tok = rj.get("counters", {}), rj.get("tokens", {}) or r.get("tokens", {})
            passed = r.get("passed_stages", [])
            reached = STAGES[min(len(STAGES) - 1, max([STAGES.index(s) for s in passed] + [-1]) + 1)]
            rv = load(d / f"review-round-{r['round']}.json")
            row = {"run_id": f"{r['run_id']}-{r['attempt']}", "issue": iid, "kind": KIND.get(iid, ""),
                   "variant": r.get("variant", "baseline"), "round": r["round"], "status": r["status"],
                   "stage_reached": "review" if rv else reached,
                   "impl_attempts": c.get("impl_attempts", ""), "design_revisions": c.get("design_revisions", ""),
                   "tester_runs": sum(1 for s in rj.get("stages", []) if s["stage"] == "test"),
                   "pr": (rj.get("pr") or {}).get("number", ""), "ci": ((rj.get("pr") or {}).get("ci") or {}).get("conclusion", ""),
                   "review_verdict": (rv or {}).get("verdict", ""), "review_route": (rv or {}).get("route", ""),
                   "cost_usd": rj.get("cost_usd", r.get("cost_usd", "")),
                   "input_tokens": tok.get("input_tokens", 0), "output_tokens": tok.get("output_tokens", 0),
                   "cache_read_tokens": tok.get("cache_read_input_tokens", 0), "run_url": r.get("run_url", "")}
            if do_hidden and (d / "diff.patch").exists() and iid in KIND:
                h = hidden(clone, iid, d / "diff.patch")
                row |= {"hidden_passed": h.get("hidden_passed", ""), "hidden_total": h.get("hidden_total", ""),
                        "suite_failed": h.get("suite_failed", "")}
            rows.append(row)
            tot["runs"] += 1
            tot["cost_usd"] += float(row["cost_usd"] or 0)
            for k, src in (("input_tokens", "input_tokens"), ("output_tokens", "output_tokens"),
                           ("cache_read_tokens", "cache_read_input_tokens"),
                           ("cache_creation_tokens", "cache_creation_input_tokens")):
                tot[k] += int(tok.get(src, 0) or 0)
            if rv:
                m = rv.get("meta", {})
                tot["reviews"] += 1
                tot["cost_usd"] += float(m.get("cost_usd") or 0)
                u = m.get("usage") or {}
                for k, src in (("input_tokens", "input_tokens"), ("output_tokens", "output_tokens"),
                               ("cache_read_tokens", "cache_read_input_tokens"),
                               ("cache_creation_tokens", "cache_creation_input_tokens")):
                    tot[k] += int(u.get(src, 0) or 0)
        del reviews

    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / "results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, COLS)
        w.writeheader()
        w.writerows({k: row.get(k, "") for k in COLS} for row in rows)

    labels = {r["issue"] + ":" + r["seeded_pr"]: r for r in csv.DictReader(
        open(ROOT / "experiment/seeded_prs/labels.csv", encoding="utf-8"))}
    pr_of = {}  # seeded PR number -> label row, by branch
    for lab in labels.values():
        p = sh(["gh", "pr", "list", "--repo", "iDheer/tinydb", "--state", "all", "--head", lab["branch"],
                "--json", "number", "-q", ".[0].number"])
        if p.stdout.strip():
            pr_of[int(p.stdout.strip())] = lab
    arows = []
    for vp in sorted(art.glob("experiments/A/*/verdict.json")):
        v = load(vp, {})
        lab = pr_of.get(int(v.get("pr", 0)), {})
        m = v.get("meta", {})
        u = m.get("usage") or {}
        blocking = [f for f in v.get("findings", []) if f.get("severity") in ("blocker", "major")]
        arows.append({"seeded_pr": lab.get("seeded_pr", ""), "pr": v.get("pr"), "variant": v.get("variant"),
                      "expected_verdict": lab.get("expected_verdict", ""), "verdict": v.get("verdict"),
                      "raw_verdict": v.get("raw_verdict"), "verdict_correct": v.get("verdict") == lab.get("expected_verdict"),
                      "expected_route": lab.get("expected_route", ""), "route": v.get("route"),
                      "blocking_findings": len(blocking), "findings": len(v.get("findings", [])),
                      "defect_named": "", "overrides": "; ".join(v.get("overrides", [])),
                      "turns": m.get("num_turns"), "cost_usd": m.get("cost_usd"),
                      "input_tokens": u.get("input_tokens", 0), "output_tokens": u.get("output_tokens", 0),
                      "dir": vp.parent.name})
        tot["reviews"] += 1
        tot["cost_usd"] += float(m.get("cost_usd") or 0)
        for k, src in (("input_tokens", "input_tokens"), ("output_tokens", "output_tokens"),
                       ("cache_read_tokens", "cache_read_input_tokens"),
                       ("cache_creation_tokens", "cache_creation_input_tokens")):
            tot[k] += int(u.get(src, 0) or 0)
    if arows:
        with open(RESULTS / "experiment_A.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, list(arows[0]))
            w.writeheader()
            w.writerows(arows)
    tot["cost_usd"] = round(tot["cost_usd"], 4)
    (RESULTS / "summary.json").write_text(json.dumps(tot, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(tot, indent=2))
    print(f"{len(rows)} run rows, {len(arows)} experiment-A reviews")
    return 0


if __name__ == "__main__":
    sys.exit(main())
