"""Rebuild an agent-written test file from its transcript(s) by replaying Write/Edit calls.

Needed because the stage-4 diff.patch of runs before the fix in PR #18 omitted untracked new
files (git diff <base> does not show them). Every Write/Edit input is logged in full in
logs/*.transcript.json, so the file can be reconstructed exactly.

usage: python -I replay_test_file.py <run_dir> <issue_number> <out_file>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    run_dir, n, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    target = f"tests/test_autose_issue_{n}.py"
    text: str | None = None
    # Replay in the order the orchestrator ran the agents: label order sorts attempts correctly.
    order = {"implementer": 0, "tester": 1}
    files = sorted((run_dir / "logs").glob("*.transcript.json"),
                   key=lambda p: (order.get(p.name.split(".")[0], 2), p.name))
    for f in files:
        for ev in json.loads(f.read_text(encoding="utf-8")):
            if ev.get("type") != "tool_use" or ev.get("name") not in ("Write", "Edit"):
                continue
            inp = ev["input"]
            if not str(inp.get("file_path", "")).replace("\\", "/").endswith(target):
                continue
            if ev["name"] == "Write":
                text = inp["content"]
            elif text is not None:
                old, new = inp["old_string"], inp["new_string"]
                if old not in text:
                    print(f"WARNING: edit in {f.name} does not apply", file=sys.stderr)
                    continue
                text = text.replace(old, new) if inp.get("replace_all") else text.replace(old, new, 1)
    if text is None:
        print("no Write of the test file found", file=sys.stderr)
        return 1
    out.write_text(text, encoding="utf-8", newline="")
    print(f"{out}: {text.count(chr(10) + 'def test_')} top-level tests")
    return 0


if __name__ == "__main__":
    sys.exit(main())
