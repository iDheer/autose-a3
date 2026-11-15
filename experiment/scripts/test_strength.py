"""Experiment B measure: do an agent's own tests catch a known-defective implementation?

usage: python -I test_strength.py <tinydb_clone> [--json out.json]

For each issue with a defective seeded PR (I2->S2, I3->S3, I4->S4) and each variant branch
(baseline: autose/issue-N, selftest: autose/issue-N-selftest), take the agent's test file
tests/test_autose_issue_N.py from the fork branch, run it against
  base   = the pinned base commit (how many tests fail before any fix),
  seeded = base + the seeded defective patch (does at least one test catch the defect?),
  own    = the branch itself (sanity: should all pass),
and print one JSON row per (issue, variant).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORK = "https://github.com/iDheer/tinydb.git"
SEEDED = {2: "S2", 3: "S3", 4: "S4"}


def sh(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8")


def junit(path: Path) -> tuple[int, int]:
    if not path.exists():
        return 0, 0
    passed = failed = 0
    for tc in ET.parse(path).getroot().iter("testcase"):
        if any(ch.tag in ("failure", "error") for ch in tc):
            failed += 1
        elif not any(ch.tag == "skipped" for ch in tc):
            passed += 1
    return passed, failed


def run_tests(clone: Path, ref: str, test_src: str, n: int, patch: Path | None) -> dict:
    tmp = Path(tempfile.mkdtemp(prefix=f"strength-{n}-"))
    wt = tmp / "wt"
    try:
        sh(["git", "-c", "core.autocrlf=false", "worktree", "add", "--detach", str(wt), ref], clone)
        if patch is not None:
            p = sh(["git", "apply", "--whitespace=nowarn", str(patch)], wt)
            if p.returncode:
                return {"error": "patch did not apply: " + p.stderr[:200]}
        tf = wt / "tests" / f"test_autose_issue_{n}.py"
        tf.write_text(test_src, encoding="utf-8")
        x = tmp / "r.xml"
        r = sh([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-cov",
                f"--junitxml={x}", str(tf.relative_to(wt))], wt)
        passed, failed = junit(x)
        out = {"passed": passed, "failed": failed}
        if passed + failed == 0:
            out["error"] = (r.stdout + r.stderr)[-300:]
        return out
    finally:
        sh(["git", "worktree", "remove", "--force", str(wt)], clone)
        shutil.rmtree(tmp, ignore_errors=True)


SELFTEST_RUNS = {1: "43718866759", 2: "43718869610", 3: "43718872397", 4: "43718875030"}


def own_patch(n: int) -> Path:
    return ROOT / "_artifacts" / f"issue-{n}" / f"run-{SELFTEST_RUNS[n]}-1" / "diff.patch"


def main() -> int:
    clone = Path(sys.argv[1]).resolve()
    sh(["git", "fetch", "-q", FORK, "+refs/heads/autose/*:refs/remotes/fork/autose/*"], clone)
    base = sh(["git", "rev-parse", "edff96aeb2616402e9489d46e90a592c05565621"], clone).stdout.strip()
    rows = []
    for n in (1, 2, 3, 4):
        for variant, br in (("baseline", f"fork/autose/issue-{n}"), ("selftest", f"fork/autose/issue-{n}-selftest")):
            src = sh(["git", "show", f"{br}:tests/test_autose_issue_{n}.py"], clone)
            local = ROOT / "results" / "selftest_tests" / f"test_autose_issue_{n}.py"
            if src.returncode and variant == "selftest" and local.exists():
                # stop_after=test runs push no branch; the file is rebuilt by replay_test_file.py
                src = subprocess.CompletedProcess([], 0, local.read_text(encoding="utf-8"), "")
                br = "base"  # 'own' then means: the selftest diff.patch applied on base, see below
            if src.returncode:
                rows.append({"issue": f"I{n}", "variant": variant, "error": "no test file on " + br})
                continue
            row = {"issue": f"I{n}", "variant": variant, "branch": br,
                   "tests": src.stdout.count("\ndef test_") + src.stdout.startswith("def test_"),
                   "base": run_tests(clone, base, src.stdout, n, None),
                   "own": (run_tests(clone, base, src.stdout, n, own_patch(n)) if br == "base"
                           else run_tests(clone, br, src.stdout, n, None))}
            if n in SEEDED:
                s = run_tests(clone, base, src.stdout, n, ROOT / "experiment/seeded_prs" / f"{SEEDED[n]}.patch")
                row["seeded"] = SEEDED[n]
                row["vs_seeded"] = s
                row["catches_defect"] = s.get("failed", 0) > 0
            rows.append(row)
            print(json.dumps(row))
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
