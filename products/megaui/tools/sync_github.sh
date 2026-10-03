#!/usr/bin/env bash
# sync_github.sh — push all MegaUI work to the session branch.
# Handles the recurring HEAD-resets in the main checkout by always
# committing from a detached worktree based on origin.
#
# Usage:  bash tools/sync_github.sh ["commit message"]
# Never touches any branch other than the session branch.

set -u
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
BR="arena/01a0f080-bountycore-assassin-and-work-d"
MSG="${1:-megaui sync $(date +%F_%T)}"
WT="/tmp/syncwt-$$"

cd "$ROOT" || exit 1
git fetch origin -q || { echo "FETCH FAILED"; exit 1; }

git worktree remove "$WT" --force 2>/dev/null
git worktree add --detach "$WT" "origin/$BR" -q 2>/dev/null || \
  git worktree add --detach "$WT" "origin/$BR" || exit 1

# copy sources (respecting size: skip generated dist/kit + build)
tar cf - --exclude='./dist' --exclude='./build' --exclude='./.git' \
    -C products/megaui . | tar xf - -C "$WT/products/megaui/" 2>/dev/null
mkdir -p "$WT/products/megaui/dist"
for f in products/megaui/dist/*.zip products/megaui/dist/*.unitypackage; do
  [ -e "$f" ] || continue
  b="$(basename "$f")"
  if ! cmp -s "$f" "$WT/products/megaui/dist/$b" 2>/dev/null; then
    cp "$f" "$WT/products/megaui/dist/$b"
  fi
done
# top-level product PLAN if present
[ -f products/PLAN.md ] && cp products/PLAN.md "$WT/products/PLAN.md" 2>/dev/null

cd "$WT" || exit 1
git add -A products/megaui products/PLAN.md 2>/dev/null
git add -A products/megaui 2>/dev/null
if git diff --cached --quiet; then
  echo "NOTHING TO SYNC"
else
  git -c user.name="MegaUI Sync" -c user.email="sync@arena.local" \
      commit -q -m "$MSG" || { echo "COMMIT FAILED"; exit 1; }
  if git push origin "HEAD:$BR" 2>&1; then
    echo "SYNCED: $(git rev-parse --short HEAD)"
  else
    echo "PUSH FAILED (will retry next run)"
    exit 1
  fi
fi
git worktree remove "$WT" --force 2>/dev/null
exit 0
