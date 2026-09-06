# Code Review — BUG-1308 expertise-replace-drop — cycle 4 (DELTA, final)

Pin graded: `b70d57b464743034231fed3d18227a17faae2ed4`. Every source/test/doc file cited was read via
`git show b70d57b4:<path>`, never the worktree copy. Reproductions ran against files extracted from
the pin into a scratch `git worktree add` off a throwaway clone (`/tmp/bug1308_pinned_wt`, `HEAD ==
b70d57b4` confirmed) — never against this feature worktree. `harness-code-reviewer` is read-only via
bash for any write pattern (confirmed: `>` and `rm` both blocked even against `/tmp`); no source,
test, doc, or plan file in this worktree was touched.

## VERDICT: PASS — no must_fix, one low advisory, four pre-existing grade-2 test functions (unchanged)

## Stage 1 — REQ verdict table (file:line at the pin)

| REQ | Status | Evidence |
|---|---|---|
| REQ-01 replace | Delivered | `_rebuild_section` (`:334-348`), `cmd_ops` (`:549-598`). My own repro: 15-entry Patterns at cap, `replace P-07` → exit 0, `REPLACED P-07`, re-parsed count 15, 7th entry is `P-07` with new text. |
| REQ-02 drop | Delivered | Same `_rebuild_section`. `case_removal`/case12 (executed): drop exits 0, id absent, neighbours intact, checker still OK. |
| REQ-03 caps preserved | **Delivered — re-executed, not read** | `_check_caps` (`:375-382`), run once on final merged state. My own repro: replace-at-cap-15 stays 15 (exit 0); a second proposal combining that replace with an `add` correctly exits 8 `CAP EXCEEDED section=Patterns cap=15 union_size=16`, file byte-identical before/after. |
| REQ-04 missing target | Delivered | `_resolve_replace_or_drop` (`:269-278`), exit 10. `case_missing_target`/case13 green. |
| REQ-05 ambiguous target | Delivered | `_check_base_ambiguity` (`:258-266`), `_check_proposal_ambiguity` (`:305-316`), exit 11. `case_ambiguous_target`/case14 green (both sub-cases). |
| REQ-06 atomic refusal | Delivered | Every forced refusal above (cap, missing, ambiguous, malformed) left sha256 unchanged; `harness_merge.locked_update` computes the whole transform before any write. |
| REQ-07(a) add-only unchanged | **Delivered, re-executed** | `git diff origin/main..b70d57b4 -- expertise-merge.py \| grep -c '^-[^-]'` → **0**; `--stat` shows `333 insertions(+), 0 deletions` — every pre-existing line, including `compute_union`/`cmd_apply`/`CAPS`, is byte-identical. |
| REQ-07(b) concurrency (SC-11) | **Delivered, actually run** | Full integration suite executed at the pin: `case_concurrent_writers`/case18 — "neither child exits during the 2.0s hold window ... (**2.03s observed**)", both children exit 0 after release, census = original 8 + P-09/P-10, P-07 carries the replace text. This is a real subprocess/timing test, not a mock — a non-locking child would fail it. |
| REQ-08 contract/mechanism agree | Delivered | `case_contract_drift`/case17 green: real SKILL.md passes; all 3 deliberately-drifted copies fail in the direction the drift predicts (verified in my own run, not read from the diff). |
| REQ-09 regression coverage | Delivered | case11/12/13/14/15/19 (+u11/u12) all present, all green, at the pin. |

No scope leakage in the c3→c4 delta (`5942e34e..b70d57b4`, `+1222/-10` across 14 files): the ONE
source change is `_validate_target_grammar` (16 lines, additive) plus its single call site in
`_validate_target_section`; the SPEC.md change is exactly 8 ops-side citation corrections plus the
enriched exit-12 row (apply-side drift deliberately left alone, per the commit message and the
already-known-accepted item); everything else is process bookkeeping (feature.json pin/cycle bump,
receipts, observations). All of it traces to VL-06's close-out and its documentation — no REQ/DEC
asked for anything absent from this shape.

## VL-01..VL-06 — each re-executed, not inferred from the diff

- **VL-01 (newline injection in `entry`)**: CLOSED. `case21`/`case22`/`u17`/`u18` enumerate the full
  `str.splitlines()` break alphabet (`\n \r \v \f \x1c \x1d \x1e \x85 U+2028 U+2029`) for both `entry`
  and `target`; every one refuses at 12 MALFORMED OPS, file sha256 unchanged — all PASS, run live.
- **VL-02 (non-string `target` → uncaught `TypeError`)**: CLOSED. `case23`: exits 12 not 1, no
  traceback in combined output — PASS, run live.
- **VL-03 (`add` resolved against last occurrence on duplicated base)**: CLOSED. `case24`(a)/(b):
  both duplicate-occurrence shapes now refuse AMBIGUOUS TARGET(11) for `add` too — PASS, run live.
- **VL-04 (two test functions at grade 1)**: CLOSED. `code-grade.py` over the whole feature range
  (`merge-base(origin/main,b70d57b4)..b70d57b4`) reports **PASSING: 84, zero grade-1, zero
  high/critical** — I ran this myself (see Stage 2).
- **VL-05 (`_reject_multiline` narrow-alphabet divergence)**: CLOSED, still. `_reject_multiline`
  checks `len(value.splitlines()) > 1` (shares `parse_expertise`'s exact alphabet); the same
  case21/22/u17/18 runs above are its regression proof, still green.
- **VL-06 (target grammar unvalidated)**: **CLOSED, re-executed exactly as specced.** Ran `case25`/
  `case26` live at the pin:
  - `add target="PPPP-1"` → exit **12**, `MALFORMED OPS ... does not match the entry id grammar`,
    sha256 unchanged; re-parsed via the tool's own `parse_expertise`, Gotchas holds **1** entry (no
    forged addition).
  - `add target="P-01: fake prefix"` → exit **12**, sha256 unchanged; re-parsed Patterns holds
    **exactly one** `P-01`.
  - A well-formed `add target="P-02"` still exits **0** (case26, positive control).
  - A following **legitimate `replace` of `P-01` exits 0, not 11** — the pre-fix lockout is gone.
  All four assertions observed PASS in my own execution of the pinned suite, matching the acceptance
  criteria verbatim.

## Grammar check attacked on its own terms — each answered by execution

- **(a) whitespace**: `_validate_target_grammar(" P-01")` and `("P-01 ")` both **refuse**, code 12 —
  the anchored `^...$` grammar has no room for surrounding whitespace. No bypass.
- **(b) `target` valid, `entry` text starts with a different valid id** (`target=P-02`,
  `entry="G-01: text starting with a different valid id"`): exits **0**. `entry` carries **no**
  grammar obligation — only `_reject_multiline`'s single-line rule applies to it. Re-parsed via
  `parse_expertise`: `P-02`'s text is the full opaque string, no forged header/entry, `check-
  expertise.sh` still exits 0. No divergence.
- **(c) Unicode digits**: Python's `\d` (no `re.ASCII`) matches Unicode `Nd`. `target="P-١"` (U+0661)
  and `"P-１"` (U+FF11) **both pass** the grammar check. Added live via the CLI: round-trips exactly
  through `parse_expertise` (`('P-١', ...)` intact) **and** `check-expertise.sh` exits 0 OK on the
  result — because the checker's own `ENTRY_RE` uses the same `\d`, so the two tools agree; no cap
  bypass, no parser-invisible data, no duplicate id. **Low/advisory** (see Findings) — this is a
  visual-confusability concern (`P-01` vs `P-١` are distinct-but-similar), not a gate defeat.
- **(d) valid target colliding with an id in a DIFFERENT section**: `add target="P-01"
  section="Gotchas"` while Patterns already holds `P-01` → exits **0**, producing `P-01` in both
  sections; `check-expertise.sh` still exits 0. This is *exactly* the already-known, already-
  backlogged gap ("no shipped gate binds Expertise id uniqueness across sections") — confirmed by
  execution, not escalated; severity unchanged from what was already known.

None of (a)-(d) gates the caps, plants parser-invisible data, or produces a NEW duplicate-id
lockout beyond the already-accepted cross-section gap.

## Stage 2 — code quality, c3→c4 delta only

No fail-open found in the 16-line delta. `_validate_target_grammar` runs unconditionally for every
verb (`_parse_op` → `_validate_target_section` → `_validate_target_grammar`, before any resolution
step), and it runs **after** `_reject_multiline`, so a target that could confuse `$`/`.` semantics is
already excluded by the wider check first — correct order, confirmed by reading the call sequence.
Docstring matches code exactly (verified the "PPPP-1 fails to match at all; P-01: fake prefix
captures P-01 != target" claims against live execution above).

**Code-grade, delta only** (`5942e34e..b70d57b4`): `_validate_target_grammar` grade 5 (bar 4); 5 new
test functions grade 3-5 (bar 3). **PASSING: 6, zero FAIL.**

**Code-grade, whole feature range** (`merge-base(origin/main,b70d57b4)=4b0d04e9..b70d57b4`, the range
`validate-digest.py` independently recomputes): **PASSING: 84**, plus **4 pre-existing GRADE:2 test
functions** (`case_missing_target` L505, `case_ambiguous_target` L537, `case_contract_drift` L740,
`case_multi_op_composition` L925 — all `BAR:3 RESULT:FAIL`, none `SEVERITY` high/critical, zero
grade-1). Confirmed via `git diff 5942e34e..b70d57b4` that **none of these four are touched** by this
cycle's delta — they are the identical four c2 first reported and reasoned (F4), reconfirmed
unchanged in c3. Reasons (unchanged from c2/c3, restated per protocol):
- `case_missing_target`/`case_ambiguous_target`: cyclomatic 1, cognitive 0 — ABC-driven only, an
  assertion-heavy single-scenario test in this suite's established idiom (many `check()` calls, no
  branching); splitting would fragment one logical scenario with no natural seam.
- `case_contract_drift`: SC-09 itself specifies three drifted copies asserting two directions each —
  the complexity is required by the signed acceptance criterion, not an accidental design choice.
- `case_multi_op_composition`: SC-12 specifies asserting the identical result under reversed op order
  plus a second two-drop shape in one function — same reasoning.
`code_grade: grade_2` for the whole range (never `fail` — no gated record below a production bar, no
grade-1 anywhere); does not gate this review.

## Docs — SPEC §5.3 / DEC-219 / DECISIONS-INDEX, read against the shipped code

- SPEC §5.3's exit-12 row now names the grammar check and cites `_validate_target_grammar,
  expertise-merge.py:191-203` — **verified accurate against the pin**, along with all 7 other citation
  edits in this commit (`_validate_target_section:206-219`, `_rebuild_section:334-348`,
  `_resolve_all:319-331`, `_check_caps:375-382`, `cmd_ops:549-598`, `MISSING TARGET:269-278`,
  `AMBIGUOUS TARGET:258-266 + :305-316`, `MALFORMED OPS:153-250 + :403-406`) — every line range
  checked directly against `git show b70d57b4:.../expertise-merge.py`, all correct.
- **Grammar binds all three verbs**: confirmed — `_parse_op` calls `_validate_target_section` (which
  calls `_validate_target_grammar`) unconditionally, before the verb-specific `_validate_entry_and_
  keys` branch. `add`, `replace`, and `drop` all pass through the same gate.
- The pre-existing apply-side citation drift (`compute_union`, `cmd_apply`, dead `acquire_lock`) is
  confirmed still present and untouched, exactly as the commit message states and exactly the
  already-known-accepted backlog item — not re-raised.
- DEC-219 (`DECISIONS.md:6901`) does not itemize the grammar check by name, but its own `Record:`
  line defers mechanism detail to SPEC §5.3, which does carry it — not drift, by the project's own
  convention.
- `DECISIONS-INDEX.md:219` carries the literal substring `replace and drop through the ops
  subcommand` (SC-10) — confirmed by direct read. `test-gen-decisions-index.py` run live at the pin:
  **14/14 `ok`**, exit 0, including `test_committed_index_matches_a_fresh_regeneration`.

## Verification run (this session, at the pin — read via a scratch `git worktree`, this feature
worktree untouched)

- `python3 tests/unit/test-expertise-ops.py` @ pin: 0 FAIL, ends `PASS test-expertise-ops.py`.
- `python3 tests/integration/test-expertise-merge.py` @ pin: 0 FAIL, ends `PASS test-expertise-merge.py`
  (all 26 cases, including case18's real 2.03s lock-hold and case25/26's VL-06 exploits).
- `python3 tests/integration/test-gen-decisions-index.py` @ pin: 14/14 ok, exit 0.
- In this worktree (HEAD `ac6c9c5b` = `b70d57b4` + a feature.json pin-bump only, diff-confirmed):
  `env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind unit`: **0
  `^FAIL `**, 28 files. `--kind integration`: **0 `^FAIL `**, 46 files, 86.86s. (The unit-kind file
  count differing from earlier cycles' reported 74 is the already-known, already-accepted
  caller-dependent discovery-count variance — not re-raised.)
- `code-grade.py` both ranges as reported above.

## Findings

- **[low, chore]** Non-ASCII decimal digits (`\d`'s Unicode-aware default) are accepted in a
  `target`'s numeric position and round-trip consistently through both `expertise-merge.py` and
  `check-expertise.sh` — not a gate defeat, but a homoglyph id (`P-01` vs `P-١`) is a real, if
  unlikely, source of human confusion during manual reconciliation. Advisory only; no consumer
  observed to rely on ASCII-only ids today.
- No must_fix. All six VL items and all nine REQs hold under fresh execution at the pin.

## `git status --porcelain` (this feature worktree; proves I changed nothing but this note)

```
 M .harness/harness/features/BUG-1308-expertise-replace-drop/observations/harness-pm.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/research-BUG-1308-expertise-replace-drop-goalcheck-sc-c4.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/review-harness-qa-c4.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/review-harness-ui-reviewer-c4.md
```
All four are concurrent sibling-agent output (pm/qa/ui-reviewer, same c4 panel), written before or
during this session by other agents — none are mine. I wrote no source, test, plan, BRIEF, STATE, or
feature.json anywhere in this worktree.

## Open questions

None blocking.
