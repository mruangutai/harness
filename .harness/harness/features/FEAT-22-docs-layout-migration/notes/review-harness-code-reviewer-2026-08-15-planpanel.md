# Plan-quality review — FEAT-22 r7 — code-reviewer panel seat

Pin: `0f12f14` (= `main` HEAD, confirmed via `git rev-parse HEAD`). No diff exists — this is a
plan review. Read-only on source throughout.

## BLUF

One must-fix: **`.harness/notes/audit-decisions.py` is a live reader the plan schedules nowhere.**
Everything else checked clean, with the census attached. One advisory (non-gating) DEC-189 gap.

---

## Hunt 1 — the survivor partition

**Independent reproduction, both spellings, matches the plan's 196/35/161 split exactly.**

```
git grep -lE 'docs/harness|"docs", ?"harness"' -- .   -> 196 files
git grep -lE 'docs/harness'                    -- .   -> 191 files
git grep -lE '"docs", ?"harness"'              -- .   ->  15 files
git grep -clE 'docs["/ ,]{1,4}harness'         -- .   -> 196 files (broader adds nothing)
```

Partitioned by prefix, independently:

| Partition | My count | Plan's count | Agree? |
|---|---|---|---|
| `.harness/harness/**` | 158 | 158 | agree — survivor |
| `.harness/logs/**` | 3 | 3 | agree — survivor |
| `.claude/**` | 22 | 22 | agree — per-file audit |
| `.harness/notes/**` | 7 | 7 | **see below** |
| `.harness/expertise/**` | 2 | 2 | agree — per-file audit |
| `docs/harness/**` | 3 | 3 | agree — moves with files |
| `CLAUDE.md` | 1 | 1 | agree — instruction-side |
| **Total** | **196** | **196** | |

The 22 `.claude` files: T-03 (3) + T-04 (6) + T-05 (5) + T-06's five `.claude` files (5) = 19
touched, plus `layout_fixtures.py`, `layout_migration.py`, `test-check-state.py` (3) declared
knowing survivors by name in T-05's intent and T-10's table. 19 + 3 = 22 — reconciles exactly.

**RESOLVER sweep (part b), literal-free, method used:**
- `grep -lE '__file__|\.\./\.\./|"\.\."'` over all `bin/*.py`, then manually walked every hit
  outside the already-named files for hard-coded depth, module-scope `open()`, or a glob whose
  empty result reads clean.
- `factory_config.py`'s `_BIN_DIR` climb (`os.path.join(_BIN_DIR, "..", "..", "..", "..")`,
  `harness_root()`) climbs from `bin/` to repo root — a FIXED count independent of docs depth (it
  never touches the docs segment count), so it is not a docs-depth dependency. Confirmed by
  reading; not a finding.
- `git grep -l 'SPEC\.md' -- .` minus files already carrying `docs/harness` literal surfaces two
  live-instruction hits: `.claude/skills/harness-team/SKILL.md:14` and
  `.claude/skills/harness/teams/review.yaml:38`. Both cite `SPEC.md` **by bare filename with a
  line number, no path segment at all** — they do not resolve a path themselves, they presume the
  reader already knows the location from elsewhere (CLAUDE.md's table, which this plan updates).
  Not a LIVE hit under the stated definition (no path resolution, no path-bearing instruction).
  Recorded here per P-15 rather than silently dropped.
- Same check repeated for `DECISIONS.md`, `DECISIONS-INDEX.md`, `BUILD.md`, `org.html` across
  `.claude`, `CLAUDE.md`, `.harness/expertise`, `.harness/team-config.yaml`, `.harness/harness.json`
  — zero hits without the `docs/harness` literal already present. `harness.json:74`'s `"docs"` key
  is a `test_matrix` change-type name, unrelated to any path.
- `glob.glob` scan over `bin/*.py` for docs-related globs: only hit is
  `layout_migration.py:176`, the detector's own already-migrated evidence marker — in scope, not
  edited by this feature, correctly so (it's the detector itself).
- `.claude/agents/*.md`: no file references `SPEC.md`, `DECISIONS.md` or `docs/harness`.
- `team-config.yaml` carries no `docs/harness` literal at all (confirmed, exit 1 on grep) — its
  `docs/**` line (`:117`) is the pre-existing product-checkout grant T-02 explicitly keeps
  alongside the new wildcard entry. No discrepancy.

**One MUST-FIX found by the repo-wide sweep outside `bin/`, `.claude`, `CLAUDE.md`,
`.harness/expertise`:**

```
find . -name "*.py" -o -name "*.sh" | grep -v .claude/skills/harness/bin \
  | xargs grep -lE 'docs/harness|SPEC\.md|DECISIONS\.md'
  -> ./.harness/notes/audit-decisions.py
```

### LIVE-MISSING: `.harness/notes/audit-decisions.py`

- The BRIEF's own partition table (`BRIEF.md:70`) classifies this file explicitly: *"7 per-file
  audit (6 dated grillings/handoffs are survivors; `audit-decisions.py` is live)"* — the plan's
  own signed disposition, not my judgment call.
- `audit-decisions.py:15-16`:
  ```
  D = pathlib.Path("docs/harness/DECISIONS.md").read_text(encoding="utf-8")
  I = pathlib.Path("docs/harness/DECISIONS-INDEX.md").read_text(encoding="utf-8")
  ```
  Module-scope, hard-coded relative-path reads. After the move these paths no longer exist;
  running the script raises `FileNotFoundError` at import/first line — loudly, not silently.
- It is a real, used tool, not dead code: `.harness/logs/2026-08-03.md:10` records an actual
  decisions-conflict audit run with this exact script as the "reproducer", output committed at
  `.harness/notes/audit-decisions-conflicts-2026-08-03.md:3`.
- **No task in plan.yaml schedules it.** `grep -n 'audit-decisions' plan.yaml` → no match. It
  appears in `notes/research-FEAT-22-docs-boundary.md` only (the BRIEF's own source), never
  carried into a task's `files:` list or `intent:`.
- **The gate that should catch this doesn't.** T-10's per-file live-surface table
  (plan.yaml `:1088-1096`) is scoped to exactly `.claude`, `CLAUDE.md`, `.harness/expertise` — it
  never reaches `.harness/notes`. T-10's `survivors:` count (`:1084-1087`) is a bare arithmetic
  equality between the note's stated figure and a fresh tree-wide grep excluding only this
  feature's own directory — it has no per-class check, so it will silently count
  `audit-decisions.py` as one more "knowing survivor" alongside the six dated grillings it sits
  beside, and the whole task goes green. The runtime failure is loud; the plan's own sweep of it
  is silent.

**No SURVIVOR-WRONGLY-SCHEDULED found.** Every file in every task's `files:` list (T-02 through
T-09) is either live `bin/*.py`/`*.sh` code, live instruction prose (`CLAUDE.md`,
`SKILL.md`, `templates/plan.yaml`), an always-injected Expertise file, or `DECISIONS.md` receiving
an append-only amendment — none is a shipped feature record or a dated log entry. Checked against
every task's `files:` block; none touches `.harness/harness/features/<other-FEAT>/**` or
`.harness/logs/**`.

---

## Hunt 3 — the detector's docs rows

Detector rows, read at `layout_migration.py:93-101` (anchors confirmed, unchanged from the
dispatch's citation):

```python
Row("docs", "…factory_config.py",
    r'os\.path\.join\("docs", "harness"',                                  # legacy
    r'os\.path\.join\("\.harness", [^,)]+, "docs"'),                       # migrated
Row("docs", "…gen-decisions-index.py",
    r'os\.path\.join\("docs", "harness"|docs/harness/',                    # legacy
    r'os\.path\.join\("\.harness", [^,)]+, "docs"|\.harness/[^/ ]+/docs/'),# migrated
Row("docs", "…harness_boundary.py",
    r"docs/harness/\*\*",                                                  # legacy
    r'\.harness/[^/"]+/docs/\*\*'),                                        # migrated
```

**T-03's `verify:` migrated-match assertions (plan.yaml `:355-360`) are byte-identical strings to
the detector's own `migrated` regex for all three rows** — diffed side by side, character for
character, no divergence. This is the opposite of the dispatch's cautioned gap: for T-03
specifically, the verify IS the detector's regex, not a lookalike.

Per-row answers:

1. **factory_config.py** — prescribed `os.path.join(".harness", "harness", "docs", "SPEC.md")`
   matches migrated `os\.path\.join\("\.harness", [^,)]+, "docs"` (`[^,)]+` = `"harness"`).
   Does NOT match legacy (first arg is `".harness"`, not `"docs"`). Clean.
2. **harness_boundary.py** — prescribed entry `.harness/*/docs/**` matches migrated
   `\.harness/[^/"]+/docs/\*\*`: the bare `*` character satisfies `[^/"]+` (one char, not `/` or
   `"`). Does NOT match legacy `docs/harness/\*\*` (no such substring). Clean.
3. **gen-decisions-index.py** — prescribed `DOCS_DIR = os.path.join(".harness", "harness",
   "docs")` matches migrated alt 1; the rewritten HEADER (`.harness/harness/docs/DECISIONS.md`)
   matches migrated alt 2. Neither matches legacy alt 1 or alt 2 (no `"docs", "harness"` comma
   pair, no `docs/harness/` substring).

**Both-match (MIXED) risk, checked directly rather than inferred:** T-03's absence check
(`grep -qE 'docs/harness|"docs", ?"harness"'`) is a strict superset of every row's `legacy`
pattern for these three files (each row's legacy regex requires the same substring or a narrower
one). I independently re-ran the enumeration T-03's intent claims (rather than trust the research
note's transcription):

```
factory_config.py:       11, 13, 32          (plan says 11, 13, 32 — exact match)
gen-decisions-index.py:  2, 5, 10, 20, 76    (plan says 2, 5, 10, 20, 76 — exact match)
harness_boundary.py:     84, 90, 111, 143, 151, 221, 315   (plan says the same 7 — exact match)
```
All 15 sites are named and addressed by T-03's intent. If T-03 lands as specified, zero legacy
substring survives in any of the three files, so neither row can read MIXED. CLEAN — migrated is
the only reachable verdict for all three.

**The gen-decisions-index "both spellings" row (`layout_migration.py:34`):** confirmed this
describes why the row's legacy/migrated patterns each carry two alternatives (the `DOCS_DIR`
join-form and the HEADER slash-form) — not a requirement that both simultaneously hold post-move.
Post-T-03 both alternatives happen to be independently satisfied (DOCS_DIR via alt 1, HEADER via
alt 2), which is stronger than the row requires (OR, not AND). No gap.

---

## Hunt 4 — specified text vs builder improvisation

**T-08 (DEC-189 amendment).** Read `docs/harness/DECISIONS.md:5549-5608` at the pin. T-08's
prescribed content is accurate everywhere it makes a claim against source:
- Four named paths, first is `docs/harness/**` (`:5567`) — confirmed.
- Worked example `<harness>/docs/harness/guide.md` (`:5576`) — confirmed, quoted correctly.
- Redundancy reasoning (`is_control_plane_glob` short-circuit, the `applicable_globs`
  comprehension) — matches `harness_boundary.py:339-343` as the plan states.

Heading is pinned exactly apart from date; body is a bounded "what it must say, and no more" list
— low latitude, and every item it does specify checks out.

**One accuracy gap in what T-08 scopes to say — advisory, not a T-08 latitude problem.**
DEC-189's ORIGINAL ruling text, `:5583-5585`, carries a claim in the same shape as the one T-03 is
required to strip from `harness_boundary.py:221` ("MUST NOT SURVIVE IN ANY SPELLING") and that
T-05 forbids reappearing in `test-check-domain.py:785-788`: *"`team-config.yaml` grants `docs/**`
and contains no `docs/harness/**` entry anywhere. A glob-keyed classifier would have nothing to
match two of the four named paths against."* Literally, the substring `docs/harness/**` stays
absent from team-config.yaml even after T-02 (T-02 adds a *different* string,
`.harness/*/docs/**`) — so the sentence isn't falsified word-for-word. But its INFERENCE goes
stale the moment the amendment respells the named path: team-config.yaml now *does* carry a
matching glob for that one path, so "nothing to match two of the four... against" is no longer an
accurate count once the reader also has the amendment in view. T-08's "what it must say, and no
more" list does not include this clause, and T-08 explicitly forbids touching the original ruling
text (append-only, per the operator's Q2b). The result: the same claim-shape the plan treats as
mandatory to correct in code and in tests is left standing, unflagged, in the decision authority
itself — precisely the risk CLAUDE.md names ("nothing detects a falsified statement left standing,
so the striking has to actually happen"). **Advisory, med, non-gating** per the hunt's own
calibration (this is amendment scope, not builder latitude — T-08's specified text, followed
exactly, still produces this gap). Remedy is one added clause in T-08's amendment body noting the
inference no longer holds; no edit to the original ruling text is implied or recommended.

**T-07 (Expertise edits).** All 5 hits across the two files are pure present-tense path claims —
`harness-backend-dev.md:73` (a glob example in a gotcha) and `harness-documentor.md:7,31,43,59`
(all cite `docs/harness/DECISIONS.md` or `DECISIONS-INDEX.md` as a location, nothing more). None
asserts anything beyond location that goes false — the harder "weaken or delete" branch T-07's
intent describes never actually fires for either file. Builder latitude here is low-risk by
inspection, not merely by the operator's blanket Q2 confirmation.

One adjacent, non-gating observation: `harness-documentor.md:57-58` (G-04) lists live surfaces to
sweep when striking a decision as "CLAUDE.md, docs/, .claude/{skills,commands,agents},
.harness/expertise" — the bare `docs/` doesn't carry the `docs/harness` literal so T-07's grep
won't touch it, and it isn't strictly false post-move (`docs/PRINCIPLES.md` still lives there), but
it no longer names where the harness's own decisions/SPEC docs live. Info-level; not raised as a
finding since nothing breaks and no requirement scopes it.

---

## Scope fences respected

Did not re-raise: briefing backlog Q6-Q8, #369's heredoc mechanism, the two-segment fixture
(B-1, declined), FEAT-21's filed set, r7's signature/Q2/MF-4. Did not touch hunt 2 (test-suite
sweep) or hunt 5 (verify runnability) — qa's lane.
