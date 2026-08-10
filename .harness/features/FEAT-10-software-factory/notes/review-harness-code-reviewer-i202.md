# Review — issue #202, the check-docs strike — completeness

Reviewed `c4fea5d..835b297` (one squashed `[harness:human]` commit). Read-only; all citations taken
via `git show 835b297:<path>` / `git grep ... 835b297`, never the working tree (which is dirty from
concurrent flows and is not the pinned SHA).

## VERDICT: FAIL

**must_fix: the DEC-165 partial strike — the item this whole ticket exists to fix — was never
executed.** Severity high. One additional non-blocking finding (med) on Expertise files.

## 1. Gate-invocation sweep — CLEAN

- `git grep -n 'check-docs' 835b297 -- .github/` → **zero hits.** `.github/workflows/tests.yml`
  calls only `run-unit-tests.sh --kind integration`; its two comment mentions of a checker
  (lines 4, 69) name `check-state.sh`, not `check-docs.sh` — verified directly, correcting an
  earlier misreading on my part.
- `run-unit-tests.sh` and `deploy.sh` at the SHA — no `check-docs` reference.
- Whole-tree `git grep -n 'check-docs' 835b297`, triaged: every hit is inside a strike record
  (`DECISIONS.md`, `DECISIONS-INDEX.md`), an Expertise file (§2 below), or `.harness/features/**`
  historical artifacts. None is a live invocation.
- Ran `bash .claude/skills/harness/bin/check-state.sh` and `bash
  .claude/skills/harness/bin/run-unit-tests.sh` in a detached worktree pinned at `835b297`:
  `check-state.sh` exits 0, zero `INV-10` mentions, only informational notes belonging to unrelated
  in-flight features (FEAT-11/12, out of scope). `run-unit-tests.sh` — every test file `PASS`,
  97/97 on the integration-suite tail, no `test-check-docs.py` remnant.
- `python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff -
  docs/harness/DECISIONS-INDEX.md` → zero diff.

No dangling gate invocation anywhere. This item is fully clean.

## 2. Completeness on live surfaces

**2a. The must_fix — DEC-165's partial strike was never done.**

The ticket's own table ("DEC-165 | Created wayfinding | Strike the contradicted passage ONLY —
DECISIONS.md:4222-4226") and the "Full change list / Strike" bullet both name this explicitly, and
DEC-188's own body names it as *the trigger for the whole ruling*: "What forced it was the
mechanism's own failure mode. A change contradicted a passage in DEC-165... There was nowhere to
put the declaration." Despite that:

- `docs/harness/DECISIONS.md` at `835b297`, inside DEC-165's body (heading at line 4098), still
  carries, byte-for-byte unchanged from base, the paragraph: *"The entry test keeps the two doors
  honest: fits one conversation → `/harness-grilling`; the destination itself is fuzzy or decisions
  wait on facts and prototypes → `/harness-wayfinding`..."* — diffed directly against
  `c4fea5d:docs/harness/DECISIONS.md:4222-4226` and confirmed identical.
- `git diff c4fea5d..835b297 -- docs/harness/DECISIONS.md` has **no hunk touching DEC-165's body at
  all** (hunks jump from ~3958 to ~4005 to ~4760; nothing in the 4098-4234 range).
- `docs/harness/DECISIONS-INDEX.md` row 184 (DEC-165) is unchanged: no `STRUCK` annotation, and its
  `refs:` list does not include DEC-188 — contrast with DEC-181's row 200, which the same diff
  correctly updated with `refs: ... DEC-188` and the text "its propagation-checker half is STRUCK
  under DEC-188" for its own partial strike. (Whether the index row itself needed a matching
  annotation is my inference from that adjacent pattern, not a literal instruction in the ticket —
  flagging it as a recommendation, not a separate violation.)

**Failure scenario.** `CLAUDE.md` instructs every future agent touching a harness doc to open
`DECISIONS-INDEX.md`, find the two or three entries a change touches, and read them as authority.
DEC-188 itself points at DEC-165 as the decision it grew out of. An agent or Mike who follows that
reference to DEC-165 finds the entry standing exactly as it did before the ruling, with nothing —
no strike record, no index annotation, no cross-reference — signalling it was ever identified as
contradicted. Under the new rule, there is no propagation checker left to catch this mechanically;
the only backstop DEC-188 names is "a human reading a diff." This review is that backstop, and it
found the ruling's own named example unresolved. I am not re-opening whether the passage is *in
fact* still contradicted today (that would re-litigate the ruling) — the finding is narrower and
sufficient on its own: the ticket named this passage for a partial strike, and no edit was made to
it or to its index row.

**2b. Med, non-blocking — Expertise files still narrate the mechanism as live.**

Excluded on a first pass as "not `.harness/features/**`," but Expertise is injected into every
spawn by the `SubagentStart` hook — live instruction, not historical prose, and distinct from the
features exclusion in my dispatch. Two files, three lines:

- `.harness/expertise/harness-dev-ops.md:9` (G-01): *"check-docs.sh runs only as a subprocess of
  check-state.sh (INV-10, check-state.sh:174), and that call is guarded by
  `os.access(cd, os.X_OK)` — if check-docs.sh loses its exec bit, INV-10 silently passes instead of
  failing."* Both the invocation and the invariant number are gone; this now describes a
  vulnerability in a mechanism that no longer runs.
- `.harness/expertise/harness-documentor.md:44` (G-04): *"WHEN judging whether a file you edited or
  wrote is inside the propagation checker's scan set DO read the glob table in `check-docs.sh`..."*
  — an imperative `DO` pointing at a deleted file.
- `.harness/expertise/harness-documentor.md:48` (G-05): *"...invisible to `check-docs.sh`"* — a
  property stated relative to a mechanism that no longer exists.

**Failure scenario.** documentor spawns on a doc-touching task, follows G-04's imperative to check
`check-docs.sh`'s glob table before judging scan-set membership, and the file is gone — it either
burns a tool call discovering that and improvises, or (worse) reasons from G-04's remembered
description of the glob table as if it were still authoritative, silently reintroducing exactly the
"declares scope from memory instead of checking" failure mode this whole ticket's replacement rule
is meant to avoid at the doc layer. dev-ops's G-01 primes a similar stale mental model of a fail-open
risk that no longer applies.

Not adding to `must_fix`: FAIL is already earned by §2a, and the ticket's own verification list is
internally inconsistent about whether `.harness/` is in scope for this sweep — item 4
(`grep -rn "check-docs" . --exclude-dir=.git --exclude-dir=.harness`) explicitly excludes it, item 6
(`grep -rn "DEC-103\|DEC-104\|DEC-181" . --exclude-dir=.git`) does not. Raising as an open question
rather than ruling on the operator's behalf.

**2c. Confirmed non-findings** (checked and ruled out):

- `DECISIONS.md:4662,2938,3101,4383` — inside the evidence/amendment sections of past decisions
  (DEC-174, DEC-127/128-area, DEC-135, DEC-165's own prior amendment), narrating what a gate showed
  *at the time*. Historical, correctly left.
- `docs/harness/org.html:345` — "updated 2026-08-06 (through DEC-181)" is a generation-date marker,
  not a live-authority citation. Not a finding.
- `check-state.sh:460` and `test-check-state.py:211` — the M-01 postmortem docstring/comment,
  narrating a specific past incident that once aborted `INV-10` among others. Accurate as history
  (INV-10 existed at the time); low-value staleness only, not worth blocking on.
- `check-state.sh:856-860` — the INV-10 retirement comment is accurate, including "Do NOT reuse
  INV-10."
- `harness/SKILL.md:220` / `templates/codebase-INDEX.md:10` — `stale: <FEAT>` / `stale: FEAT-NN` is
  DEC-137's codebase-map section-staleness attribute (consumed by `render-map.py`/documentor
  ship-refresh) — a different mechanism from the struck `<!-- stale: "…" -->` marker. Confirmed
  homonym, not a finding.
- `test-render-brief.py:78`, `test-bash-write-guard.py:31`, `test-gh-sync.py:269` — reuse of
  `ok-stale`/`INV-10` strings as inert fixture data for unrelated mechanisms. Not findings.
- `gen-decisions-index.py` / `test-gen-decisions-index.py` retain `<!-- ok-stale -->` handling
  (`strip_trailing_clauses`) for a **different** consumer — an index-row-preservation escape used
  when regenerating `DECISIONS-INDEX.md`, not check-docs.sh's prose-exemption marker, though it
  reuses the string. Currently unreachable (zero live rows carry the marker): dead capability, not a
  functional bug. Stage-2 note only.
- No live `<!-- stale: "…" -->` marker syntax remains anywhere under `CLAUDE.md`, `docs/`,
  `.claude/`, `.github/`.

## 3. Dangling citations to DEC-103/104/181 — CLEAN

- `check-domain.sh:779-780` — `out.append(_head(f"CLAUDE.md is {len(lines)} lines — budget is 80
  (DEC-181)."))`. Verified at the SHA: correctly cites DEC-181's surviving budget half. **Confirmed
  correct, not flagged**, per the dispatch's own instruction.
- `check-state.sh:523` — `INV-23 CLAUDE.md is {len} lines — budget is 80 (DEC-181)` — a second,
  independent enforcement of the same preserved half. Also correct.
- `docs/harness/SPEC.md:45` — explicitly reframes: "The ruling came from DEC-104, since struck on
  other grounds under DEC-188; this half of it was never what was contradicted." Correct.
- All other DEC-103/104/181 hits are inside the strike records themselves, historical-defect
  narration, or `test-gen-decisions-index.py:132`'s comment correctly explaining why a frozen-count
  assertion was loosened after DEC-104's struck example disappeared. None is live authority.

## 4. The strike records

DEC-103, DEC-104 (`DECISIONS.md:1552`, `:1562`) and DEC-181 (`:5096`, "STRUCK IN PART") each state
clearly what was struck, when, under what (DEC-188), and — for DEC-181 — exactly which half
survives and where it is enforced. DEC-188 (`:5481`) records the new rule and states plainly that
nothing mechanical checks the striking happened. A reader who finds DEC-103/DEC-104 cited six
months out lands correctly. **DEC-165 is the exception** — see §2a.

## Stage 2 (code quality) — not blocking

Nothing beyond §2b/§2c's low-value items. Not reached in a gating sense since §2a's must_fix already
determines the verdict.

## Recommendation

Strike DEC-165's "entry test keeps the two doors honest" paragraph with a strike record (mirroring
DEC-181's partial-strike shape), and give its `DECISIONS-INDEX.md` row the same `STRUCK`/`refs:
DEC-188` treatment DEC-181's row got. Separately, sweep `.harness/expertise/harness-dev-ops.md` and
`.harness/expertise/harness-documentor.md` for the three `check-docs.sh`/`INV-10` lines — resolve
first whether Expertise is in scope for this strike at all (see open question).
