# Goal-check (full, from scratch) — BUG-1305 @ `review_sha 5ed929bd`

**Ten of eleven live criteria are MET. SC-07 is NOT MET.** The cycle-13 fix is sound and the void is
closed: SC-01's (a)-Edit half — including the **omp `file_path`-only payload that binds this host** —
is now red at `1b11bc18` and green at `5ed929bd` **in-suite**, measured by me, not carried forward.
What failed is the *record*, not the protection: `notes/regression-delta-BUG-1305.md` was written
before cycle 13 and SC-07 grades that note. Every verdict below is re-derived from
`git show 5ed929bd:` plus my own replays; **no verdict is inherited from the c2 check.**

**Mode A and Mode B are each independently declarable delivered** on their own criteria (A: SC-01,
02, 03, 09, 10, 11, 13; B: SC-04, 05, 06). **The feature has not met its goal in full**, because
SC-07 — the cross-cutting no-regression criterion tagged to both modes — fails on an artifact that is
one edit from current.

## Grades — eleven live criteria (SC-08, SC-12 retired, not graded)

| SC | verdict | method | what settles it at `5ed929bd` |
|---|---|---|---|
| SC-01 | **met** | automated / integration | 21/21 marker + 10/10 identity green at pin; 5/21 and 4/10 red at `c369fb1f`. Detail below. |
| SC-02 | met | automated / integration | `test-check-state.py:4560` — dirty tree exit 1 with exactly 3 INV-36 lines (`runs/X` seed, `runs/V` uid, `runs/W` unreadable), agreeing `Y` unreported; clean tree exit 0. My replay: `RESULT True`. `check-state.sh` byte-unchanged in the delta. |
| SC-03 | met | inspection | Same case, `:4596-4598`: asserts `runs/X`,`runs/V`,`runs/W`, `'A'`,`'B'`,`'U1'`,`'U2'`, `cannot be read` present **and** `non-checkpoint top-level key` absent — the malformed/clobbered distinction the criterion names. |
| SC-04 | met | automated / integration | `run_bug1305_artifact_resolution_cases` 6/6 at pin: non-compliant refused naming the run dir, compliant passes in the same tree. Hands-off path = `validate-digest.py --hook` on SubagentStop. |
| SC-05 | met | automated / integration | 5/5 at pin: `digest Edit append repair remains allowed` exit 0 **and** `cross-run digest replacement remains refused` exit 2. Not "guard removed". |
| SC-06 | met | inspection | `check-domain.sh:1296-1298` — "This guard fires on Write and Edit: Edit content is reconstructed against the on-disk prior" — agrees with SC-05's observed routes. Caveat F-03. |
| **SC-07** | **not_met** | inspection | Direction one and direction two both fail against `notes/regression-delta-BUG-1305.md`. **F-01.** |
| SC-09 | met | automated / integration | Four pins in the one case: `Z` (checkpoint, no witness) and `L` (witness uid, checkpoint none) silent in a clean tree that contains only `Y`,`Z`,`L` (exit 0, no INV-36); `W` unreadable and `X` seed-disagreement both reported. Fifth pin: delta note `:38` records control-plane root exit 0 / 0 INV-36. |
| SC-10 | met | automated / integration | Four assertions present and green: mints 32-hex uid + matching witness, second POST byte-stable, preserves supplied uid, leaves malformed untouched. Minting **red at `c369fb1f`** in my replay. |
| SC-11 | met | inspection | `probe-notebookedit-BUG-1305.md:7` `route_reachable: no`, `:40` `guard_fires: n_a`, both column 0, each with verbatim `omp --help` + `Available Tools` output (v18.1.11, `notebook`, no `NotebookEdit`). No `## Reported` owed. |
| SC-13 | met | automated / integration | 4 route refusals green at pin; **red-proof measured by me**: check-domain side FAILs at `c369fb1f` (witness Write/Edit/unmatched-Edit/false-witness), Bash side **6/8 with both witness cases at exit 0** against a `c369fb1f` `bash-write-guard.sh`. Scoping: `case_run_identity_pattern` 6/6 rejects both siblings; `state.yaml` and `digest.md` Writes exit 0. |

## SC-01 — the three required cases, named, located, red/green

All three live in `tests/integration/test-check-domain.py` at the pin, wired into
`run_bug1305_marker_cases` via `_bug1305_edit_reconstruction_cases` (`:4823`). Red = pre-fix
`1b11bc18` bin via `CHECK_DOMAIN_BIN`; green = the pin.

1. **`absent-prior Edit refuses unverifiable witness identity`** — `_bug1305_absent_prior_edit_case`,
   `:4779`. Witness present, prior checkpoint **ABSENT** — SC-01(a)'s stated grading shape.
   **RED at `1b11bc18` (exit 0), GREEN at pin (exit 2).**
2. **`unmatched state Edit refuses unverifiable witness identity`** — `_bug1305_unmatched_edit_case`,
   `:4788`. **RED at `1b11bc18`, GREEN at pin.**
3. **`omp file-path-only state Edit fails closed`** — `_bug1305_omp_edit_cases`, `:4800`; payload is
   literally `{"tool_name":"Edit","tool_input":{"file_path":…}}`, no `old_string`/`new_string`.
   **RED at `1b11bc18` (exit 0 — the dormancy the Advisor measured), GREEN at pin.** This is the case
   that binds production traffic on this host. **It exists.**

Do-no-harm control `uniquely reconstructable state Edit remains allowed` is **green on both trees**.
No `FAILS if` leg fires: (a) present on Write (`foreign first Write is refused by witness`, red at
`c369fb1f`) and on Edit, exit 2, and the Edit half is graded on an absent prior — never on a parsing
prior carrying a `run_uid`. (b) `different minted uid` Write+Edit name U1 and U2, both red at
`c369fb1f`. (c) `modal collision Write/Edit omitting uid` both red at `c369fb1f`. (d) both recovering
cases exit 0. (e) resumed owner exit 0. (f) both halves read the message
(`Issue #1124` present / `Issue 1305` absent, and the converse). **I cite no part of the c2
reviewer's benign-`None` reasoning.**

## SC-07 — why it fails, and why the protection is nonetheless intact

The suite satisfies the *substance*. **All six signed permit pairs still exit 0 at the pin**, verified
case by case — and the dispatch's premise that every permit case is Write-route is **false**: pair 3,
`digest Edit append repair remains allowed` (`:3888-3892`), is the **Edit** route, the one case
genuinely exposed to the new fail-closed branch. It exits 0. Pairs 1, 2, 6 are Write
(`_bug1305_identity_write:5037`, `_bug1124_state_fire:3471`, `_bug1305_digest_write:3873`); pairs 4
and 5 are `check-state.sh` / `validate-digest.py`, both byte-unchanged in the delta. **No signed
permit case moved from permitted to refused.**

The *note* is stale, two ways, and SC-07 grades the note:

- **Direction one fails.** Two assertions present at `c369fb1f` — `an old_string ABSENT from the file
  is not this gate's problem (exit 0)` (`c369fb1f:3817`) and `a NON-UNIQUE old_string … (exit 0)`
  (`:3825`) — are **changed in their expected exit code, 0 → 2**, at `5ed929bd:3839,3848`. SC-07
  requires every assertion "changed in its expected exit code" to be enumerated under
  `## Removed or altered assertions`. The note's `:12` covers `test-check-domain.py` but names only
  additions and the concurrent-sweep replacement. Leg 1 of the `FAILS if` fires.
- **Direction two fails.** The cycle-13 branch (`check-domain.sh:2058-2072`, reconstruction `None` →
  exit 2 for `RE_STATE_YAML`/`RE_RUN_DIGEST`/`RE_HANDOFF`) is a refusing branch this feature adds and
  is **not paired** under `## Newly refused writes`. That section's BLUF (`:27`) — "the only
  intentional compatibility refusal is a foreign writer…" — is now **false** at the pin.

## Residuals — each still bounded exactly as ruled

Copied-`run_uid` forgery (unchanged); unmeasured end-to-end PostToolUse delivery (unchanged, disclosed
in REQ-01); the `run_uid`-dropping from-scratch rewrite (all three bounds hold); SEC-01 under #1376
(unchanged, no guard weakened). **The new one — forced-Write discipline for governed artifacts on
omp** — is real and grew silently: on this host every Edit of `state.yaml`, `digest.md` and handoff
notes now exits 2 and routes to a whole-file Write. REQ-05's outcome survives it (`digest Write append
remains allowed` exits 0, so the lead's repair route is Write-append, not Edit). It is recorded in
`STATE.md`'s ruling line but **not** in the artifact SC-07 grades — which is F-01's second half.

## Findings, each classified for routing

- **F-01 — gating, SC-07. Delta-scoped.** Remedy: in `notes/regression-delta-BUG-1305.md`, enumerate
  the two bug1106 exit-code flips under `## Removed or altered assertions` with their justification
  (fail-closed strengthening), and add the new refusal branch under `## Newly refused writes` paired
  with `uniquely reconstructable state Edit remains allowed`, naming the omp forced-Write consequence.
  No code, no test change. Arises **entirely from the `1b11bc18..5ed929bd` diff lines** and is not a
  second fix attempt on the seam — but it is a **note** edit, not literally "test-only or
  message-wording", so the tier above should confirm it qualifies for cycle 15.
  Fold in the two c2 citation-rot items in the same file (`:23` cites `run_uid is a legal checkpoint
  key`, now `… beside identity witness`; and pair 6's "same run directory" clause is better cited to
  `digest Write append remains allowed beside identity witness`).
- **F-02 — advisory, non-gating. Delta-scoped, message-wording.** The absent-prior Edit refusal does
  not name the witness's recorded `run_id`, though the witness is on disk and readable at that point.
  SC-01(a) is met — the message names the identity subject, clearing the "generic shape error" bar,
  and no `FAILS if` leg fires — but naming the recorded value would make it literally conflict-naming.
- **F-03 — advisory. Outside the delta → Advisor, does not consume cycle 15.** `check-domain.sh:1240`
  "RE_RUN_DIGEST stays out because its content comparison is PRE-only." True, and its subject is
  `SHAPE_PATTERNS` membership rather than route coverage, so SC-06 holds on `:1296-1298`. Carried from
  c1/c2 unchanged; the delta does not touch it.

## Tree state

`git -C /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1305-run-state-clobber status --porcelain`, verbatim:

```
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/research-BUG-1305-goalcheck-build-c3.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/review-harness-code-reviewer-c3.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/review-harness-qa-c3.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/review-harness-security-reviewer-c3.md
```

No tracked file is modified. The first entry is this note; the other three belong to the concurrent
cycle-14 validator panel — I neither read nor touched them. HEAD is `9cb1cb1a`, one commit past the
pin, differing only in `feature.json`; `git diff 5ed929bd -- .claude/ tests/` is empty, so every
script I executed is byte-identical to the pin. I wrote only this note and my observations log; every
replay bin was built under `/tmp`. I moved no ref and edited no code, test, `plan.yaml` or `BRIEF.md`.

## Open questions

- **Q1 (blocking SC-07 only):** F-01 is a `main-session-direct` edit to one note under DEC-174.
  Whether it consumes cycle 15 or is ruled a record-currency correction outside the cycle budget is
  the tier above's call. Until it lands, SC-07 is `not_met` and the feature cannot be declared fully
  delivered — though nothing about the protection itself is in doubt.
