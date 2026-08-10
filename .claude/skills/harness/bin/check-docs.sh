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

python3 - "$@" <<'PY'
import re, sys, os, glob

D = "docs/harness"
dec = os.path.join(D, "DECISIONS.md")
if not os.path.isfile(dec):
    print(f"check-docs: {dec} not found."); sys.exit(1)

text = open(dec, encoding="utf-8").read()

# Attribute each marker to the DEC that declared it, so a hit names its authority.
owner, pats, infence = None, [], False
for line in text.splitlines():
    # Markers shown INSIDE a code fence are documentation of the format, not live
    # declarations. Harvesting them would let an illustrative example become an
    # enforced rule.
    if line.lstrip().startswith("```"):
        infence = not infence
        continue
    if infence:
        continue
    m = re.match(r"^##\s+(DEC-\d+)", line)
    if m:
        owner = m.group(1)
    for s in re.findall(r"<!--\s*stale:\s*(.+?)\s*-->", line):
        s = s.strip().strip('"\'')
        # An EMPTY pattern matches every line. This is not hypothetical: DEC-109's
        # prose mentions the marker syntax inline (outside a code fence) to explain
        # it, and that got harvested as an empty rule that flagged all 1889 lines of
        # SPEC. Require real content, and require it to be reasonably specific.
        if len(s) < 4:
            continue
        pats.append((owner or "?", s))

if not pats:
    print("check-docs: no <!-- stale: ... --> markers declared yet — nothing to check.")
    sys.exit(0)

# EVERY prose surface a human or an agent reads, not just the two design docs.
#
# It was SPEC.md + BUILD.md only. Two separate failures came out of that narrowness in
# one session, on runs that were green the whole time:
#
#   - "three prerequisites" and "three `settings.json`" survived in harness-init's
#     SKILL.md and .harness/README.md and had to be found by hand-grep;
#   - harness-init's own `description:` — the line the model reads to decide whether to
#     invoke the skill — still advertised "three platform prerequisites" after
#     everything else had been corrected.
#
# A skill is read by an agent at spawn and a template is copied into a project, so a
# stale claim in either propagates FURTHER than one in SPEC.md, not less. Frontmatter
# is the worst place of all for one, because it is the part nobody re-reads.
targets = []
# THE REPO ROOT, NON-RECURSIVELY (issue #139). CLAUDE.md is read at EVERY session start —
# the widest blast radius of any file here, wider than SPEC.md or any agent file — and the
# propagation checker could not see it. Verified before the fix by planting a live stale
# phrase in it: zero hits. Root-level *.md only, at depth 0 and never `**`: recursing from
# `.` would walk .git, node_modules and .claude/worktrees/, where every file in every other
# checkout would be scanned as if it were this one.
targets += glob.glob("*.md")
# `docs`, NOT `docs/harness` — the constitution lives at docs/principles.md, one directory
# above the design docs, and was the last prose surface an agent reads that this checker could
# not see. It reaches all 16 agents distilled, as the preloaded `harness-principles` skill, so a
# superseded sentence there propagates as far as one in an agent file. Measured when this widened:
# 0 of 62 markers matched it, so the change added coverage without changing the verdict. The skill
# itself was already in scope under `.claude/skills` below.
for base, pats_ in (("docs", ("*.md", "*.html")),
                    (".harness", ("*.md",)),
                    (".claude/skills", ("*.md",)),
                    (".claude/commands", ("*.md",)),
                    # Agent files were missing, and they are the same argument as skills: an
                    # agent file is read at every spawn of that agent, so a stale claim in one
                    # propagates FURTHER than one in SPEC.md. Found by the #138 review, where
                    # this PR's own central rule ("you do not preload harness-team") landed in
                    # a file the checker could not see.
                    (".claude/agents", ("*.md",))):
    for pat in pats_:
        targets += glob.glob(os.path.join(base, "**", pat), recursive=True)
# DECISIONS.md is the registry, not a target: it QUOTES stale wording by design, in
# the very paragraph that supersedes it. Scanning it would flag every marker forever.
# Run dirs are ephemeral, git-ignored RECORDS of what happened — a digest that says
# "pm wrote .harness/PLAN.md" was true when written and stays true as history, exactly
# like a quote in DECISIONS.md. Scanning them makes every path migration flag its own
# past. STATE.md and feature docs stay in scope: those are live.
targets = sorted(t for t in set(targets)
                 if os.path.isfile(t) and os.path.basename(t) != "DECISIONS.md"
                 and "/runs/" not in t)

if "--audit" in sys.argv:
    # Which markers are actually load-bearing? A marker that matches nothing today AND
    # has never matched anything in history is inert, and inert rules make a green run
    # read as more thorough than it is (the DEC-119 failure in another costume). This
    # found 11 of 25 — all wording from the pre-restructure plan file, never in the repo.
    #
    # HEURISTIC, NOT PROOF, and it errs toward calling a live marker dead: history is
    # only visible for TRACKED files, and a marker whose wording spans a line break can
    # never match a line-based checker even though the claim is really there. Before
    # deleting one, confirm which it is. `three `settings.json`` was the second kind.
    import subprocess
    print(f"marker audit — {len(pats)} declared, {len(targets)} file(s) scanned\n")
    dead = 0
    for dec, p in pats:
        live = sum(1 for t in targets
                   for ln in open(t, encoding="utf-8", errors="replace").read().splitlines()
                   if p.lower() in ln.lower())
        r = subprocess.run(["git", "log", "--oneline", "-S", p, "--"] + targets,
                           capture_output=True, text=True)
        hist = len([l for l in r.stdout.splitlines() if l.strip()])
        if not live and not hist:
            dead += 1
            print(f"  INERT   {dec:8} {p!r} — never matched any scanned file, ever.")
    print(f"\n{dead} inert marker(s) of {len(pats)}."
          if dead else f"\nall {len(pats)} markers are load-bearing.")
    sys.exit(1 if dead else 0)

hits = 0
found = {}   # (dec_id, pattern) -> [(file, lineno, snippet), ...]
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
                found.setdefault((dec_id, pat), []).append((t, i, line.strip()[:100]))

# Grouped by PATTERN, with every location listed together. Reporting one location at a
# time made a phrase occurring twice take two round-trips: the reader fixed the line the
# checker named, re-ran, and got another failure for the same pattern. FEAT-04 spent
# three trips on exactly that. The full set has to be visible in one pass.
for (dec_id, pat), locs in sorted(found.items(), key=lambda kv: kv[0][1]):
    print(f"  STALE  {pat!r} — invalidated by {dec_id} — "
          f"{len(locs)} location(s), ALL must be fixed or escaped:")
    for t, i, snippet in locs:
        print(f"         {t}:{i}")
        print(f"         > {snippet}")

print(f"\nchecked {len(pats)} superseded pattern(s) across {len(targets)} file(s).")
if hits:
    print(f"{hits} stale statement(s) across {len(found)} pattern(s) — a decision was "
          f"recorded but never propagated.")
    print("Fix every location listed above in one pass. A line that legitimately QUOTES "
          "stale wording marks itself with <!-- ok-stale --> (per line, not per file).")
    sys.exit(1)
print("no stale statements found.")
PY
