# Goal-check — BUG-1305-run-state-clobber @ `dc0e0313`

**The feature did NOT fully meet its goal: ten of eleven graded criteria are MET; SC-11 is NOT MET.**
Mode A (run-state clobbering) and Mode B (durable-digest grading and repair) are both delivered on
their own criteria. The single failure is an *evidence* defect in one probe note, not a code defect:
`notes/probe-notebookedit-BUG-1305.md` records its two answers with no command and no output beside
them, which is the exact leg SC-11's `FAILS if` names. No production file, test, plan or brief needs
to change to remedy it. Every verdict below was re-derived from the assertion or the file at the pin
(`git show dc0e0313:`), not carried forward from qa.

## Grades

| SC | verdict | method (BRIEF's own line) | evidence at `dc0e0313` |
|---|---|---|---|
| SC-01 | met | `verify: automated  evidence: integration` | `tests/integration/test-check-domain.py`. All eight halves by name, below. |
| SC-02 | met | `verify: automated  evidence: integration` | `test-check-state.py::case_bug1305_run_identity_invariant` — dirty tree run `V` (witness `U1`, checkpoint `U2`) reported, run `Y` (`SAME`/`SAME`) silent; `code == 1` on the dirty tree, `clean_code == 0` on the tree holding only agreeing/legacy runs. Red-before: `redproof-BUG-1305.md ## SC-02` (pinned checker reported only `run_uid` as an unknown key). |
| SC-03 | met | `verify: inspection` | `check-state.sh:1495-1514` — the INV-36 text carries `{_run_rel}` (the run directory) and, via `run_identity.conflict` / `uid_conflict`, both disagreeing values (`'A'`/`'B'`, `'U1'`/`'U2'`; asserted by the test's `joined` membership check). It does **not** reuse `non-checkpoint top-level key`; the test explicitly asserts that wording is absent from the INV-36 lines. |
| SC-04 | met | `verify: automated  evidence: integration` | `test-validate-digest.py::_bug1305_relative_artifact_cases` — `existing run directory without digest is refused` asserts exit 2 mentioning the run dir and `missing`; `located compliant digest passes` exit 0 in the same tree. Red-before: `redproof ## SC-04` (old hook exit 0). |
| SC-05 | met | `verify: automated  evidence: integration` | `test-check-domain.py::run_bug1305_digest_repair_cases` — `digest Edit append repair remains allowed` exit 0 **and** `cross-run digest replacement remains refused` exit 2. Both halves; the allowance is not "guard removed". Red-before: `redproof ## SC-05`. |
| SC-06 | met | `verify: inspection` | `check-domain.sh:1295-1298` now reads "This guard fires on Write and Edit: Edit content is reconstructed against the on-disk prior before this branch runs." The false `intentionally Write/PRE-only` comment present at `c369fb1f:1237` is gone. Agrees with SC-05's test, which observes the guard acting on both routes. Caveat below. |
| SC-07 | met | `verify: inspection` | `notes/regression-delta-BUG-1305.md`. Both directions re-derived below. |
| SC-09 | met | `verify: automated  evidence: integration` | `case_bug1305_run_identity_invariant` fixtures `Z` (checkpoint, no witness → silent, tree exit 0), `L` (witness uid, checkpoint none → silent), `W` (unreadable witness → reported), `X` (seed-field disagreement → reported); fifth pin recorded in `regression-delta` `## Suite results` (`check-state.sh` exit 0, no INV-36/run-identity finding). |
| SC-10 | met | `verify: automated  evidence: integration` | `_bug1305_marker_post_mint_cases` / `_bug1305_marker_post_preservation_cases` — (1)+(2) `POST mints uid and matching witness` asserts `re.fullmatch(r"[0-9a-f]{32}", uid)` **and** `marker_doc["run_uid"] == uid` over a payload with no `run_uid`; (3) `second POST is byte stable`; (4) `POST preserves supplied uid bytes`. Red-before: `redproof ## SC-10` (both minting cases FAIL on `c369fb1f`). |
| **SC-11** | **not_met** | `verify: inspection` | Finding below. |
| SC-13 | met | `verify: automated  evidence: integration` | Four route refusals + scoping, below. |
| SC-08 | retired | — | Retired with struck REQ-08: grammar unification was frequency-only and its supersession mechanics contradicted DEC-205. Not graded. |
| SC-12 | retired | — | Retired with struck T-12: its probe runs under the MAIN checkout's hook, so `post_mint_observed: no` was guaranteed by construction and would have published a false claim. Not graded. |

## SC-01 — the eight halves, each by name

Read from `tests/integration/test-check-domain.py` at the pin.

- **(a) Write** `_bug1305_marker_foreign_refusals` → `foreign first Write is refused by witness`, exit 2 + `Issue 1305`. Prior is **absent** (`_bug1124_state_fixture` creates only the directory), witness disagrees on `run_id`. Red on `c369fb1f` (`redproof ## SC-10`).
- **(a) Edit** same function → `foreign Edit is refused by witness`, exit 2 + `Issue 1305`. Red on `c369fb1f`. Its prior is present-but-legacy rather than absent; no `FAILS if` leg fires (the forbidden shape is *a parsing prior carrying a `run_uid`*), and it is the criterion's own "wherever the checkpoint's own identity is unavailable" case.
- **(b) Write** `different minted uid is refused` — `rc==2 and "U1" and "U2" in stderr`. Red on pinned (`redproof ## SC-01-identity`).
- **(b) Edit** `different minted uid Edit is refused` — same assertion via `_bug1305_identity_edit("run_uid: U2\n")`. Red on pinned, confirmed by the cycle-10 re-gate (6/10, exit 4, this case named in the red set). This is the half cycle 1 found missing.
- **(c) Write** `modal collision Write omitting uid is refused` — `rc==2`, names `U1`, `"field disagreement" not in stderr`. Message (`run_identity.uid_conflict`) names U1, says the same value is recorded in the witness beside it, and routes the writer to a run directory of its own. Red on pinned.
- **(c) Edit** `modal collision Edit removing uid is refused` — `rc==2`, names `U1`. Red on pinned.
- **(d) two cases** `recovering owner with absent checkpoint remains allowed` and `... with zero-byte checkpoint remains allowed`, both `rc==0` with a witness present. Green on both trees.
- **(e)** `DEC-154 resumed owner with same uid remains allowed across sessions` — `rc==0` with `session_id="S2"`. Green on both trees; no session-keyed denial exists (`run_identity.conflict` iterates only `run_id/feature/squad/host`, and its docstring forbids consuming `identity`).
- **(f) two cases** `run_id disagreement keeps Issue 1124 precedence` (asserts `"Issue #1124" in stderr and "Issue 1305" not in stderr`) and `witness outranks legacy run_id ladder` (asserts `"Issue 1305" in stderr and "Issue 1124" not in stderr`). Both read the message, not the exit code alone.

Advisory, non-gating: SC-01's preamble asks every refusing case to be red on the pinned copy, while its
`FAILS if` requires red only for (b) and (c). (f)'s Issue-1124 half is green on both trees *by
construction* — the pre-existing 1124 branch answers first, which is the deferral the case exists to
prove. The `FAILS if` clause is what governs; no leg fires.

## SC-13 — four refusals, scoping, and the pre-change proof

- Bash write and Bash removal: `test-bash-write-guard.py:1413-1422`, `rc==2` + `identity witness`.
- Write and Edit of an existing witness, plus creation of a false one: `_bug1305_marker_file_protection`, all `rc==2` + `identity witness`.
- Scoping: `test-harness-boundary.py::case_run_identity_pattern` asserts `RE_RUN_IDENTITY` matches the witness and **rejects** the sibling `runs/r1/state.yaml` and `runs/r1/digest.md`; `run_uid is a legal checkpoint key` lands a `state.yaml` Write at exit 0 in the witness-bearing directory; the Bash negative control (`notes.txt`, same directory) stays exit 0. The `digest.md`-at-exit-0 Write lives in `run_bug1305_digest_repair_cases`' own fixture rather than the witness directory — present and exit 0, so no `FAILS if` leg fires.
- Pre-change proof, **both** guard scripts. check-domain: `redproof ## SC-10` (three witness refusals FAIL on `c369fb1f`). bash-write-guard: the redproof note does **not** cover it, so I replayed it against the committed pinned fixture `tests/integration/fixtures/prior-bash-write-guard.sh.fixture` via the suite's own `bug1304_pre_change_guard` helper — `overwrite exit 0`, `remove exit 0` on the pinned guard; `exit 2` with `identity witness` live. Green-before/red-after holds.

## SC-07 — both directions

**Direction one.** `git diff c369fb1f dc0e0313 -- tests/` is +5299/-86 over 17 files; I read every
deleted line. The only substantive removals are the three the note enumerates: the timing-sensitive
concurrent-sweep proof in `test-check-domain.py` (replaced by a FIFO-gated proof of the same
observable contract), the `DEC-156 … fails OPEN` case in `test-validate-digest.py` (the deliberate
fail-open → fail-closed change), and the `validate-digest.py:check_artifact_file` complexity
allowlist exception (a tightening). The one deletion that looked like a weakened aggregate —
`- and ok_i33` in `test-check-state.py::main` — is a rewrite to `and ok_bug1305 and ok_i33`;
`ok_i33` is retained. Nothing removed or weakened is unenumerated.

**Direction two — the six pairs, compared one by one against the suite at the pin.** (1) legacy both
sides → `legacy checkpoint without uid remains allowed`, exit 0. (2) resumed owner → `DEC-154 resumed
owner …` exit 0, plus both SC-01(d) recovering cases exit 0. (3) `digest Edit append repair remains
allowed`, exit 0. (4) `check-state.sh` over legacy witness-less directories → `clean_code == 0` with
run `Z` in the tree. (5) `located compliant digest passes` exit 0 and `unresolvable artifact lookup
still fails open` exit 0. (6) `run_uid is a legal checkpoint key` exit 0, `digest Write append remains
allowed` exit 0, `bug1106 Bash route NEGATIVE CONTROL … notes.txt` exit 0. `## Removed or altered
assertions`, `## Newly refused writes` and `## Suite results` are all present; suite results record
exit 0 / 0 `FAIL` for both kinds and `check-state.sh` exit 0 with no INV-36. Neither BLUF claims a
lost refusal.

## THE FINDING — SC-11, not met

`git show dc0e0313:.harness/harness/features/BUG-1305-run-state-clobber/notes/probe-notebookedit-BUG-1305.md`
is nine lines. `route_reachable: no` and `guard_fires: n_a` are at column 0 — but **neither carries a
command or an output**. The `## Observation` section is prose asserting that the host exposes no
`NotebookEdit` tool. SC-11's `FAILS if` fires literally ("if a recorded answer has no command and
output beside it"), and the BRIEF's criteria preamble forbids exactly this shape: "settled by the
state of the repository and a command anyone can run — never by an agent's report of it". T-11's own
`intent:` demanded "record `route_reachable: no` and `guard_fires: n_a` **with the verbatim
refusal**"; its `verify:` is two greps for the two lines, which cannot see the missing evidence.

**Exact remedy (no code, no test, no criterion change).** A main-session-direct edit to that one note,
adding beside each line either (i) the `NotebookEdit` call actually issued against
`/tmp/bug1305-probe/state.yaml` and the host's verbatim refusal text, or (ii) if the tool genuinely is
absent from the inventory, the verbatim invocation that enumerates the host tool inventory together
with its verbatim output showing no `NotebookEdit` entry. No `## Reported` section is owed: the
recorded answer is an *unreachable* route, not an unguarded reachable one — so nothing is carried to
the operator as an open defect on that axis.

## Mode separation

- **Mode A** rests on SC-01, SC-02, SC-03, SC-10, SC-11, SC-13 (REQ-01/02/03 → T-01, T-02, T-03, T-09).
- **Mode B** rests on SC-04, SC-05, SC-06 (REQ-04/05/06 → T-05, T-06).
- **SC-07** spans both, in both directions.

**Mode B is delivered: every criterion it depends on is met, and none of them touches Mode A's
evidence.** Mode A is delivered in mechanism — prevention, minting, detection, witness protection and
detection shape all met — but **cannot be declared delivered while SC-11 stands unmet**, because SC-11
is the one criterion that answers whether a fourth write route reaches `state.yaml` unguarded. The
two modes are therefore separable exactly as the flow's acceptance criterion requires: Mode B is
declarable done with Mode A short of one criterion.

## Residuals — each still bounded as signed

- **Copied `run_uid`.** `run_identity.uid_conflict` returns `None` when incoming equals prior, and
  INV-36 compares witness against checkpoint — a forger that copies the field agrees with both. Bound
  unchanged: undetectable by construction, deliberate forgery, not the accidental slug reuse #1305
  records. Nothing at the pin widens it.
- **End-to-end PostToolUse delivery.** SC-10's evidence is `fire_post` invoking `check-domain.sh --post`
  directly over an isolated bin root; nothing at the pin observes host delivery. Bound unchanged and
  disclosed in REQ-01.
- **The newly-refused `run_uid`-dropping rewrite.** All three signed bounds hold: the message names the
  line to carry forward and where it is recorded (`run_identity.uid_conflict`'s no-uid branch); POST
  re-injects it after every governed landing (`inject_uid`); and the seed doctrine is in the tree
  (`.claude/skills/harness-team/SKILL.md:56-57` — "a lead never invents, edits, or drops it").

**One new refusal beyond the disclosed set — advisory, covered by no criterion.** A write into a run
directory whose witness JSON is corrupt is refused (`unreadable witness fails closed`,
`check-domain.sh:1636-1641`) where `c369fb1f` permitted it. It is narrow — it fires only when the prior
checkpoint has no readable `run_uid` **and** the witness will not parse — and it follows the same
fail-closed doctrine the BRIEF endorses for an unreadable prior. It is not a criterion failure; it is
raised so the operator sees it rather than discovers it.

**SC-06 caveat, recorded not graded.** `check-domain.sh:1240` still reads "RE_RUN_DIGEST stays out
because its content comparison is PRE-only." Its subject is the pattern's exclusion from
`SHAPE_PATTERNS`/the POST sweep, and the statement is TRUE (a post-write comparison of the file with
itself cannot fire). It asserts nothing about tool routes, so SC-06's operative clause — the carried
description agrees with the routes SC-05 observes — holds. Flagged because the phrase reads like the
false comment REQ-06 removed.

## Tree state

`git -C <worktree> status --porcelain`, verbatim:

```
 M .harness/harness/features/BUG-1305-run-state-clobber/observations/harness-pm.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/research-BUG-1305-goalcheck-build-c1.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/review-harness-qa-c1.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/review-harness-security-reviewer-c1.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/review-harness-ui-reviewer-c1.md
```

Mine are the first two lines only. The three `review-*` notes are the concurrent adversarial panel's,
landing in the same worktree while I graded; they are not mine and I did not read them. I edited no
production file, no test, no `plan.yaml` and no `BRIEF.md`; the one replay I ran wrote only to
`$TMPDIR`. `HEAD` is `929d4144` ("pin review_sha at the review seam commit"), one commit past the pin;
every graded read was `git show dc0e0313:`.

## Open questions

- **Q1 (blocking the ship decision):** SC-11 is unmet on evidence, and the remedy is a one-file note
  edit — but the cycle budget is exhausted at 9/9 with both Advisor extensions spent. Authorizing the
  remedy needs an operator or Advisor ruling that nobody in this stage can grant. Ship-with-SC-11-unmet
  is also available to the operator: the substantive answer (route unreachable on this host) is
  plausible and no code change depends on it.
