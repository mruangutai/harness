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
#   - file budget: 150 lines (the spawn hook truncates there)
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

python3 - "${files[@]}" <<'PY'
import re, sys, os

CAPS = {"Patterns": 15, "Gotchas": 15, "Outcomes": 10, "Open": 5}
LINE_BUDGET = 150
WORD_CAP = 50
SECTION_RE = re.compile(r"^## (\w+)(?: \(max (\d+)\))?\s*$")
ENTRY_RE = re.compile(r"^- ([A-Z]{1,3}-\d+): ")
FEATURE_TOKEN_RE = re.compile(r"\bFEAT-\d+\b|\bT-\d+\b|#\d+\b")

failed = False
for path in sys.argv[1:]:
    problems = []
    lines = open(path, encoding="utf-8").read().splitlines()

    if len(lines) > LINE_BUDGET:
        problems.append(f"{len(lines)} lines — over the {LINE_BUDGET}-line budget (the spawn hook truncates the rest)")

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

    for sec, eid, lno, text in entries:
        label = eid or f"entry at line {lno}"
        words = len(text.split())
        if words > WORD_CAP:
            problems.append(f"line {lno}: {label} is {words} words — cap is {WORD_CAP}; a rule, not a story")
        tok = FEATURE_TOKEN_RE.search(text)
        if tok:
            problems.append(f"line {lno}: {label} names '{tok.group(0)}' — feature/issue tokens belong in observations, not Expertise")

    if problems:
        failed = True
        print(f"FAIL {path}")
        for p in problems:
            print(f"  - {p}")
    else:
        print(f"OK   {path}")

sys.exit(1 if failed else 0)
PY
