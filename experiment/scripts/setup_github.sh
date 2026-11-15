#!/usr/bin/env bash
# One-time GitHub setup for A3. Every step acts on the account `gh` is logged in as.
# Usage: bash experiment/scripts/setup_github.sh   (from the submission repo root)
set -euo pipefail

OWNER="iDheer"
FORK="$OWNER/tinydb"
SUB="$OWNER/autose-a3"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
FORK_DIR="$ROOT/_fork"

echo "== 1. Submission repository $SUB (public, so TAs can open every link)"
if ! gh repo view "$SUB" >/dev/null 2>&1; then
  gh repo create "$SUB" --public --description "AutoSE A3: agentic SDLC workflow (issue in, PR out)"
fi
git -C "$ROOT" remote get-url origin >/dev/null 2>&1 || git -C "$ROOT" remote add origin "https://github.com/$SUB.git"
git -C "$ROOT" push -u origin main

echo "== 2. Fork msiemens/tinydb -> $FORK and push main pinned at edff96a + autose commits"
gh repo view "$FORK" >/dev/null 2>&1 || gh repo fork msiemens/tinydb --clone=false --default-branch-only
sleep 5
git -C "$FORK_DIR" push origin main
gh repo edit "$FORK" --default-branch main --enable-issues
gh api -X PUT "repos/$FORK/actions/permissions" -F enabled=true -f allowed_actions=all
# PR creation by the workflow needs this; reviews are posted as COMMENT, never as approvals.
gh api -X PUT "repos/$FORK/actions/permissions/workflow" -f default_workflow_permissions=read \
  -F can_approve_pull_request_reviews=true

echo "== 3. Protect main: no direct pushes for anyone; PR + 1 approval; admins may only bypass when merging a PR"
gh api -X POST "repos/$FORK/rulesets" --input - <<'JSON' || echo "(ruleset may already exist)"
{"name": "protect-main", "target": "branch", "enforcement": "active",
 "conditions": {"ref_name": {"include": ["refs/heads/main"], "exclude": []}},
 "rules": [{"type": "deletion"}, {"type": "non_fast_forward"},
           {"type": "pull_request", "parameters": {"required_approving_review_count": 1,
             "dismiss_stale_reviews_on_push": true, "require_code_owner_review": false,
             "require_last_push_approval": false, "required_review_thread_resolution": false}}],
 "bypass_actors": [{"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "pull_request"}]}
JSON

echo "== 4. Labels"
gh label create autose --repo "$FORK" --color 5319e7 --description "Run the autose workflow on this issue" --force
gh label create seeded-review --repo "$FORK" --color c5def5 --description "Reviewer calibration PR (experiment A)" --force

echo "== 5. Open the five issues (frontmatter stripped)"
for f in I1-bug-fragment-cache I2-bug-one-of-generator I3-feature-search-limit I4-feature-append-operation I5-vague-datetime; do
  src="$ROOT/experiment/issues/$f.md"
  title=$(sed -n 's/^title: "\(.*\)"$/\1/p' "$src")
  body=$(awk 'BEGIN{n=0} /^---$/{n++; next} n>=2' "$src")
  gh issue list --repo "$FORK" --state all --search "in:title \"$title\"" --json number -q '.[].number' | grep -q . \
    || gh issue create --repo "$FORK" --title "$title" --body "$body"
done
gh issue list --repo "$FORK" --state all --json number,title

echo "== 6. Seeded reviewer-check PRs (experiment A)"
declare -A BR=([S1]=seeded/S1-fragment-fix [S2]=seeded/S2-one-of-list-in-lambda [S3]=seeded/S3-limit-poisons-cache
               [S4]=seeded/S4-append-as-table-method [S5]=seeded/S5-limit-correct)
declare -A TI=([S1]="Fix fragment() queries sharing a cache entry across paths"
               [S2]="Make one_of() work with generators"
               [S3]="Add a limit argument to search()"
               [S4]="Add a built-in way to append to list fields"
               [S5]="Add a limit argument to search() (early stop, cache-safe)")
for s in S1 S2 S3 S4 S5; do
  b=${BR[$s]}
  git -C "$FORK_DIR" checkout -q -B "$b" main
  git -C "$FORK_DIR" apply "$ROOT/experiment/seeded_prs/$s.patch"
  git -C "$FORK_DIR" add -A
  git -C "$FORK_DIR" -c user.name="$OWNER" commit -q -m "${TI[$s]}"
  git -C "$FORK_DIR" push -q -f origin "$b"
  gh pr list --repo "$FORK" --head "$b" --json number -q '.[].number' | grep -q . || \
    gh pr create --repo "$FORK" --base main --head "$b" --title "${TI[$s]}" \
      --body-file "$ROOT/experiment/seeded_prs/$s.body.md" --label seeded-review
done
git -C "$FORK_DIR" checkout -q main
gh pr list --repo "$FORK" --json number,title,headRefName

echo
echo "Done. Remaining manual steps:"
echo "  - in a SEPARATE terminal (not in Claude Code): claude setup-token   (uses your Claude Pro plan)"
echo "  - gh secret set CLAUDE_CODE_OAUTH_TOKEN --repo $FORK   (paste the token when prompted)"
