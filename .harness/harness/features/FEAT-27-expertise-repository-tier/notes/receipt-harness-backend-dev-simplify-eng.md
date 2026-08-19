# Receipt — harness-backend-dev — REUSE angle — FEAT-27 (`b4659cd..252fa72`)

**BLUF:** One finding. `test-check-expertise.py` defines two fixture builders in the same
file that produce the identical four-section Expertise skeleton — `valid()` (line 22, the
original 8 cases) and `body_with_entry()` (line 94, the 6 new tier/advisory cases). The
second is a strict generalization of the first: `body_with_entry("WHEN a thing happens DO
the other thing.")` reproduces `valid()`'s output exactly. Flag-only, per the dispatch's hard
constraint (no assertion deletion/weakening) — this is a backlog row, not an apply.

## Finding

**File · line:** `.claude/skills/harness/bin/test-check-expertise.py:22` (`valid()`) and
`:94` (`body_with_entry()`).

**Summary:** Two functions build the same fixture shape — title line, `## Patterns (max
15)` with one `- P-01: ...` entry, then empty `## Gotchas (max 15)`, `## Outcomes (max
10)`, `## Open (max 5)` — under two names in one file. `body_with_entry(entry_text,
title=...)` differs from `valid(title=...)` only in taking the Patterns entry text as a
parameter instead of hardcoding `"WHEN a thing happens DO the other thing."`.

**Concrete cost:** If the canonical Expertise skeleton changes — a fifth section, a cap
wording change, a different Patterns-entry prefix — `check-expertise.sh`'s own title/section
rules would need both builders edited in lockstep to keep testing real files. The two are
maintained by different code (T-01's original 8 cases vs. T-03's later 6), so the second
builder going stale while the first is updated (or vice versa) is invisible: both still
compile, both still produce *some* value the checker accepts, and the suite stays green
while half of it is validating a shape `check-expertise.sh` no longer requires.

**Alternative (one line, dispatchable):** Delete `valid()`; replace its 8 call sites with
`body_with_entry("WHEN a thing happens DO the other thing.")`, keeping `body_with_entry`'s
default title.

**What would prove it safe:** `python3 .claude/skills/harness/bin/test-check-expertise.py`
exits 0 with the same case count (14 base + 20 extra) after the substitution, and a
one-line skeleton mutation (e.g. renaming `## Open (max 5)` to `## Open (max 4)` in both
builders) reddens the same set of cases it reddens today in each builder independently —
proving the merge didn't drop coverage either builder was carrying alone.

## Other surfaces checked, nothing found

- `inject-expertise.sh`'s repository-tier segment extraction/sort and `check-expertise.sh`'s
  `CRAFT_TIER_RE`/`REPO_TIER_RE` classification are purpose-built, small regexes; nothing in
  `harness_boundary.py` or a sibling script exports an equivalent tier classifier — its
  `glob_to_re`/`matches`/`classify` machinery answers a different question (manifest
  permission, not injection tier) and matching it against team-config globs would be a much
  larger surface for the same 6-line job.
- `REPO_TOKEN_RE` in `check-expertise.sh` restates `FEAT-\d+` (already covered by the
  existing `FEATURE_TOKEN_RE`), but the two serve different outcomes (blocking vs.
  advisory) on the same token — not treated as a finding; the two-language 40/150 budget
  pair (shell + Python) is explicitly settled by the dispatch as acceptable duplication.
- `test-inject-expertise.py`'s helpers (`run_hook`, `get_context`, `fresh_home`, `write`,
  `report`, `lines_body`) are genuinely new — no other `test-*.py` in the same directory
  defines matching names; nothing to reuse.
- `test-harness-yaml.py`'s `COLLECT_FIXTURE` additions are out of scope for a reuse finding
  per the dispatch (exact ordered equality, not to be touched).

**Verdict for this angle:** one finding, backlog-only.
