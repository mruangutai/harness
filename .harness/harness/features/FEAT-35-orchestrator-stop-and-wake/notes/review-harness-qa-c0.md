# QA gate — FEAT-35-orchestrator-stop-and-wake — c0

review_sha `e0ae67152` (worktree HEAD matches exactly). Base `df18fe52e`. Pre-change sha for
failure demonstrations `569d417`.

## BLUF

Suite green (21/21 unit scripts, `test-orchestrator-playbook.py` genuinely runs and its 8 named
cases genuinely discriminate — verified failing 9/9 sub-assertions against a real `569d417`
extract). But `matrix_ok: false`: T-01/T-02/T-03 are `change_type: ai_behavior`, the matrix
requires `eval` for that type, and `test_kinds.eval.cmd` is `null` (`status: unresolved`) — that
is **misconfigured, not not-applicable, and never a pass**. No orchestrator-sequenced qa segment
ran during build either, so this gate-only pass is the only matrix enforcement this feature gets,
and it cannot satisfy the floor. VERDICT: BLOCKED — the missing runner is a standing dev-ops gap
the BRIEF itself scopes out ("a markdown playbook cannot be executed by any runner... a standing
dev-ops gap worth a backlog row, not something this feature closes"), not a defect in this diff,
so BLOCKED rather than FAIL.

## Phase 1 (pre-code) expected coverage, from BRIEF alone

- Playbook text asserts no stay-alive language and does carry the never-wait rule (SC-01) — needs
  a lexical/regression test since the artifact is markdown.
- Playbook's wake step names the context meter and threshold, and never pairs the threshold with
  refusal language (SC-02).
- The self-id mechanism actually works from inside a real agent turn (SC-03) — inspection only,
  not mine to run in a gate-only pass (reviewer's job per BRIEF).
- No refused `feature.json` write remains; `status:` replaces `phase:` (SC-04).
- A real long-running feature phase shows no 600s kill and no stay-alive Bash (SC-05) — uat,
  outside this gate.
- Loop coherence across steps 3–7 (SC-06) — inspection, not mine.
- DEC-201 recorded and indexed (SC-07).
- BRIEF's own "Verification gaps" section pre-declares that `eval` is a soft skip for the three
  `ai_behavior` tasks and that nothing in this repo can execute a markdown playbook — so Phase 1
  already expects the matrix requirement to resolve to a non-pass state, carried instead by SC-01/
  02/04/06 (unit+inspection) and SC-05 (uat). That is the one Phase-1-vs-Phase-2 gap worth
  flagging explicitly: **the matrix's own floor (`eval`) cannot be met by design**, and the BRIEF
  is honest about it rather than silently substituting.

## Matrix enforcement (Phase 2)

| task | change_type | required kinds | state |
|---|---|---|---|
| T-01, T-02, T-03 | `ai_behavior` | `eval` (always) | **misconfigured → BLOCKED** — `test_kinds.eval.cmd: null`, `status: unresolved` (`.harness/harness.json`, confirmed at `e0ae67152`) |
| T-04 | `docs` | none (`always: []`) | n/a |
| T-05 | `logic` | `unit` (always) | **satisfied** — `test-orchestrator-playbook.py` registered in `UNIT_SCRIPTS` (diff confirmed, one basename added) and ran for real |

`matrix_ok: false`. Not a soft skip reported as green — `eval` genuinely required by 3/5 tasks,
genuinely unsatisfiable with the current tooling. Per the digest contract this forces
`VERDICT != PASS`; per the state table, a null `cmd` is `misconfigured → BLOCKED`, never `FAIL`.

## `run-unit-tests.sh --kind unit` at the pin — real run, not a self-report

Exit 0. 21/21 scripts `PASS`, including `PASS test-orchestrator-playbook.py` — verified live, not
assumed. That script's own output shows all 8 named cases (`case1`..`case8`, with `case6` split
into two sub-checks) printing `PASS` against the current `SKILL.md`.

Demonstrated the required pre-change failure independently: extracted `569d417`'s `SKILL.md` via
`git show`, pointed `PLAYBOOK_PATH` at it, ran the script directly — **exit 1, all 9 named
sub-assertions FAIL**, each with a legible detail line (e.g. `found the retired literal 'Receive
the team digest'`). This matches the plan's own required demonstration and I reproduced it
independently rather than trusting the receipt.

Also independently confirmed at `e0ae67152`: SC-01 (`Receive the team digest`: 0 occurrences,
`Loop until DONE`: 0, `NEVER WAIT FOR A LEAD`: 1), SC-04 (`Record your phase in`: 0 occurrences),
SC-07 (`gen-decisions-index.py --stdout` diffs clean against `DECISIONS-INDEX.md`, and
`DEC-201` row present).

## Adequacy — what does this suite actually bind, and what could regress under it green

The suite is **eight literal-string presence/absence checks over the file's raw text**, run
against a live `SKILL.md`. It binds only the exact retired/new phrases named in the plan. It
proves nothing about whether an orchestrator actually behaves per the rewritten loop — the BRIEF
says this outright (a markdown playbook cannot be executed). Concretely, all of the following would
land with this suite still fully green:

- A regression that reintroduces stay-alive behaviour under **different wording** — e.g. "Poll the
  child every 30 seconds until it reports" or "Hold this turn open until the digest arrives" —
  passes cases 1/2/3 because none of the retired/required literals changed.
  This is the same shape #804 already ticketed for `case6` in this same file; it recurs across
  every case here since all eight are pure string matches, not structural or semantic checks.
- Case 6 (`context_warn_tokens` never paired with a refusal word) is **same-line scoped**: a wrap
  that puts "...over the threshold, the orchestrator is BLOCKED from continuing." on the line
  *after* the one naming `orchestrator_context_warn_tokens` goes undetected. New instance of the
  #804 shape, worth flagging per the dispatch's invitation (case 6 specifically, not previously
  ticketed for this file).
- Cases 4/5/8 are pure presence checks with no context-scoping: `context-watch.py` or
  `orchestrator_context_warn_tokens` or `Record your status in` could appear anywhere in the file
  — a stray comment, a deleted-and-relocated mention, or text that says the opposite of what's
  intended ("we no longer call context-watch.py") — and still satisfy the assertion.
- Cases 1/2/7 (absence checks) miss any reintroduction of the refused behaviour phrased even
  slightly differently — e.g. `Record your phase into feature.json` (different preposition) would
  not trip case 7.

None of this is a defect in the diff under review — the tests do exactly what the plan specified,
and the plan itself is honest that lexical matching is the ceiling available for a markdown
artifact. It is a floor-of-the-floor limitation the matrix's `eval` requirement was meant to raise
above, and can't, because `test_kinds.eval.cmd` is null repo-wide.

## What each of the eight assertions would MISS (task 4, explicit)

1. `case1` (absence "Receive the team digest") — misses reworded stay-alive language.
2. `case2` (absence "Loop until DONE") — misses reworded wait-loop language.
3. `case3` (presence "NEVER WAIT FOR A LEAD") — misses the phrase appearing decoratively (e.g.
   inside a quoted counter-example) without being the operative instruction; no context-scoping.
4. `case4` (presence "context-watch.py") — misses a mention that isn't actually wired into the
   decision step; no scoping to "this is invoked in the wake-time context check."
5. `case5` (presence "orchestrator_context_warn_tokens") — same shape as case4.
6. `case6` (two sub-checks) — same-line-scoped refusal-pairing check; a next-line refusal
   statement is invisible to it (#804-shape, new instance for this file).
7. `case7` (absence "Record your phase in") — misses a differently-worded reintroduction of the
   refused write.
8. `case8` (presence "Record your status in") — misses the phrase appearing without being followed
   by the correct field/target; no content-scoping past the literal string.

## Cited, not re-filed

#803 (DEC-NN id collision), #804 (case-6-shape line scoping — reproduced here as a new instance in
this file, not previously ticketed for `test-orchestrator-playbook.py`), #805 (`done` write has no
commit-path owner). The six INV-26 board-lag violations are accepted, not findings.

## SC evidence

| SC | test |
|---|---|
| SC-01 | `.claude/skills/harness/bin/test-orchestrator-playbook.py` cases 1–3, run via `run-unit-tests.sh --kind unit`; independently re-verified via `grep -c` against `git show e0ae67152:...SKILL.md` |
| SC-02 | same script, cases 4–6 |
| SC-03 | not mine — `verify: inspection`, reviewer's note |
| SC-04 | same script, cases 7–8; independently re-verified via `grep -c` |
| SC-05 | not mine — `verify: uat`, out of gate scope |
| SC-06 | not mine — `verify: inspection`, reviewer's note |
| SC-07 | independently re-run: `gen-decisions-index.py --stdout \| diff - DECISIONS-INDEX.md` clean, `DEC-201` row present |
