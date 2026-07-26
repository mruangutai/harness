#!/usr/bin/env bash
# Propagation checker — catch statements that a superseding decision invalidated.
#
# WHY: DEC-103. After 12 decisions were recorded, SPEC and BUILD still contained
# TEN statements those decisions had already falsified. That is the exact defect
# the SPEC/DECISIONS/BUILD split was created to prevent, and the split did not
# prevent it — because appending to DECISIONS is cheap while re-reading a
# 1853-line SPEC is not.
#
# HOW IT STAYS MAINTAINED: the registry is DECISIONS.md itself. A decision that
# supersedes something declares the stale wording inline, at the moment it
# supersedes it:
#
#     <!-- stale: "pending spike" -->
#     <!-- stale: "rules/<name>/SKILL.md" -->
#
# A doc line that legitimately QUOTES stale wording (the migration map's
# «change "old" -> new» rows, or a section describing a retired mechanism)
# marks itself with an inline  <!-- ok-stale -->  and is skipped.
#
# There is no separate list to drift out of sync, and the declaration sits in the
# same paragraph as the reasoning that justifies it.
#
# Exit 0 = clean. Exit 1 = stale statements found.
set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-$(pwd)}"

python3 - <<'PY'
import re, sys, os

D = "docs/harness"
dec = os.path.join(D, "DECISIONS.md")
if not os.path.isfile(dec):
    print(f"check-docs: {dec} not found."); sys.exit(1)

text = open(dec, encoding="utf-8").read()

# Attribute each marker to the DEC that declared it, so a hit names its authority.
owner, pats = None, []
for line in text.splitlines():
    m = re.match(r"^##\s+(DEC-\d+)", line)
    if m:
        owner = m.group(1)
    for s in re.findall(r"<!--\s*stale:\s*(.+?)\s*-->", line):
        pats.append((owner or "?", s.strip().strip('"\'')))

if not pats:
    print("check-docs: no <!-- stale: ... --> markers declared yet — nothing to check.")
    sys.exit(0)

targets = [os.path.join(D, f) for f in ("SPEC.md", "BUILD.md")]
targets = [t for t in targets if os.path.isfile(t)]

hits = 0
for t in targets:
    lines = open(t, encoding="utf-8").read().splitlines()
    for i, line in enumerate(lines, 1):
        low = line.lower()
        # An EXPLICIT escape beats a clever heuristic. A line may legitimately
        # quote stale wording — the migration map says «change "old" -> new», and
        # a spec section may describe a mechanism it has retired. Those lines mark
        # themselves. Anything unmarked is treated as a real claim.
        if "<!-- ok-stale -->" in line:
            continue
        # Lines that are themselves narrating the correction are also fine.
        if any(k in low for k in ("an earlier", "was wrong", "superseded",
                                  "no longer", "corrected", "inverted")):
            continue
        for dec_id, pat in pats:
            if pat.lower() in low:
                hits += 1
                print(f"  STALE  {t}:{i}")
                print(f"         matches {pat!r}, invalidated by {dec_id}")
                print(f"         > {line.strip()[:100]}")

print(f"\nchecked {len(pats)} superseded pattern(s) across {len(targets)} file(s).")
if hits:
    print(f"{hits} stale statement(s) — a decision was recorded but never propagated.")
    sys.exit(1)
print("no stale statements found.")
PY
