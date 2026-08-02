#!/usr/bin/env bash
# Append the harness .gitignore rules to a project, without ever overwriting.
#
#   merge-gitignore.sh <project-root> [--check]
#
# WHY A SCRIPT: `.harness/features/*/runs/**` is not cosmetic. Run dirs are ephemeral
# scratch, and the git-failure-mode rule halts a team with BLOCKED on a dirty tree —
# so if this rule is missing, the harness's own artifacts deadlock the next run. The
# project's existing .gitignore must survive intact, and re-running must be a no-op.
#
# Exit 0 = rules present (or appended). Exit 1 = --check found them missing.
set -uo pipefail

root="${1:-}"
mode="${2:-}"
if [ -z "$root" ] || [ ! -d "$root" ]; then
  echo "usage: merge-gitignore.sh <project-root> [--check]" >&2
  exit 1
fi
root="$(cd "$root" && pwd)"

# Locate the snippet relative to this script, not to cwd — a caller's working
# directory is not guaranteed, and resolving from pwd is how check-domain.sh
# previously failed open.
_selfdir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
snippet="$_selfdir/../templates/gitignore.snippet"
if [ ! -r "$snippet" ]; then
  echo "merge-gitignore: no snippet at $snippet" >&2
  exit 1
fi

target="$root/.gitignore"

# The rules, ignoring the snippet's comment and marker lines.
rules="$(grep -v -e '^[[:space:]]*#' -e '^[[:space:]]*$' "$snippet")"

missing=""
while IFS= read -r rule; do
  [ -n "$rule" ] || continue
  # Fixed-string, whole-line match: `.claude/worktrees/` must not be considered
  # present because some other line merely contains it as a substring.
  if [ -f "$target" ] && grep -qxF -- "$rule" "$target"; then
    continue
  fi
  missing+="$rule"$'\n'
done <<< "$rules"

if [ -z "$missing" ]; then
  echo "merge-gitignore: all harness rules already present in $target"
  exit 0
fi

if [ "$mode" = "--check" ]; then
  echo "merge-gitignore: MISSING from $target:" >&2
  # Quoted AND iterated. Unquoted, `$missing` glob-expanded (the snippet holds
  # *.pyc) and printed cwd filenames instead of the rules. Fully quoted, one
  # printf swallowed every line and only the first got the "  - " prefix.
  # (review of PR #4, and of the first fix for it)
  printf '%s\n' "$missing" | while IFS= read -r _rule; do
    [ -n "$_rule" ] && printf '  - %s\n' "$_rule"
  done >&2
  exit 1
fi

# Append only the rules that are absent, under the marker block. Partial presence is
# normal — a project may already ignore .DS_Store — and re-adding it would be noise.
{
  [ -f "$target" ] && [ -s "$target" ] && echo ""
  echo "# --- harness ---"
  echo "# Run dirs are ephemeral; a dirty tree halts a team with BLOCKED, so these"
  echo "# must be ignored or the harness deadlocks itself. Everything else under"
  echo "# .harness/ is committed on purpose — it is the record of what shipped."
  printf '%s' "$missing"
  echo "# --- end harness ---"
} >> "$target"

echo "merge-gitignore: appended to $target"
printf '  + %s\n' $missing
