# Goal-check (full) — BUG-1305-run-state-clobber @ `e77b30ca`

**The feature MET its goal: all eleven live criteria are MET at the pin.** SC-11, the single cycle-1
failure, is closed by evidence repair; the other ten were re-derived from scratch at the new pin, not
carried forward. Every verdict below rests on a `git show e77b30ca:` read plus, where the criterion is
`automated`, a replay I ran myself at the pin *and* against a pinned pre-change bin. **Mode A and Mode
B are each declarable delivered, independently.** Two advisory citation-rot findings in
`notes/regression-delta-BUG-1305.md` are recorded below; neither fires a `FAILS if` leg and neither
gates.

Replay validity: `git diff e77b30ca -- .claude/ tests/ .harness/harness.json` is empty, so the
working-tree scripts I executed are byte-identical to the pin (HEAD is `1b029f88`, one commit past).

## Grades — eleven live criteria

| SC | verdict | method (BRIEF's own line) | what settles it at `e77b30ca` |
|---|---|---|---|
| SC-01 | met | automated / integration | All eight halves present in `tests/integration/test-check-domain.py`; my replay `run_bug1305_marker_cases()+run_bug1305_identity_cases()` = 17/17 + 10/10 exit 0, and the same replay against a c369fb1f `check-domain.sh` bin = 4/17 + 4/10 with (a) Write+Edit, (b) Write+Edit, (c) Write+Edit and (f)-legacy all red. Detail below. |
| SC-02 | met | automated / integration | `test-check-state.py::case_bug1305_run_identity_invariant` (`:4560`) — dirty tree exit 1 with exactly 3 INV-36 lines (`runs/X`,`runs/V`,`runs/W`), clean tree exit 0 / no INV-36. Replayed: `RESULT True`. Red-before: `redproof-BUG-1305.md ## SC-02`. |
| SC-03 | met | inspection | `check-state.sh:1489,1496,1510` — each message carries `{_run_rel}` and the `conflict`/`uid_conflict` reason naming both values; the test asserts `'A'`,`'B'`,`'U1'`,`'U2'`,`cannot be read` present and `non-checkpoint top-level key` **absent** (`test-check-state.py:4599-4601`). |
| SC-04 | met | automated / integration | `_bug1305_relative_artifact_cases` (`test-validate-digest.py:1965`) — non-compliant refused exit 2 naming the run dir; compliant passes exit 0 in the same tree; missing digest exit 2. Replayed 6/6 exit 0. Hands-off path: `.claude/settings.json:75` registers `validate-digest.py --hook` on SubagentStop. |
| SC-05 | met | automated / integration | `run_bug1305_digest_repair_cases` — `digest Edit append repair remains allowed` exit 0 **and** `cross-run digest replacement remains refused` exit 2, both in my 5/5 replay. The allowance is not "guard removed". |
| SC-06 | met | inspection | `check-domain.sh:1296` now reads "This guard fires on Write and Edit: Edit content is reconstructed against the on-disk prior before this branch runs" — agreeing with SC-05's observed Write+Edit behaviour. No comment asserts Write-only/PRE-only of that guard. Caveat below. |
| SC-07 | met | inspection | Both directions re-derived below against `notes/regression-delta-BUG-1305.md`. |
| SC-09 | met | automated / integration | Same INV-36 case: `Z` (checkpoint, no witness) and `L` (witness uid, checkpoint none) are outside the 3 reported lines in *both* trees; `W` (unreadable) and `X` (seed disagreement) are reported. Fifth pin: the note's `## Suite results` now records the control-plane-root run — exit 0, 0 `INV-36` lines. |
| SC-10 | met | automated / integration | `POST mints uid and matching witness` (32-hex + witness equality over a payload with no uid), `second POST is byte stable`, `POST preserves supplied uid bytes` — all ok at the pin; the two minting cases are **red on c369fb1f** in my own replay. |
| **SC-11** | **met** | inspection | `probe-notebookedit-BUG-1305.md:7` `route_reachable: no` and `:40` `guard_fires: n_a`, both at column 0, each now followed by a verbatim `omp --help` invocation and its verbatim `Available Tools` output (v18.1.11, `notebook` present, no `NotebookEdit`). No `## Reported` owed: an unreachable route is not an unguarded one. |
| SC-13 | met | automated / integration | Four route refusals + scoping + green-before/red-after on **both** guard scripts. Detail below. |

SC-08 and SC-12 are retired with their struck requirements and were not graded.

## SC-01 — the eight halves, re-derived

`_bug1305_marker_foreign_refusals` (`test-check-domain.py:4767`): **(a) Write** on an ABSENT prior with
a disagreeing witness, exit 2 + `Issue 1305`; **(a) Edit** on a parsing prior carrying **no** `run_uid`
— so the forbidden shape in SC-01(a)'s `FAILS if` (a parsing prior *with* a `run_uid`) does not occur.
**(b)** `different minted uid is refused` / `different minted uid Edit is refused`, both asserting `U1`
and `U2` (`:5014-5019`). **(c)** `modal collision Write/Edit omitting uid is refused` (`:5006-5013`) —
each now asserts `U1`, `run identity`, and `"field disagreement" not in stderr`; the emitted text
(`check-domain.sh:1698-1703` + `run_identity.uid_conflict`) names U1, says the same value is recorded
in the witness beside it, and routes a foreign writer to a run directory of its own. **(d)** both
recovering cases exit 0 (`:4809-4821`), green on both trees. **(e)** `DEC-154 resumed owner …` exit 0;
`run_identity.conflict` iterates seed fields only and its comment marks `identity` forensic-only, so no
session-keyed denial exists. **(f)** `run_id disagreement keeps Issue 1124 precedence` asserts
`"Issue #1124" in` and `"Issue 1305" not in` (`:5020-5022`); `witness outranks legacy run_id ladder`
asserts the converse (`:4803-4805`). Both read the message. No `FAILS if` leg fires.

## SC-13 — re-derived, including the cycle-11 additions

Refusals: Bash write + Bash removal (`run_bug1106_bash_route`, my replay 8/8 live, **6/8 with both
witness cases at `exit 0`** against a c369fb1f `bash-write-guard.sh` bin); Write, Edit, and now
`unmatched Edit` and `Edit creating false witness` of the witness (`_bug1305_marker_file_protection`,
`:4838`). **Non-vacuity of the two new Edit cases, measured by me:** against a `dc0e0313`
`check-domain.sh` bin, `unmatched Edit of existing witness is refused` and `Edit creating false witness
is refused` both **FAIL at exit 0**, 15/17 — the F-04 hole was live and is now closed by path
(`check-domain.sh:2039-2042` keys `RE_RUN_IDENTITY` ahead of Edit reconstruction). Scoping: the
sibling `state.yaml` Write (`run_uid is a legal checkpoint key beside identity witness`) and the
`digest.md` Write (`digest Write append remains allowed beside identity witness`) are both exit 0 and
both **genuinely composed** — I instantiated `_feat50_digest_fixture()` + `_bug1305_write_marker()` and
the directory listing is `['.run-identity.json', 'digest.md']`, so a directory-scoped denial would
redden them. `RE_RUN_IDENTITY` matches the witness and rejects both siblings
(`test-harness-boundary.py:552`, replayed 6/6 PASS).

## SC-07 — both directions at the new pin

**Direction one.** `git diff c369fb1f e77b30ca -- tests/` deletes 84 lines; reading them, the only
substantive removals remain the three the note enumerates (timing-sensitive concurrent-sweep proof,
the `DEC-156 … fails OPEN` case, the `validate-digest.py:check_artifact_file` complexity exception).
Cycle 11 deleted no assertion: its three test deletions are a strengthened `(c)` Edit assertion, a
case rename, and a reordering. `## Removed or altered assertions` covers all three removals.

**Direction two — the six pairs against the suite at the pin.** (1) `legacy checkpoint without uid
remains allowed` exit 0. (2) `DEC-154 resumed owner …` + both SC-01(d) cases, exit 0. (3) `digest Edit
append repair remains allowed` exit 0. (4) `check-state.sh` clean tree containing witness-less `Z`,
exit 0. (5) `located compliant digest passes` and `unresolvable artifact lookup still fails open`, both
exit 0. (6) `state.yaml` Write, `digest.md` Write and the Bash `notes.txt` negative control, all exit
0. `## Removed or altered assertions`, `## Newly refused writes` and `## Suite results` are all
present; `## Suite results` records unit exit 0 / 28 files / 0 `FAIL` and integration exit 0 / 46 files
/ 0 `FAIL`. The one disclosed new refusal (dropped `run_uid`) is stated with the test that pins its
message. No leg of the `FAILS if` fires.

## Mode statements — kept separate

- **Mode A (run-state clobber: prevention + detection) IS delivered.** Prevention: SC-01 (all eight
  halves, six of them red pre-change), SC-10 (minting), SC-13 (the witness the detection reads cannot
  be destroyed by any governed write route). Detection: SC-02, SC-03 (actionable, distinct from the
  malformed-shape finding), SC-09 (self-limiting, nothing historical reddens). SC-11 — the last open
  question about a fourth write route — is now answered with command-produced evidence: the route does
  not exist on this host.
- **Mode B (durable digest graded and repairable) IS delivered.** SC-04 (automatic grading via the
  registered SubagentStop hook), SC-05 (repair permitted, cross-run replacement still refused),
  SC-06 (the guard's own record is true). None of its evidence depends on Mode A's.

## Findings — advisory, non-gating, remedies for the main session (DEC-174)

- **A-01 (citation rot, `notes/regression-delta-BUG-1305.md`, `## Removed or altered assertions`,
  last bullet).** It cites `run_bug1305_marker_cases` — `run_uid is a legal checkpoint key`; cycle 11
  renamed that case to `run_uid is a legal checkpoint key beside identity witness`. **Remedy:** in that
  bullet, replace the quoted case name with `run_uid is a legal checkpoint key beside identity
  witness`. No test or code change.
- **A-02 (weaker-than-available citation, same bullet).** For SC-07 pair 6's "in the same run
  directory" clause the note cites `digest Write append remains allowed`, whose fixture carries no
  witness; the composed case `digest Write append remains allowed beside identity witness` added at
  cycle 11 is the one that actually shows the clause. **Remedy:** add that case name beside the
  existing one in the same bullet. The pair itself is satisfied by the suite, which is why this is
  advisory.
- **A-03 (SC-06 caveat, recorded not graded — unchanged from cycle 1).** `check-domain.sh:1240` still
  reads "RE_RUN_DIGEST stays out because its content comparison is PRE-only." Its subject is the
  pattern's exclusion from the POST sweep and the statement is true; it asserts nothing about tool
  routes, so SC-06's operative clause holds. Flagged only because the phrasing echoes the false
  comment REQ-06 removed.

## Residuals — each still bounded exactly as ruled, none widened

- **Copied `run_uid`.** `run_identity.uid_conflict` returns `None` when incoming equals prior, and
  INV-36 compares witness against checkpoint — a forger agreeing with both is invisible. Unchanged.
- **Unmeasured end-to-end PostToolUse delivery.** SC-10's evidence is a direct `--post` invocation over
  an isolated bin root; nothing at the pin observes host delivery. Unchanged, disclosed in REQ-01.
- **The newly-refused `run_uid`-dropping from-scratch rewrite.** All three signed bounds hold: the
  message names the line to carry forward and where it is recorded; POST re-injects the field; the seed
  doctrine is in the tree. Unchanged.
- **SEC-01 / issue #1376 — directory-level `rm`/`mv`.** Now *narrower in claim, not wider in exposure*:
  the BRIEF records it as an accepted residual under REQ-02, and `bash-write-guard.sh:788-802` states
  it in both the docstring and the deny message. No guard was weakened to accommodate it.
- **`unreadable witness fails closed`** (`check-domain.sh` fail-closed branch) remains the one refusal
  beyond the disclosed set — narrow (fires only when the prior carries no readable `run_uid` **and** the
  witness will not parse), consistent with the BRIEF's fail-closed doctrine, and covered by no
  criterion. Raised again so it is seen rather than discovered.

## Tree state

`git -C <worktree> status --porcelain`, verbatim:

```
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/review-harness-security-reviewer-c2.md
```

That file is the concurrent Advisor-scoped panel's, not mine; I did not read or touch it. I wrote only
this note and my observations log. Every replay wrote to `/tmp` only; I moved no ref and edited no
production file, test, `plan.yaml` or `BRIEF.md`.

## Open questions

- **Q1 (non-blocking):** A-01 and A-02 are one-file citation edits in `notes/regression-delta-BUG-1305.md`,
  both `main-session-direct` under DEC-174 and neither gating any criterion. Whether to spend the
  cycle-12 budget on them, or ship as-is and record them, is the operator's call.
