# SIMPLIFY / simplification angle — receipt

Scope: diff `7ebfc9e..384b800`. Read-only. No repository file edited.

## Ranked findings

### 1. [BLOCKING] Untrue decision citation introduced by the sweep — `test-no-distribution.py:72`

- **file/line:** `.claude/skills/harness/bin/test-no-distribution.py:72`
- **summary:** The comment reads `codebase map tier was retired (DEC-162, struck 2026-08-24)`.
  Both halves are false. `DEC-162` is alive (`grep -n "^## DEC-162" DECISIONS.md` → line 3774,
  "The glossary gets a checkable moment; domain-modeling is otherwise already resident") and was
  never struck. The map-tier retirement is actually recorded at **DEC-149**
  (`DECISIONS-INDEX.md:153`: *"the third, mission `deepen`, retired with the map tier"*), which is
  also alive, not struck.
- **cost:** A reader hits a FAIL in this regression guard, opens `DEC-162` expecting the map-tier
  ruling, and finds an unrelated glossary decision — the exact "citation found a green/plausible
  reference and stopped looking" failure mode `validate-digest.py:722-726` names as the thing this
  whole feature exists to prevent (`check-decision-claims.py`/`check-decision-anchors.py`, T-17/T-20).
  This file is also the guard that catches a distribution sweep taking the wrong command doors —
  its own citation is now the kind of dangling/wrong reference DEC-205 says must never survive.
- **provenance:** confirmed introduced by this diff — `git show 7ebfc9e:…test-no-distribution.py`
  had `DEC-137, struck 2026-08-24` at the same line; `DEC-137` genuinely is struck
  (`## DEC-137 — STRUCK 2026-08-24` at `DECISIONS.md:3116`), so the original citation was already a
  dead-decision pointer. The sweep silently swapped the id from 137 to 162 instead of repointing to
  the live successor (149) — this is exactly the "swap the id" move the sweep's own rule
  ("rewrite the sentence, never swap the id") forbids.
- **alternative:** `# codebase map tier was retired (DEC-149). The guard is that a` — drops the
  now-untrue "struck 2026-08-24" clause entirely (DEC-149 is not struck) and points at the entry
  that actually states the ruling.
- **why ranked first:** it is the one finding that is actually untrue in the tree today, not
  merely inelegant — an untrue comment outranks everything else per the pass's own tie-break rule,
  and it sits inside a regression-guard test this feature's sibling checkers (`check-decision-
  claims.py`, `check-decision-anchors.py`) exist specifically to catch failures of this shape.

### 2. [ADVISORY] Dead tuple slot in `build_index` — `gen-decisions-index.py:172`

- **file/line:** `.claude/skills/harness/bin/gen-decisions-index.py:172`
- **summary:** `decisions, lines, headings = parse_decisions(text)` unpacks `lines`, but nothing
  in `build_index` reads it after T-06 deleted `amendments = compute_amendments(lines, headings)`
  (the sole prior consumer). `parse_decisions` has exactly one caller (`build_index`), confirmed by
  grep, so `lines` is now purely a computed-and-discarded return slot.
- **cost:** a future reader sees `lines` bound and reasonably assumes it still does something in
  this function; tracing it to confirm it is dead costs a real read every time someone touches
  `build_index`. It is also a live footgun: `parse_decisions` still computes and returns `lines` at
  real cost (a full de-fenced-line pass) for a caller that discards it.
- **alternative:** `decisions, _, headings = parse_decisions(text)` at line 172 — one-token change,
  makes the dead slot visible instead of silently retained.

### 3. [ADVISORY] Stale docstring reference to removed extraction — `gen-decisions-index.py:94`

- **file/line:** `.claude/skills/harness/bin/gen-decisions-index.py:94`
- **summary:** `defenced_lines`'s docstring says de-fencing "must run BEFORE all extraction:
  headings, **amendments**, the reference graph, and tag scoring all see the de-fenced body." The
  amendment extraction it names (`compute_amendments`) no longer exists in this file (T-06).
- **cost:** minor — a reader learning what `defenced_lines` gates for will list "amendments" as a
  live consumer and go looking for it; it is not there.
- **alternative:** `harvested. This must run BEFORE all extraction: headings, the reference graph,` — drop "amendments,".

## Hunt 1 — six residue shapes, explicit verdict on each (`gen-decisions-index.py`)

1. **Local var/dict-key/tuple-slot/accumulator computed only for a removed branch** — **FOUND**,
   finding #2 above (`lines` in `build_index`).
2. **Helper whose caller count dropped to 1 (inline candidate) or 0 (orphan)** — **NONE.** T-06/T-10
   deleted `compute_amendments`, `format_amendment_span`, `compute_supersession_target` and their
   regexes (`AMEND_HEADING_RE`, `AMEND_BOLD_RE`, `SUPERSESSION_VERB_RE`, `BODY_SUPERSESSION_RE`)
   whole — no orphan or single-caller remnant of any of them remains (grepped the file for each
   name; zero hits post-removal).
3. **Parameter still threaded through a call chain nothing reads** — **NONE.** `compute_refs(body,
   own_num, live_nums)` — `live_nums` is the new filter added in the same diff and is read;
   `compute_tags`, `strip_trailing_clauses` parameters are all read.
4. **HEADER/docstring/help/error text still describing a removed construct** — **FOUND**, finding
   #3 above. The `HEADER` row-grammar string and the `main()` malformed-row error text were both
   correctly updated to drop `[am-span]`/`SUPERSEDED BY` (checked lines 58-74, 288); only the
   `defenced_lines` docstring was missed.
5. **Comments narrating the removal ("no longer handles X", "used to…") instead of stating present
   fact** — **NONE new.** One pre-existing "used to mean" comment survives at line 244, but it is
   about an unrelated 2026-era bug (#140, argv fallback), untouched by this diff, not a residue of
   this removal.
6. **Now-unconditional conditional / loop that can only run once / defensive branch guarding an
   unreachable state** — **NONE.** `strip_trailing_clauses`'s `while prev != cur` loop lost one of
   its two strippable clause shapes (`SUPERSEDED BY`) but the remaining `ok-stale` clause can still
   legitimately repeat (a doubled/malformed marker), so the loop is not dead machinery — left as an
   anchor per the skill's explicit carve-out, not flagged.

## Hunt 2 — truth of the swept citation comments

**Checked 27 of the ~42 sites**, selected as: every site in `.claude/skills/harness/bin/*.py`,
`.claude/skills/harness/bin/check-domain.sh`, `.github/workflows/tests.yml` whose diff line matches
`^[-+].*DEC-\d+` — **excluding** (a) `gen-decisions-index.py`'s own machinery lines, covered by
Hunt 1, and (b) synthetic `DEC-01/07/42/99` fixture literals introduced by the new T-17/T-20 test
files, which cite no real decision. For each, cross-referenced the cited `DEC-NN` against
`grep -n "^## DEC-NN\b" DECISIONS.md` for liveness and read the entry at its
`DECISIONS-INDEX.md` anchor for content match.

**All 27 checked, per-site verdicts for the ones that failed:**

- **1 FAILED**: `test-no-distribution.py:72` (`DEC-162`) — finding #1 above.
- **26 confirmed TRUE**, including every `am.N`-suffix drop sampled (`DEC-171` ×9, `DEC-138` ×4,
  `DEC-174` ×2 including the `amendment 4` form), and every full id-swap sampled (`DEC-192`→`DEC-203`
  ×6, `DEC-186`→`DEC-203` ×3 — `DEC-203`'s body explicitly states "Replaces three earlier entries,
  struck under DEC-188", and its item 6 literally reads "case sensitive, byte for byte", matching
  the swept claims verbatim; `DEC-19`→dropped entirely ×3, correct since `DEC-19` has no live
  heading and DEC-110/DEC-119 remain valid on their own).
- One site, `check-state.sh`'s `INV-24 (DEC-203)` factory/fleet citation, I could **not** fully
  confirm verbatim against `DECISIONS.md` text (no exact phrase match for "repository the fleet
  declares" under any entry I located) but it is plausible under `DEC-203`'s stated "read-back
  purpose 1: whether an item is claimed" and I found no live decision it more clearly belongs to —
  reporting this as unresolved rather than as a finding; not confident enough to rank it.
- **Grammar**: none of the 27 lost its subject or referent when the `am.N`/`amendment N` suffix was
  dropped — every parenthetical/prose form (`(DEC-171)`, `(DEC-138: …)`, `DEC-138 refuses…`) reads
  grammatically on its own.

## Skipped (out of scope / not flaggable)

- The removed supersession/amendment machinery itself, the anchoring regexes, and the
  `strip_trailing_clauses` defensive loop — settled design decisions per the dispatch's explicit
  non-goals.
- `check-state.sh`'s unresolved `INV-24 (DEC-203)` citation — noted above, not raised as a finding
  for lack of confidence, not skipped for convenience.
