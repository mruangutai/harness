#!/usr/bin/env bash
# Distribute the harness: skills, agents and templates -> global + enrolled projects.
#
#   deploy.sh                      dry run of a global + all-projects push  (DEFAULT)
#   deploy.sh --apply              perform it
#   deploy.sh --project <path>     dry run of enrolling one project
#   deploy.sh --project <path> --apply
#
# DRY RUN IS THE DEFAULT BECAUSE THIS DELETES THINGS. Copy-only deploy is how the
# three agents this design removed stayed spawnable everywhere for months, pointing
# at a `.planning/` root that no longer exists. Reconciling means deleting, deleting
# is not reversible by re-running, so the plan is shown before anything moves.
#
# IT NEVER WRITES PROJECT STATE. Not `.harness/`, not `.planning/`, not settings.json.
# That is `/harness-init`'s job, and the split is the whole reason deploy can be dumb
# enough to run unattended. Deploy owns the TOOL tree; init owns the PROJECT tree.
#
# AGENTS GO GLOBAL ONLY (DEC-113). One copy in ~/.claude/agents/ is visible from every
# project, so per-project copies buy nothing and cost drift: a project holding a stale
# shadow of an agent silently overrides the fixed one, and prune cannot see it.
#
# Exit 0 = clean (or planned). Exit 1 = refused, or a problem the caller must surface.
set -uo pipefail

APPLY=0; PROJECT="";
while [ $# -gt 0 ]; do
  case "$1" in
    --apply)   APPLY=1 ;;
    --project) PROJECT="${2:-}"; shift ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "deploy: unknown argument $1" >&2; exit 1 ;;
  esac
  shift
done

# ---- locate the repo, and refuse to run from anywhere else ---------------------
_selfdir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
REPO="$(cd "$_selfdir/../../../.." && pwd)"
if [ ! -f "$REPO/.claude/skills/harness/SKILL.md" ]; then
  echo "deploy: $REPO is not the harness repo (no .claude/skills/harness/SKILL.md)." >&2
  exit 1
fi

GLOBAL_SKILLS="$HOME/.claude/skills"
GLOBAL_AGENTS="$HOME/.claude/agents"
REG_NEW="$HOME/.harness/registry.json"
REG_OLD="$HOME/.gsd/harness-registry.json"

# ---- what ships ----------------------------------------------------------------
# Names are derived from the repo, never from an argument. Every delete target below
# is checked against this set, so a typo cannot widen the blast radius.
SKILL_DIRS=(); for d in "$REPO"/.claude/skills/harness*/; do
  [ -d "$d" ] && SKILL_DIRS+=("$(basename "$d")"); done
AGENTS=(); for f in "$REPO"/.claude/agents/harness-*.md; do
  [ -f "$f" ] && AGENTS+=("$(basename "$f")"); done

if [ ${#SKILL_DIRS[@]} -eq 0 ] || [ ${#AGENTS[@]} -eq 0 ]; then
  echo "deploy: found ${#SKILL_DIRS[@]} skill dirs and ${#AGENTS[@]} agents — refusing." >&2
  echo "        A push computed from an empty set would prune everything." >&2
  exit 1
fi

# The flat skill dirs are SIBLINGS of harness/, not children. `cp -r skills/harness/.`
# copies the router, bin/ and templates/ and NONE of the rule skills or harness-init —
# so every agent's `skills:` list resolves to nothing, silently, because a missing
# skill is not an error. The glob above is what prevents that.
has_flat=0; for s in "${SKILL_DIRS[@]}"; do [ "$s" != "harness" ] && has_flat=1; done
if [ "$has_flat" -eq 0 ]; then
  echo "deploy: only skills/harness/ found, no flat harness-*/ skill dirs — refusing." >&2
  exit 1
fi

say()  { printf '%s\n' "$*"; }
plan() { printf '  %s %s\n' "$1" "$2"; }

# ---- guarded replace: the only destructive primitive ---------------------------
# A resolved target must live under the expected parent AND be named harness*. Anything
# else is a bug in this script, and the correct response to that is to stop.
safe_replace_dir() {           # <src> <dest-parent> <name>
  local src="$1" parent="$2" name="$3" dest="$2/$3"
  case "$name" in harness|harness-*) ;; *) echo "deploy: refusing unsafe name '$name'" >&2; exit 1;; esac
  case "$dest" in "$HOME"/.claude/skills/*|*/.claude/skills/*) ;; *) echo "deploy: refusing unsafe dest '$dest'" >&2; exit 1;; esac
  [ ${#dest} -gt 20 ] || { echo "deploy: refusing suspiciously short dest '$dest'" >&2; exit 1; }
  mkdir -p "$parent"
  rm -rf "$dest"
  cp -R "$src" "$dest"
}

# ============================== PLAN ============================================
say ""
say "harness deploy — $([ $APPLY -eq 1 ] && echo APPLY || echo 'DRY RUN (nothing will change)')"
say "  repo: $REPO"
say "  ships: ${#SKILL_DIRS[@]} skill dirs, ${#AGENTS[@]} agents"
say ""

# ---- global skills -------------------------------------------------------------
say "GLOBAL SKILLS  $GLOBAL_SKILLS"
for s in "${SKILL_DIRS[@]}"; do
  if [ -d "$GLOBAL_SKILLS/$s" ]; then
    plan "~" "$s (replace)"
    # A skill dir is replaced wholesale — correct, since it is harness-owned end to
    # end. But "replace" hides deletions, and an installed tree can be structurally
    # older than the current one (the April layout had personas/, rules/, tdd/).
    # Name what goes, or the destructive part of a routine push is invisible.
    for e in "$GLOBAL_SKILLS/$s"/*; do
      [ -e "$e" ] || continue
      n="$(basename "$e")"
      [ -e "$REPO/.claude/skills/$s/$n" ] || plan " " "    - $s/$n (gone in the current layout)"
    done
  else
    plan "+" "$s (new)"
  fi
done
STALE_SKILLS=()
if [ -d "$GLOBAL_SKILLS" ]; then
  for d in "$GLOBAL_SKILLS"/harness*/; do
    [ -d "$d" ] || continue
    n="$(basename "$d")"; keep=0
    for s in "${SKILL_DIRS[@]}"; do [ "$s" = "$n" ] && keep=1; done
    [ $keep -eq 0 ] && { STALE_SKILLS+=("$n"); plan "-" "$n (PRUNE — not in the repo)"; }
  done
fi

# ---- global agents ---------------------------------------------------------------
say ""
say "GLOBAL AGENTS  $GLOBAL_AGENTS"
new=0; upd=0
for a in "${AGENTS[@]}"; do
  if [ -f "$GLOBAL_AGENTS/$a" ]; then upd=$((upd+1)); else new=$((new+1)); plan "+" "$a (new)"; fi
done
[ $upd -gt 0 ] && plan "~" "$upd existing agent(s) overwritten"
STALE_AGENTS=()
if [ -d "$GLOBAL_AGENTS" ]; then
  for f in "$GLOBAL_AGENTS"/harness-*.md; do
    [ -f "$f" ] || continue
    n="$(basename "$f")"; keep=0
    for a in "${AGENTS[@]}"; do [ "$a" = "$n" ] && keep=1; done
    [ $keep -eq 0 ] && { STALE_AGENTS+=("$n"); plan "-" "$n (PRUNE — deleted from the design)"; }
  done
fi

# ---- registry --------------------------------------------------------------------
PROJECTS="$(python3 - "$REG_NEW" "$REG_OLD" "$PROJECT" <<'PY'
import json, os, sys
new_p, old_p, extra = sys.argv[1], sys.argv[2], sys.argv[3]
def read(p):
    try: return json.load(open(p)).get("projects", []) or []
    except Exception: return []
# Union, order-preserving. Idempotent with both files present, and a project listed
# only in the old registry is carried over rather than orphaned.
seen, out = set(), []
for p in read(new_p) + read(old_p) + ([extra] if extra else []):
    p = os.path.abspath(os.path.expanduser(p))
    if p not in seen:
        seen.add(p); out.append(p)
print("\n".join(out))
PY
)"

say ""
say "REGISTRY  $REG_NEW"
[ -f "$REG_OLD" ] && plan "~" "migrate from $REG_OLD (then renamed .migrated)"
[ -n "$PROJECT" ] && plan "+" "enroll $(cd "$PROJECT" 2>/dev/null && pwd || echo "$PROJECT")"

# ---- per-project ------------------------------------------------------------------
say ""
say "PROJECTS"
LIVE=(); WARN=0
if [ -z "$PROJECTS" ]; then
  say "  (none registered — use --project <path> to enroll one)"
else
  while IFS= read -r p; do
    [ -n "$p" ] || continue
    if [ ! -d "$p" ]; then
      # Dropped from the rewritten registry rather than warned about forever. This is
      # deploy's OWN state, not project state, so tidying it breaks no invariant — and
      # the pre-migration file is kept as .migrated if the path was only unmounted.
      plan "!" "$p — GONE, will be dropped from the registry"; WARN=$((WARN+1)); continue
    fi
    LIVE+=("$p")
    plan "~" "$p — ${#SKILL_DIRS[@]} skill dirs"
    [ -d "$p/.harness" ] || { plan " " "    needs /harness-init (no .harness/)"; }
    # A project whose GSD config injects from paths this push removes is a project
    # this push BREAKS. Say so before it happens, not after.
    if [ -f "$p/.planning/config.json" ] && grep -q '"agent_skills"' "$p/.planning/config.json" 2>/dev/null; then
      plan "!" "    .planning/config.json still has agent_skills pointing at paths this push"
      plan " " "    removes (skills/harness/tdd, /rules). Injection there will resolve to"
      plan " " "    nothing afterwards. Deploy will NOT edit it — that is project state."
      WARN=$((WARN+1))
    fi
  done <<< "$PROJECTS"
fi

say ""
if [ $APPLY -eq 0 ]; then
  say "DRY RUN — nothing changed. Re-run with --apply to perform this plan."
  if [ ${#STALE_SKILLS[@]} -gt 0 ] || [ ${#STALE_AGENTS[@]} -gt 0 ]; then
    say "Note: --apply DELETES the items marked '-'. That is the point, and re-running does not undo it."
  fi
  if [ $WARN -gt 0 ]; then say "$WARN warning(s) above need a human decision."; fi
  exit 0
fi

# ============================== APPLY ============================================
say "applying…"

# Cheap insurance on the one irreversible step, same as merge-settings.py takes.
if [ ${#STALE_AGENTS[@]} -gt 0 ] && [ -d "$GLOBAL_AGENTS" ]; then
  bak="$HOME/.claude/agents.harness-bak"
  rm -rf "$bak"; cp -R "$GLOBAL_AGENTS" "$bak"
  say "  backup: $bak"
fi

for s in "${SKILL_DIRS[@]}"; do
  safe_replace_dir "$REPO/.claude/skills/$s" "$GLOBAL_SKILLS" "$s"
done
# NOTE the ${ARR+"${ARR[@]}"} form, here and below. On macOS's bash 3.2, `set -u` plus
# a bare "${empty_array[@]}" is an UNBOUND VARIABLE error, not an empty loop — and it
# aborted a real apply here after the skills were copied but before agents, registry or
# projects ran. A half-applied deploy is the worst state this script can produce, so
# every possibly-empty array is expanded with the guard.
for n in ${STALE_SKILLS+"${STALE_SKILLS[@]}"}; do
  case "$n" in harness|harness-*) rm -rf "${GLOBAL_SKILLS:?}/$n" ;; esac
done
mkdir -p "$GLOBAL_AGENTS"
for a in "${AGENTS[@]}"; do cp "$REPO/.claude/agents/$a" "$GLOBAL_AGENTS/$a"; done
for n in ${STALE_AGENTS+"${STALE_AGENTS[@]}"}; do
  case "$n" in harness-*.md) rm -f "${GLOBAL_AGENTS:?}/$n" ;; esac
done
say "  global: ${#SKILL_DIRS[@]} skill dirs, ${#AGENTS[@]} agents, ${#STALE_SKILLS[@]} skill prune(s), ${#STALE_AGENTS[@]} agent prune(s)"

mkdir -p "$(dirname "$REG_NEW")"
# Only live projects are written back; a path that no longer exists is dropped.
#
# Passed as argv, NOT piped: `python3 - <<'PY'` already uses stdin for the program, so
# a pipe into it is silently discarded — which wrote an EMPTY registry while the
# per-project push visibly succeeded. Two sources, one stdin, no error.
_live="$(printf '%s\n' ${LIVE+"${LIVE[@]}"})"
python3 - "$REG_NEW" "$_live" <<'PY'
import json, sys
projects = [l.strip() for l in sys.argv[2].splitlines() if l.strip()]
open(sys.argv[1], "w").write(json.dumps({"projects": projects}, indent=2) + "\n")
PY
[ -f "$REG_OLD" ] && mv "$REG_OLD" "$REG_OLD.migrated" && say "  registry: migrated, old file kept as $(basename "$REG_OLD").migrated"
say "  registry: $REG_NEW"

for p in ${LIVE+"${LIVE[@]}"}; do
  for s in "${SKILL_DIRS[@]}"; do
    safe_replace_dir "$REPO/.claude/skills/$s" "$p/.claude/skills" "$s"
  done
  # Reconcile the project's tool tree too — a stale skill dir there shadows nothing
  # but is read by agents as though it were current.
  for d in "$p"/.claude/skills/harness*/; do
    [ -d "$d" ] || continue
    n="$(basename "$d")"; keep=0
    for s in "${SKILL_DIRS[@]}"; do [ "$s" = "$n" ] && keep=1; done
    [ $keep -eq 0 ] && case "$n" in harness|harness-*) rm -rf "$d" ;; esac
  done
  say "  ✓ $p"
done

say ""
say "done. Agents are GLOBAL only — do not copy them per-project (DEC-113)."
say "A project with no .harness/ still needs /harness-init before a crew will run."
say "Agent definitions are not live-reloaded: restart Claude Code before spawning."
