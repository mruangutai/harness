#!/usr/bin/env python3
"""Mechanical conflict audit of DECISIONS.md + its index.

Computes what reading 4,600 lines cannot reliably do by hand:
  A. a decision whose BODY claims to reverse/supersede DEC-N, while DEC-N's index
     row carries no marker  -> a reader of the index acts on a dead rule
  B. index row says SUPERSEDED but no body prose supports it (and vice versa)
  C. duplicate decision numbers
  D. references to decisions that do not exist
  E. amendment headings physically orphaned from their parent's section, which is
     how refs get misattributed (observed today with DEC-142 am.1 inside DEC-173)
"""
import re, pathlib, collections, sys

D = pathlib.Path(".harness/harness/docs/DECISIONS.md").read_text(encoding="utf-8")
I = pathlib.Path(".harness/harness/docs/DECISIONS-INDEX.md").read_text(encoding="utf-8")

# --- fence-guard: a ## DEC- inside a code fence is an example, not a decision.
lines, in_fence, tops = D.split("\n"), False, []
for n, l in enumerate(lines, 1):
    if l.lstrip().startswith("```"):
        in_fence = not in_fence
        continue
    if in_fence:
        continue
    m = re.match(r"^## (DEC-(\d+))\b(.*)", l)
    if m:
        tops.append((m.group(1), int(m.group(2)), n, m.group(3)))

amend = [(re.match(r"^### (DEC-\d+) amendment", l).group(1), n)
         for n, l in enumerate(lines, 1) if re.match(r"^### DEC-\d+ amendment", l)]

rows = {}
for l in I.split("\n"):
    m = re.match(r"^- (DEC-\d+) @(\d+)((?: am\.\d+(?:-am\.\d+)?)?) \[([^\]]*)\] refs:([^:]*)::(.*)", l)
    if m:
        rows[m.group(1)] = {"line": int(m.group(2)), "am": m.group(3).strip(),
                            "refs": m.group(5).split(), "ruling": m.group(6).strip()}

ids = [t[0] for t in tops]
byline = {t[0]: t[2] for t in tops}
print(f"decisions: {len(tops)} top-level (fence-guarded) · {len(amend)} amendment headings "
      f"· {len(rows)} index rows\n")

issues = collections.defaultdict(list)

# C. duplicates
for k, v in collections.Counter(ids).items():
    if v > 1:
        issues["C duplicate decision number"].append(f"{k} appears {v}x as a top-level heading")

# index vs body membership
for k in rows:
    if k not in byline:
        issues["B index row with no body heading"].append(k)
for k in byline:
    if k not in rows:
        issues["B body heading with no index row"].append(k)

# sections, for attributing prose
bounds = sorted((t[2], t[0]) for t in tops)
def owner_of(lineno):
    cur = None
    for ln, k in bounds:
        if ln <= lineno:
            cur = k
        else:
            break
    return cur

# A. reversal/supersession claimed in prose
CLAIM = re.compile(r"(reverses|reversed|supersedes|superseded|REVERSED|SUPERSEDES|"
                   r"no longer holds|overrides)\b[^.\n]{0,120}?(DEC-\d+)", re.I)
for n, l in enumerate(lines, 1):
    for verb, target in CLAIM.findall(l):
        src = owner_of(n)
        if target == src:
            continue
        r = rows.get(target)
        if r is None:
            issues["D reference to a nonexistent decision"].append(f"{src} -> {target} (line {n})")
        elif not re.search(r"SUPERSEDED|REVERSED|reversed|superseded", r["ruling"], re.I):
            issues["A claimed reversal not reflected in the target's index ruling"].append(
                f"{src}:{n} says '{verb} {target}' — {target}'s row shows no marker")

# D. all DEC- references resolve
for n, l in enumerate(lines, 1):
    if l.lstrip().startswith("```"):
        continue
    for ref in set(re.findall(r"\bDEC-(\d+)\b", l)):
        if f"DEC-{ref}" not in byline:
            issues["D reference to a nonexistent decision"].append(f"DEC-{ref} at line {n}")

# E. orphaned amendments — parent section does not contain the amendment
for parent, n in amend:
    if owner_of(n) != parent:
        issues["E amendment sits outside its parent's section"].append(
            f"{parent} amendment at line {n} is inside {owner_of(n)}'s section "
            f"— refs and @anchor get misattributed")

for k in sorted(issues):
    v = sorted(set(issues[k]))
    print(f"## {k}  ({len(v)})")
    for x in v[:14]:
        print(f"   - {x}")
    if len(v) > 14:
        print(f"   ... +{len(v)-14} more")
    print()
if not issues:
    print("no mechanical inconsistencies found.")
