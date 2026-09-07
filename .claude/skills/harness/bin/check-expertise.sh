#!/usr/bin/env bash
# check-expertise.sh — validate an Expertise file against the format contract (DEC-145).
#
# Usage: check-expertise.sh <file.md> [<file.md> ...]
#        check-expertise.sh <dir>          # checks every *.md under it
#
# Enforces, per file:
#   - only the four canonical sections: Patterns / Gotchas / Outcomes / Open
#   - section entry caps: 15 / 15 / 10 / 5
#   - entry format `- XX-NN: ...` at column 0; no nested bullets
#   - per-entry word cap: 50
#   - no feature/task/issue tokens (FEAT-NN, T-NN, #NN) — those belong in observations
#   - file budget: 150 lines for a CRAFT-tier file (.harness/expertise/<name>.md),
#     40 lines for a REPOSITORY-tier file (.harness/<segment>/expertise/<name>.md)
#     (the spawn hook truncates there); classified by the resolved absolute path
#   - CRAFT-tier files only: an ADVISORY (never blocking) scan for repository-specific
#     tokens (DEC-NN, .harness/, check-*.sh, ...) — see issue 340
#   - both tiers: an ADVISORY (never blocking) once a file is within 10% of its own
#     line budget — the only signal below that fires while there is still headroom
#     to displace an entry rather than overflow (issue #613)
#
# Exit 0 = all files clean. Exit 1 = violations (listed). Exit 2 = usage error.
set -uo pipefail

[ $# -ge 1 ] || { echo "usage: check-expertise.sh <file-or-dir> ..." >&2; exit 2; }

files=()
for arg in "$@"; do
  if [ -d "$arg" ]; then
    while IFS= read -r f; do files+=("$f"); done < <(find "$arg" -maxdepth 1 -name '*.md' | sort)
  elif [ -f "$arg" ]; then
    files+=("$arg")
  else
    echo "check-expertise: no such file or directory: $arg" >&2; exit 2
  fi
done
[ ${#files[@]} -ge 1 ] || { echo "check-expertise: nothing to check" >&2; exit 2; }

python3 -I - "${files[@]}" <<'PY'
import re, sys, os

CAPS = {"Patterns": 15, "Gotchas": 15, "Outcomes": 10, "Open": 5}

# Issue #254: the three sections whose id prefix has been 100% consistent across every
# file in this repository (measured 2026-09-07 against every .harness/**/expertise/*.md:
# zero violations). Open is deliberately NOT pinned here — live files disagree on its
# prefix ('OQ-', 'O-' and 'Q-' all appear on disk) and forcing one would fail files that
# are not wrong. The cross-section-collision check below still catches Open reusing a
# prefix another section in the SAME file already owns, which is the actual defect shape.
CANONICAL_PREFIX = {"Patterns": "P", "Gotchas": "G", "Outcomes": "O"}
CRAFT_LINE_BUDGET = 150
REPO_LINE_BUDGET = 40
# Issue #613: "near budget" is within 1/NEAR_BUDGET_FRACTION of the tier's own line
# budget (150//10 = 15 lines of headroom for craft, 40//10 = 4 for repo) — fixed data,
# not re-derived per call, so the threshold means the same thing for every file this
# script checks.
NEAR_BUDGET_FRACTION = 10
WORD_CAP = 50
SECTION_RE = re.compile(r"^## (\w+)(?: \(max (\d+)\))?\s*$")
ENTRY_RE = re.compile(r"^- ([A-Z]{1,3}-\d+): ")
FEATURE_TOKEN_RE = re.compile(r"\bFEAT-\d+\b|\bT-\d+\b|#\d+\b")

# The repository-specific token set (issue 340), verbatim. Advisory-only, CRAFT-tier only.
REPO_TOKEN_RE = re.compile(
    r"DEC-\d+|INV-\d+|FEAT-\d+|\.harness/|\.claude/|check-[a-z-]*\.sh|"
    r"factory_[a-z]*\.py|gh-sync|harness\.json|team-config"
)

# CRAFT tier: a path ending in .harness/expertise/<name>.md
CRAFT_TIER_RE = re.compile(r"(^|/)\.harness/expertise/[^/]+\.md$")
# REPOSITORY tier: a path ending in .harness/<segment>/expertise/<name>.md
REPO_TIER_RE = re.compile(r"(^|/)\.harness/[^/]+/expertise/[^/]+\.md$")


def classify_tier(path):
    """Classify by the resolved absolute path, never the argument as typed —
    a bare-path invocation from a cwd under .harness/... must still resolve
    to its true tier (see check-expertise.sh's CHANGE 1 note)."""
    ap = os.path.abspath(path)
    if CRAFT_TIER_RE.search(ap):
        return "craft", CRAFT_LINE_BUDGET
    if REPO_TIER_RE.search(ap):
        return "repo", REPO_LINE_BUDGET
    return None, CRAFT_LINE_BUDGET


failed = False
for path in sys.argv[1:]:
    problems = []
    advisories = []
    tier, line_budget = classify_tier(path)
    lines = open(path, encoding="utf-8").read().splitlines()

    if len(lines) > line_budget:
        problems.append(f"{len(lines)} lines — over the {line_budget}-line budget (the spawn hook truncates the rest)")

    # Issue #613: the ONLY signal above is a hard failure once the file is ALREADY over
    # budget — the first warning arrived after inject-expertise.sh had already truncated
    # the tail from every spawn. A file caught here, three lines under 150, still has
    # room to DISPLACE an entry before the next distillation pushes it over; that
    # headroom is exactly what this advisory exists to spend while it still exists.
    # NEAR_BUDGET_FRACTION mirrors CRAFT_LINE_BUDGET/REPO_LINE_BUDGET as fixed data
    # (never re-derived per call) so "near" means the same thing everywhere this
    # script runs. Applies to BOTH tiers — a repo-tier file is truncated by the exact
    # same mechanism (inject-expertise.sh caps both), so its headroom is just as real.
    near_budget_threshold = line_budget - line_budget // NEAR_BUDGET_FRACTION
    if near_budget_threshold <= len(lines) <= line_budget:
        advisories.append(
            f"ADVISORY {path}: {len(lines)} lines of a {line_budget}-line budget "
            f"({line_budget - len(lines)} lines of headroom) — the next entry must "
            f"DISPLACE an existing one, not append (issue #613)")


    # --- TITLE (B-10). This file is injected whole into its agent's context at every
    # spawn, so line 1 is what tells the agent whose memory it is reading. A missing
    # title silently opens the injected block with `## Patterns`; a title naming the
    # WRONG agent hands one agent another's rules, which is worse than no title at all.
    # The checker had neither rule, and three of this repo's own files carried no title.
    expected = f"# Expertise — {os.path.basename(path)[:-3]}"
    actual = lines[0] if lines else ""
    if actual.strip() != expected:
        if not actual.strip().startswith("# Expertise —"):
            problems.append(f"line 1 must be the title {expected!r}, found {actual.strip()[:48]!r} "
                            f"— the injected block opens with this and names whose memory it is")
        else:
            problems.append(f"line 1 titles {actual.strip()[14:].strip()!r} but the filename says "
                            f"{os.path.basename(path)[:-3]!r} — an agent must never be handed "
                            f"another agent's memory")

    section = None
    counts = {}
    entries = []          # (section, id, first_lineno, text)
    for i, line in enumerate(lines, 1):
        m = SECTION_RE.match(line)
        if line.startswith("## ") and not m:
            problems.append(f"line {i}: non-canonical section {line!r}")
            section = None
            continue
        if m:
            name = m.group(1)
            if name not in CAPS:
                problems.append(f"line {i}: non-canonical section '## {name}' — only {'/'.join(CAPS)} are legal")
                section = None
            else:
                section = name
                counts.setdefault(name, 0)
            continue
        if re.match(r"^\s+- ", line):
            problems.append(f"line {i}: nested bullet — sub-points are banned; distill to one rule")
            continue
        if line.startswith("- "):
            em = ENTRY_RE.match(line)
            if not em:
                problems.append(f"line {i}: entry lacks the '- XX-NN: ' id prefix")
                if section:
                    counts[section] = counts.get(section, 0) + 1
                entries.append((section, None, i, line[2:]))
                continue
            if section is None:
                problems.append(f"line {i}: entry {em.group(1)} outside any canonical section")
            else:
                counts[section] += 1
            entries.append((section, em.group(1), i, line[len(em.group(0)):]))
            continue
        if entries and line.startswith("  ") and line.strip():
            sec, eid, lno, text = entries[-1]
            entries[-1] = (sec, eid, lno, text + " " + line.strip())

    for sec, cap in CAPS.items():
        n = counts.get(sec, 0)
        if n > cap:
            problems.append(f"section {sec}: {n} entries — cap is {cap}")

    # Issue #254: an id's prefix was never checked against its own section, nor against
    # every OTHER id in the file — a `G-` entry could sit under a section that is not
    # Gotchas, and two sections could mint the identical id independently. Live example,
    # found while building this check and fixed alongside it:
    # .harness/harness/expertise/harness-orchestrator.md carried `O-01` under BOTH
    # Outcomes and Open — a `replace` op naming O-01 could not tell which rule it meant.
    #
    # NOT ENFORCED: numeric contiguity. Measured the same day: gaps are the normal
    # residue of distillation displacing a resolved entry — present in at least 13 of
    # this repository's own files (e.g. `harness-orchestrator.md`'s craft-tier Open
    # section is missing OQ-02). A contiguity rule would fail all of them for correct,
    # ordinary behaviour, so it is not part of this check.
    prefix_owner = {}   # prefix -> the section that first claimed it in THIS file
    seen_ids = {}        # "PREFIX-NN" -> first line number, in THIS file
    for sec, eid, lno, text in entries:
        if eid is None or sec is None:
            continue
        prefix = eid.split("-", 1)[0]
        canon = CANONICAL_PREFIX.get(sec)
        if canon is not None and prefix != canon:
            problems.append(f"line {lno}: {eid} sits under {sec}, whose entries use "
                            f"'{canon}-' — id prefix does not match its section")
        elif prefix in prefix_owner and prefix_owner[prefix] != sec:
            problems.append(f"line {lno}: {eid}'s prefix '{prefix}-' already belongs to "
                            f"this file's {prefix_owner[prefix]} section — a mis-sectioned "
                            f"id, or a collision, either way unfindable by prefix alone")
        else:
            prefix_owner.setdefault(prefix, sec)
        if eid in seen_ids:
            problems.append(f"line {lno}: duplicate id {eid} — first used at line "
                            f"{seen_ids[eid]}; a repeated id makes a `replace` op "
                            f"ambiguous about which entry it targets")
        else:
            seen_ids[eid] = lno

    for sec, eid, lno, text in entries:
        label = eid or f"entry at line {lno}"
        words = len(text.split())
        if words > WORD_CAP:
            problems.append(f"line {lno}: {label} is {words} words — cap is {WORD_CAP}; a rule, not a story")
        tok = FEATURE_TOKEN_RE.search(text)
        if tok:
            problems.append(f"line {lno}: {label} names '{tok.group(0)}' — feature/issue tokens belong in observations, not Expertise")

        # CHANGE 2 (issue 340): advisory-only repository-token scan, CRAFT-tier only.
        # Never appended to `problems` — must never fail the gate or flip the exit code.
        if tier == "craft":
            for rm in REPO_TOKEN_RE.finditer(text):
                advisories.append(
                    f"ADVISORY {path}:{lno}: {label} names '{rm.group(0)}' — "
                    f"repository-layer candidate; rule on it (issue 340)"
                )

    if problems:
        failed = True
        print(f"FAIL {path}")
        for p in problems:
            print(f"  - {p}")
    else:
        print(f"OK   {path}")
    for a in advisories:
        print(a)

sys.exit(1 if failed else 0)
PY
