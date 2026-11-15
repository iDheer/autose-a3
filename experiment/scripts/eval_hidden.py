"""Run the hidden acceptance tests for one issue against a patch applied to tinydb@edff96a.

usage: python -I eval_hidden.py <tinydb_clone> <issue_id I1..I5> <patch|-> [--json out.json]

`-` means no patch (the base commit). The hidden tests are copied into a temporary checkout
only for this run; they never enter the fork or any agent run.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = "edff96aeb2616402e9489d46e90a592c05565621"
HERE = Path(__file__).resolve().parent
HIDDEN = HERE.parent / "hidden_tests"


def sh(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def junit(path: Path) -> dict:
    res = {"passed": [], "failed": []}
    if not path.exists():
        return {"passed": [], "failed": ["<collection error>"]}
    for tc in ET.parse(path).getroot().iter("testcase"):
        bad = tc.find("failure") is not None or tc.find("error") is not None
        res["failed" if bad else "passed"].append(tc.get("name"))
    return res


def main() -> int:
    clone, iid, patch = Path(sys.argv[1]).resolve(), sys.argv[2], sys.argv[3]
    out_json = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
    tmp = Path(tempfile.mkdtemp(prefix=f"hidden-{iid}-"))
    wt = tmp / "wt"
    try:
        sh(["git", "-c", "core.autocrlf=false", "worktree", "add", "--detach", str(wt), BASE], clone)
        applied = True
        if patch != "-":
            p = sh(["git", "apply", "--whitespace=nowarn", str(Path(patch).resolve())], wt)
            applied = p.returncode == 0
            if not applied:
                print("PATCH DID NOT APPLY:", p.stderr)
        shutil.copy2(HIDDEN / f"test_hidden_{iid}.py", wt / "tests" / f"test_hidden_{iid}.py")
        hx, sx = tmp / "hidden.xml", tmp / "suite.xml"
        py = sys.executable
        sh([py, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-cov", f"--junitxml={hx}",
            f"tests/test_hidden_{iid}.py"], wt)
        (wt / "tests" / f"test_hidden_{iid}.py").unlink()
        sh([py, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--no-cov", f"--junitxml={sx}"], wt)
        h, s = junit(hx), junit(sx)
        result = {"issue": iid, "patch": patch, "applied": applied,
                  "hidden_passed": len(h["passed"]), "hidden_total": len(h["passed"]) + len(h["failed"]),
                  "hidden_failed_names": h["failed"], "suite_passed": len(s["passed"]),
                  "suite_failed": len(s["failed"]), "suite_failed_names": s["failed"][:20]}
        print(json.dumps(result))
        if out_json:
            Path(out_json).write_text(json.dumps(result, indent=2), encoding="utf-8")
        return 0
    finally:
        sh(["git", "worktree", "remove", "--force", str(wt)], clone)
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
