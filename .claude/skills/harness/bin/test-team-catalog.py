#!/usr/bin/env python3
"""FEAT-06 — the team-definition layer and the blocking qa gate, asserted mechanically.

WHY THIS EXISTS: every defect this feature closed was **a definition or a check that
appears to exist but does nothing** —

  INV-6                 fired only on an ABSENT `review_sha`, so the string `none`
                        read as a pinned SHA and an unpinned feature passed (#16).
  teams/review.yaml     omitted the qa step, so the project's only blocking gate ran
                        three times only because a lead added it by hand (#8).
  teams/build.yaml      did not exist; every build composed its step list at dispatch (#9).
  harness/SKILL.md      contained ZERO occurrences of `qa` and `test_matrix` while
                        SPEC.md:1978 assigned the sequencing to the orchestrator (#24).

The last one is the point. `SKILL.md` is the only file `harness-orchestrator` preloads,
so an obligation recorded anywhere else is an obligation its owner never reads. Check (8)
is the assertion that makes that fix falsifiable: **no other check in this feature fails
if `SKILL.md` is never touched for qa.**

A gate that guesses is the defect class this file exists to close, so check (9) FAILS
LOUDLY on an ambiguous SPEC row rather than picking a brace group and hoping.
"""
import json
import os
import re
import sys

try:
    import harness_yaml
except ModuleNotFoundError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        import harness_yaml
    except ModuleNotFoundError:
        print("test-team-catalog: PyYAML is not importable from this interpreter "
              f"({sys.executable}).\n"
              "  install:  python3 -m pip install --user --break-system-packages pyyaml\n"
              "  This is REQUIRED, not optional (DEC-171 am.1).", file=sys.stderr)
        sys.exit(1)

REPO = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
TEAMS = os.path.join(REPO, ".claude", "skills", "harness", "teams")
BIN = os.path.join(REPO, ".claude", "skills", "harness", "bin")
SKILL_MD = os.path.join(REPO, ".claude", "skills", "harness", "SKILL.md")
SPEC_MD = os.path.join(REPO, "docs", "harness", "SPEC.md")

fails = 0
ran = 0


def check(name, ok, detail=""):
    # Counted, never a literal total: a frozen count reddens the moment a case is added.
    global fails, ran
    ran += 1
    if ok:
        print(f"ok    {name}")
    else:
        fails += 1
        print(f"FAIL  {name}")
        for line in str(detail).splitlines():
            print(f"      | {line}")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


# --- 1. review.yaml carries the qa step, gate-only ---------------------------
try:
    review = harness_yaml.load_file(os.path.join(TEAMS, "review.yaml"))
    ids = {s["id"] for s in review["steps"]}
    qa = next((s for s in review["steps"] if s["id"] == "qa"), None)
    ok = (ids == {"code", "qa", "security", "ui"}
          and qa is not None and qa["persona"] == "qa" and qa["mutates_repo"] is False)
    check("(1) review.yaml is {code, qa, security, ui} and qa is gate-only "
          "(persona: qa, mutates_repo: false) — SC-04, MF-1", ok,
          f"ids={sorted(ids)} qa={qa}")
except Exception as e:
    check("(1) review.yaml is {code, qa, security, ui} and qa is gate-only "
          "(persona: qa, mutates_repo: false) — SC-04, MF-1", False, e)

# --- 2. build.yaml exists and is the eng-lead's ------------------------------
build = None
try:
    build = harness_yaml.load_file(os.path.join(TEAMS, "build.yaml"))
    check("(2) build.yaml parses, name: build, lead: eng-lead — SC-07",
          build.get("name") == "build" and build.get("lead") == "eng-lead",
          f"name={build.get('name')!r} lead={build.get('lead')!r}")
except Exception as e:
    check("(2) build.yaml parses, name: build, lead: eng-lead — SC-07", False, e)

# --- 3. the team is single-squad — the DEC-118 assertion ---------------------
# READ FROM team-config.yaml, THE ONLY FILE THAT CAN BE RIGHT ABOUT THIS. build.yaml
# used to carry a copied `personas:` roster and this check asserted the copy was a
# subset of the real one — but nothing at runtime read that copy, and the assertion
# pointed the wrong way: it caught a persona that should not be there and could NOT
# catch a member added to the squad, which is the direction a copy actually rots.
# The single-squad property is carried by the team's LEAD: build.yaml declares
# `lead: eng-lead`, and team-config records which squad that lead owns. A lead cannot
# dispatch outside its own squad (DEC-118), so a team hosted by an eng-squad lead is
# eng-squad by construction — no roster copy required.
try:
    tc = harness_yaml.load_file(os.path.join(REPO, ".harness", "team-config.yaml"))
    lead_name = build["lead"]
    lead_rec = next((l for l in tc["leads"]
                     if l["name"] in (lead_name, f"harness-{lead_name}")), None)
    eng = next(t for t in tc["teams"] if t.get("team-name") == "Engineering")
    eng_members = {m["name"] for m in eng["members"]}
    check("(3) build.yaml is hosted by a lead whose squad is Engineering, so the team "
          "is single-squad by construction — SC-07, DEC-118",
          lead_rec is not None and lead_rec.get("squad") == "eng",
          f"lead={lead_name!r} record={lead_rec}")
except Exception as e:
    check("(3) build.yaml is hosted by a lead whose squad is Engineering, so the team "
          "is single-squad by construction — SC-07, DEC-118", False, e)

# --- 4. the recorded floor, asserted against the squad that will supply it ----
# FEAT-03's eng build runs 2026-07-31-09-eng and -10-eng used dev-ops and backend-dev.
# The expansion routes by `consult-when` at dispatch, so what makes those reachable is
# their membership of the Engineering squad — not a list in build.yaml.
try:
    check("(4) the Engineering squad covers the personas FEAT-03's eng build runs "
          "actually used {dev-ops, backend-dev} — SC-08",
          {"harness-dev-ops", "harness-backend-dev"} <= eng_members,
          f"Engineering={sorted(eng_members)}")
except Exception as e:
    check("(4) the Engineering squad covers the personas FEAT-03's eng build runs "
          "actually used {dev-ops, backend-dev} — SC-08", False, e)

# --- 5. the playbook names the build team, with its bound -------------------
try:
    lines = read(SKILL_MD).splitlines()
    hit = [l for l in lines if "build" in l and "DEC-118" in l]
    check("(5) harness/SKILL.md has a line naming both `build` and DEC-118 — SC-09",
          bool(hit), "no line carries both tokens")
except Exception as e:
    check("(5) harness/SKILL.md has a line naming both `build` and DEC-118 — SC-09",
          False, e)

# --- 6. the placeholder vocabulary has exactly one home ---------------------
# THE NEEDLE IS CONSTRUCTED, NEVER EMBEDDED. This file lives in the directory it
# scans, so a literal copy would take the count 1 -> 2 the moment the file landed —
# the assertion would break itself by existing. json.dumps, not repr: repr emits
# SINGLE quotes and matches 0 occurrences, while the tree carries the double-quoted
# form. Reading the constant is also what makes this check agree with D-01 by
# construction rather than by restating the definition.
try:
    needle = ", ".join(json.dumps(x) for x in harness_yaml.PLACEHOLDER_UNSET)
    hits = []
    for fn in sorted(os.listdir(BIN)):
        if fn.endswith((".py", ".sh")):
            body = read(os.path.join(BIN, fn))
            hits += [f"{fn}:{i+1}" for i, l in enumerate(body.splitlines()) if needle in l]
    tok_ok = all("PLACEHOLDER_UNSET" in read(os.path.join(BIN, f))
                 for f in ("check-state.sh", "validate-digest.py"))
    check("(6) the placeholder literal occurs exactly once across bin/, and both "
          "consumers reference PLACEHOLDER_UNSET — SC-02",
          len(hits) == 1 and tok_ok,
          f"needle={needle!r} hits={hits} consumers_reference_constant={tok_ok}")
except Exception as e:
    check("(6) the placeholder literal occurs exactly once across bin/, and both "
          "consumers reference PLACEHOLDER_UNSET — SC-02", False, e)

# --- 7. SPEC's build row agrees with build.yaml on the lead -----------------
try:
    spec_lines = read(SPEC_MD).splitlines()
    row = next((l for l in spec_lines
                if re.match(r"^\|\s*\*\*build\*\*\s*\|", l)), None)
    if row is None:
        check("(7) SPEC §13 has a `build` row whose conducted-by cell matches "
              "build.yaml's lead — SC-10", False, "no §13 row for **build**")
    else:
        conducted_by = row.split("|")[2].strip()
        check("(7) SPEC §13 has a `build` row whose conducted-by cell matches "
              "build.yaml's lead — SC-10",
              build["lead"] in conducted_by,
              f"row cell={conducted_by!r} build.yaml lead={build['lead']!r}")
except Exception as e:
    check("(7) SPEC §13 has a `build` row whose conducted-by cell matches "
          "build.yaml's lead — SC-10", False, e)

# --- 8. SC-14 — the #24 assertion, the one that makes the fix falsifiable ---
# An 8-line sliding window, anchor-free. 8 is T-11's own added-line budget for the
# passage, so the predicate says "these tokens occur inside the one passage T-11
# adds" and nothing wider. NOT a single-line predicate: at SKILL.md's ~95-col house
# style the prescribed passage renders across six lines with no line carrying all
# three, so a one-line rule would fail the plan's own text — and a later harmless
# reflow would turn the gate red with the content unchanged.
WINDOW = 8
try:
    lines = read(SKILL_MD).splitlines()
    tm = sum(1 for l in lines if "test_matrix" in l)
    windowed = any(
        all(k in "\n".join(lines[i:i + WINDOW]) for k in ("qa", "validator", "loop_back"))
        for i in range(len(lines))
    )
    check(f"(8) harness/SKILL.md names the blocking qa gate: `test_matrix` present and "
          f"qa+validator+loop_back within {WINDOW} consecutive lines — SC-14, issue #24",
          tm >= 1 and windowed,
          f"test_matrix lines={tm} windowed={windowed}")
except Exception as e:
    check(f"(8) harness/SKILL.md names the blocking qa gate: `test_matrix` present and "
          f"qa+validator+loop_back within {WINDOW} consecutive lines — SC-14, issue #24",
          False, e)

# --- 9. SC-15 — three descriptions of the panel, one set --------------------
def panel_set(row, label):
    """The panel group is the {...} group containing `∥`. Zero or several is a LOUD
    failure naming the row — a gate that guesses is what this feature exists to close."""
    groups = [g for g in re.findall(r"\{([^{}]*)\}", row) if "∥" in g]
    if len(groups) != 1:
        raise ValueError(f"{label}: expected exactly one ∥-bearing {{...}} group, "
                         f"found {len(groups)} in row: {row[:160]}")
    return {p.strip().strip("`*") for p in groups[0].split("∥")}


try:
    spec_lines = read(SPEC_MD).splitlines()
    ship_row = next(l for l in spec_lines if "**ship-feature**" in l and l.startswith("|"))
    rev_row = next(l for l in spec_lines
                   if re.search(r"\|\s*★\s*\*\*review\*\*\s*\|", l))
    a = panel_set(ship_row, "SPEC ship-feature row")
    b = panel_set(rev_row, "SPEC review row")
    c = {s["id"] for s in review["steps"]}
    check("(9) the panel set agrees across SPEC's ship-feature row, SPEC's review row "
          "and the shipped review.yaml — SC-15",
          a == b == c, f"ship={sorted(a)} review_row={sorted(b)} review.yaml={sorted(c)}")
except Exception as e:
    check("(9) the panel set agrees across SPEC's ship-feature row, SPEC's review row "
          "and the shipped review.yaml — SC-15", False, e)

# --- 10. T-01's fixtures, registered durably --------------------------------
# EMF-5's "eighth check": without this, a later edit could delete the red-first
# fixtures and every other check in this file would still pass.
try:
    tcs = read(os.path.join(BIN, "test-check-state.py"))
    n_none = tcs.count("review_sha: none")
    n_sha = tcs.count("review_sha: 1ce886a")
    check("(10) test-check-state.py still carries T-01's INV-6 fixtures "
          "(`review_sha: none` >= 2, `review_sha: 1ce886a` >= 1) — SC-01",
          n_none >= 2 and n_sha >= 1,
          f"none={n_none} sha={n_sha}")
except Exception as e:
    check("(10) test-check-state.py still carries T-01's INV-6 fixtures "
          "(`review_sha: none` >= 2, `review_sha: 1ce886a` >= 1) — SC-01", False, e)

print(f"\n{ran - fails}/{ran} checks passed." if fails == 0 else f"\n{fails} of {ran} FAILING.")
sys.exit(1 if fails else 0)
