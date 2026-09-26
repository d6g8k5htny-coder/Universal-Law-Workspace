#!/usr/bin/env bash
# Materialise every ref BRANCH_MAP.md names as a real local branch inside its submodule.
#
# The submodule gitlink pins ONE commit per package -- the public reviewed default tip.
# The other named refs are recorded in WORKSPACE.json with exact SHAs; this fetches them
# so they are branches you can check out and diff, rather than SHAs in a document.
#
# Copies nothing. Changes no default branch. Pushes nothing. Scientific effect: NONE.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - <<'PY' > /tmp/named_refs.tsv
import json, pathlib
m = json.loads(pathlib.Path('WORKSPACE.json').read_text())
for r in m['named_branches']:
    if r['kind'] != 'default':
        print(f"{r['repo']}\t{r['branch']}\t{r['sha']}")
PY
missing=0
while IFS=$'\t' read -r repo branch sha; do
  dir="repos/$repo"
  if [ ! -d "$dir/.git" ] && [ ! -f "$dir/.git" ]; then
    echo "SKIP  $repo  (submodule not initialised: run git submodule update --init --recursive)"
    missing=1; continue
  fi
  if git -C "$dir" cat-file -e "${sha}^{commit}" 2>/dev/null; then
    :
  else
    git -C "$dir" fetch -q --depth 50 origin "$branch" || { echo "FAIL  $repo  $branch"; missing=1; continue; }
  fi
  git -C "$dir" branch -f "$branch" "$sha" >/dev/null 2>&1 || git -C "$dir" branch -f "$branch" FETCH_HEAD >/dev/null 2>&1
  have=$(git -C "$dir" rev-parse "$branch" 2>/dev/null || echo "")
  if [ "$have" = "$sha" ]; then
    printf "OK    %-16s %-52s %s\n" "$repo" "$branch" "${sha:0:12}"
  else
    printf "DRIFT %-16s %-52s recorded %s, fetched %s\n" "$repo" "$branch" "${sha:0:12}" "${have:0:12}"
    missing=1
  fi
done < /tmp/named_refs.tsv
rm -f /tmp/named_refs.tsv
if [ "$missing" != "0" ]; then
  echo
  echo "One or more named refs could not be materialised at the recorded SHA."
  echo "A DRIFT line means the branch has moved since WORKSPACE.json was generated:"
  echo "that is information, not a failure to paper over. Regenerate the manifest."
  exit 1
fi
echo
echo "All named refs materialised at their recorded SHAs. Nothing was copied or pushed."
