# QA re-gate — SC-13 and SC-01(c) only — BUG-1305-run-state-clobber (cycle 12, review-c2)

**VERDICT: PASS on both SC-13 and SC-01(c) at their own literal FAILS-if clauses. QA-F1/F2/F3 all
CLOSED, measured, not merely read.** One low-severity, ship-rulable, non-gating finding on an inert
conjunct inherited (not introduced) by this delta's SC-01(c) fix. No over-refusal found.

## 1. SC-13 — MET

Text graded (BRIEF `e77b30ca:.../BRIEF.md:450-467`): four route refusals, path-scoped to the witness
and not `state.yaml`/`digest.md`, both siblings' Writes asserted unaffected, green-before/red-after
on both guard scripts.

- Four routes: Bash write/removal (`test-bash-write-guard.py::run_bug1106_bash_route`,
  `:1413-1423`) + Write/Edit (`test-check-domain.py::_bug1305_identity_refusal_cases`,
  `run_bug1305_marker_cases`) — all four present and asserted `returncode == 2`.
- Path scoping: `harness_boundary.py:43`'s `RE_RUN_IDENTITY` anchored `$` on the exact marker
  filename — unchanged this delta (not in the three-file diff), re-confirmed by code read only.
- **QA-F1 CLOSED.** `test-check-domain.py:3912-3917`, case `"digest Write append remains allowed
  beside identity witness"` — the missing `digest.md` half now exists, fixture creates the witness
  first (`_bug1305_write_marker(path)`) then Writes the digest. Measured green at both `dc0e0313`
  and `e77b30ca` (§3).
- Green-before/red-after: independently replayed myself, not merely read from the note (§3).

**SC-13: MET.**

## 2. SC-01(c) — MET

Text graded (BRIEF `:293-296`): PRESENT prior U1, incoming with NO run_uid, refused both routes,
message names U1, says where it's recorded, routes a non-owning writer to a run directory of its own.

- **QA-F3 CLOSED.** `test-check-domain.py:5010-5013`: Edit half now asserts
  `returncode == 2 and "U1" in edit.stderr and "run identity" in edit.stderr and "field
  disagreement" not in edit.stderr` — byte-for-byte the same conjunct shape as its Write sibling
  (`:5006-5009`). Message source `run_identity.uid_conflict` (`run_identity.py:138-142`, unchanged
  this delta): for the missing-uid branch it names `run_uid {prior!r}` verbatim, states "the same
  value is recorded in the witness beside it" (where it's recorded), and routes the writer to "a run
  directory of its own." Wrapped by `check-domain.sh:1697-1702`'s `_head("state.yaml run identity
  (Issue 1305).")`.

**SC-01(c): MET.**

## 3. Non-vacuity — measured, both pins, verbatim

All replays below use the pinned worktrees `qa-c2-dc0` (`dc0e0313`), `qa-c2-e77` (`e77b30ca`),
`qa-c2-c369` (`c369fb1f`, the pre-fix pin the redproof note itself uses), each `git worktree add
--detach`. Every run used the SAME (current, `e77b30ca`) test file so only the guard binary varies.

**(a) Digest-sibling case (QA-F1) — permitting case, green at both pins, correctly so:**
```
CHECK_DOMAIN_BIN=qa-c2-e77/.../check-domain.sh python3 -c '...run_bug1305_digest_repair_cases()...'
→ ok "digest Write append remains allowed beside identity witness"   (5/5 passed, exit 0)
CHECK_DOMAIN_BIN=qa-c2-dc0/.../check-domain.sh python3 -c '...run_bug1305_digest_repair_cases()...'
→ ok "digest Write append remains allowed beside identity witness"   (5/5 passed, exit 0)
```
Green at both. **This is a permitting assertion (SC-01(d)/(e)-style), correctly green at both** —
the digest guard's filename scoping was never broken by this delta (only the Edit-reconstruction
path for the *witness itself* changed); the case exists to prove the composed guard leaves siblings
alone, not to catch a regression in the sibling path. Not vacuous-as-a-refusal because it never was
a refusing case.

**(b) SC-01(c) Edit strengthening — refusing case, green at both pins on the two pins compared, but
NOT vacuous — established by targeted mutation, not by both-green alone:**
```
CHECK_DOMAIN_BIN=qa-c2-e77 → ok "modal collision Edit removing uid is refused"  (10/10, exit 0)
CHECK_DOMAIN_BIN=qa-c2-dc0 → ok "modal collision Edit removing uid is refused"  (10/10, exit 0)
```
Both green because `run_identity.uid_conflict` — the mechanism this assertion exercises — is
**unchanged** in this delta; only the test's own assertion strength changed (from
cycle-1's `returncode==2 and "U1" in stderr` to the current four-conjunct form matching the Write
sibling). Both-green here does not mean vacuous: it means the underlying behavior predates this
cycle and was already correct. Confirmed non-vacuous by mutation probe in a disposable worktree
(`qa-c2-mutate`, detached at `e77b30ca`): `run_identity.uid_conflict` patched to
`return None` unconditionally (simulating the guard never firing). Replay:
```
CHECK_DOMAIN_BIN=qa-c2-mutate/.../check-domain.sh python3 -c '...run_bug1305_identity_cases()...'
→ FAIL "modal collision Write omitting uid is refused"
→ FAIL "modal collision Edit removing uid is refused"
→ FAIL "different minted uid is refused"
→ FAIL "different minted uid Edit is refused"
   (6/10 passed, exit 4)
```
The (c) Edit case reddens on the intended mutant. **Credited, measured.**

**(c) F-04 Edit-creates-witness fix (the delta's actual logic change) — independently replayed, not
trusted from `redproof-BUG-1305.md` alone:**
```
CHECK_DOMAIN_BIN=qa-c2-dc0/.../check-domain.sh (pre-fix)  python3 -c '...run_bug1305_marker_cases()...'
→ FAIL "unmatched Edit of existing witness is refused"     | exit 0
→ FAIL "Edit creating false witness is refused"            | exit 0
   (15/17 passed, exit 2)
CHECK_DOMAIN_BIN=qa-c2-e77/.../check-domain.sh (post-fix)  python3 -c '...run_bug1305_marker_cases()...'
→ ok   "unmatched Edit of existing witness is refused"
→ ok   "Edit creating false witness is refused"
   (17/17 passed, exit 0)
```
Matches `redproof-BUG-1305.md`'s own recorded numbers exactly, independently reproduced.

**(d) Bash-route witness cases (QA-F2) — independently replayed against the SAME `c369fb1f` pin the
redproof note cites, not merely re-read:**
```
BASH_WRITE_GUARD_BIN=qa-c2-c369/.../bash-write-guard.sh python3 -c '...run_bug1106_bash_route()...'
→ FAIL "overwriting the write-once identity witness is refused"  | exit 0
→ FAIL "removing the write-once identity witness is refused"     | exit 0
   (6/8 passed, exit 2)
BASH_WRITE_GUARD_BIN=qa-c2-e77/.../bash-write-guard.sh  python3 -c '...run_bug1106_bash_route()...'
→ ok   "overwriting the write-once identity witness is refused"
→ ok   "removing the write-once identity witness is refused"
   (8/8 passed, exit 0)
```
Bit-for-bit matches the note. `bash-write-guard.sh`'s diff in this delta is comment/message-wording
only (mentions issue #1376) — confirmed by direct diff, no logic change — so this red/green split is
entirely attributable to the guard version, and the note's evidence (previously QA-F2's gap) is now
present, real, and independently reproducible. **QA-F2 CLOSED.**

## 4. New over-refusal check — none found

The witness-path-first Edit branch (`check-domain.sh:2042-2044`) is gated on
`RE_RUN_IDENTITY.match(_norm(target))` — matches only the exact witness filename (unchanged
`harness_boundary.py` pattern), so it cannot reach `state.yaml`, `digest.md`, or any other path.
Measured, not just read:
- `state.yaml` Write beside witness: `"run_uid is a legal checkpoint key beside identity witness"` —
  green at `e77b30ca` (17/17 marker run, §1).
- `digest.md` Write beside witness: `"digest Write append remains allowed beside identity witness"`
  — green at both pins (§3a).
- Unrelated file, Bash route, same run directory: `"bug1106 Bash route NEGATIVE CONTROL: an
  unrelated file in the same run directory is still ALLOWED"` — green at **both** `c369fb1f` and
  `e77b30ca` (§3d transcripts above), confirming the fix added no collateral refusal on that axis.
- No dedicated Write/Edit-route "unrelated file beside witness" negative control exists in the
  suite (the closest is `:3857`'s unrelated-file-Edit control for the *digest* guard, not the
  identity witness specifically) — but the path-anchored regex makes this a code-level, not
  test-gap, guarantee. Noted, not gating (see finding F-01 below).

**No new refusal beyond the one disclosed in BRIEF REQ-07 (owner rewrite dropping `run_uid`).**

## Findings

**F-01 (severity: low, INFO-adjacent — reasoned, not measured as exploitable; ship-rulable, no code
change required).** SC-01(c) Edit's strengthened assertion (and its pre-existing Write sibling)
carries a dead conjunct: `"field disagreement" not in stderr`. Grepped the entire
`check-domain.sh` at `e77b30ca` and its full git history under `-S"field disagreement"` for this
file — the literal substring never appears in any production message, at any commit. It cannot be
tripped by any real code path, so it discriminates nothing; the actual discriminating conjunct is
`"U1" in stderr` (mutation-probe confirmed in §3b: disabling `uid_conflict` reddens the case). This
predates this delta — it was already present in the Write sibling this cycle's fix mirrored — so
cycle 11 propagated an existing weak conjunct for exact-symmetry reasons, it did not introduce it.
**Ship-rulable at ship with this finding in front of the operator; does not require code** — the
assertion as a whole is non-vacuous (mutation-proven), this is one inert clause inside it, and
removing it is a test-only edit with zero behavior implication.

**F-02 (severity: info).** No dedicated Write/Edit-route "unrelated file beside witness" negative
control exists (§4) — the guarantee currently rests on the unchanged, already-reviewed
`RE_RUN_IDENTITY` anchoring rather than a named test. Not required by SC-13's own text (which asks
only for the two named siblings, both present) — recorded for completeness, not gating.

**severity_max: low**

## Housekeeping

Disposable worktrees created for this replay, left in place per the standing worktree-removal rule
(main session's act, not mine): `qa-c2-dc0` (`dc0e0313`), `qa-c2-e77` (`e77b30ca`), `qa-c2-c369`
(`c369fb1f`), `qa-c2-mutate` (`e77b30ca`, mutated copy of `run_identity.py` for the F-01/§3b probe —
**not restored**, it is disposable and scheduled for the same removal).

`git -C .../BUG-1305-run-state-clobber status --porcelain`:
```
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/review-harness-security-reviewer-c2.md
```
(A sibling reviewer's untracked note, not mine — I wrote no file inside this checkout other than my
own note at this path, and edited nothing.)

## What my verdict does NOT license

This PASS covers only SC-13 and SC-01(c)'s own named cases, replayed with mutation- and pin-level
evidence. It does **not** license a claim that every other SC or every other route in this feature
is equally proven — I did not re-audit SC-02/04/05/06/09/10 this cycle (settled at c1, out of this
narrow re-gate's scope), and F-01's "field disagreement" observation is specific to the (b)/(c) uid-
conflict messages; it says nothing about whether other conjuncts elsewhere in the suite carry the
same inert-clause pattern.

## Addendum — SC-01(a) Edit absent-prior measurement (lead-requested)

**Lead's derivation CONFIRMED.** For `state.yaml`, an Edit whose target file is ABSENT exits 0
before the witness is ever consulted — the same F-04 mechanism class (path-blind Edit
reconstruction returning `None` on `except OSError`/`count==0`, caller doing
`if _content is None: sys.exit(0)`), one regex pattern over from the marker witness the cycle-11
fix closed. This is a genuine, currently-live gap, not a fixture artifact — probe 3 (the control)
refuses correctly, so probe 1 is not vacuous.

All three probes fired with `_bug1124_state_fixture()` + `_bug1305_write_marker(state, run_id="A")`
witness, then `_fire_digest_edit`, against `CHECK_DOMAIN_BIN` pinned per-pin. Full probe script kept
at scratch path `/tmp/probe_sc01a.py` (imports `test-check-domain.py` from `qa-c2-e77` via
`importlib`; not written inside any tracked checkout).

**Probe 1 — derivation, ABSENT prior.** `state.yaml` never created; witness records `run_id: A`;
fired `_fire_digest_edit(root, state, "run_id: A", "run_id: B")`.
```
exit=0
stderr=
```
CONFIRMED: exit 0, no refusal, no witness message at all.

**Probe 2 — same seam, `count==0` route.** `state.yaml` PRESENT and parsing (`run_id: A`), witness
agrees; fired an Edit whose `old_string` (`"NOT-PRESENT-ANYWHERE"`) does not occur in the file, so
`_edit_reconstructed_content`'s `.count(old_string) == 0 → return None` branch fires instead of the
`OSError` branch.
```
exit=0
stderr=
```
Same bypass: a SECOND door to the identical room. Any Edit whose `old_string` fails to match —
typo, stale context, wrong quoting — silently exits 0 rather than either genuinely editing or
refusing, regardless of whether the prior file exists.

**Probe 3 — control, PRESENT prior (existing suite case, unmodified).** Identical fixture and
payload to probe 1, except `state.yaml` is written first with `run_id: A`.
```
exit=2
stderr=check-domain: BLOCKED — .../state.yaml: state.yaml run identity (Issue 1305).
  run identity witness run_id is 'A', but the incoming checkpoint carries 'B'. Write this cycle's
  state into a run directory of its own.
```
Refuses correctly — this is `_bug1305_marker_foreign_refusals`'s existing "foreign Edit is refused
by witness" case, replayed verbatim. **Probe 1 is not vacuous**: the same fixture, same witness,
same payload refuses when the file is present and does not when it is absent — the only variable
is presence of the prior.

**Q1 — is the Write route genuinely closed for the same absent-prior case?** CONFIRMED closed.
Fired `_bug1124_state_fire` (Write route) with the identical absent-prior/disagreeing-witness setup
(state.yaml never created, witness `run_id: A`, incoming content `run_id: B`):
```
exit=2
stderr=check-domain: BLOCKED — .../state.yaml: state.yaml run identity (Issue 1305).
  run identity witness run_id is 'A', but the incoming checkpoint carries 'B'. Write this cycle's
  state into a run directory of its own.
```
The Write route never calls `_edit_reconstructed_content` at all — `shape_problems()`'s
`RE_STATE_YAML` branch runs directly against the incoming `content` field with no on-disk
read-and-reconstruct step, so there is no `OSError`/`count==0` fallthrough for it to fall through.
**The gap is Edit-only, not both-route.** This narrows the exposure to exactly the tool surface
REQ-01/SC-01(a) name ("Write AND Edit") — the Write half of that promise holds; only the Edit half
has the seam.

**Q2 — pre-existing or introduced by this delta?** Pre-existing, confirmed by side-by-side replay
of probes 1 and 2 at both pins:
```
                          dc0e0313 (pre-cycle-11)   e77b30ca (post-cycle-11, target)
probe 1 (absent prior)    exit=0                    exit=0
probe 2 (count==0)        exit=0                    exit=0
```
Both exit 0 at BOTH pins. Cycle-11's F-04 fix added the path-blind `RE_RUN_IDENTITY` pre-check for
the *marker witness file itself* (`check-domain.sh:2042-2044`) — it did not touch the
`RE_STATE_YAML`/`RE_RUN_DIGEST`/`RE_HANDOFF` branch's own `_edit_reconstructed_content` call or its
`None`-fallthrough, which is exactly the code this addendum's derivation is about. **This gap
predates cycle 11 and is not a regression introduced by this delta** — it is a pre-existing hole in
the ORIGINAL #1106 Edit-reconstruction design that the marker-witness fix happened to sit one
branch above, not one this delta created or worsened.

**Severity: `high` (own rating, cycle-1's F-04 precedent).** Structurally identical defect class to
cycle-1's F-04 (rated high): a silent, no-error exit-0 on the Edit route for exactly the case
REQ-01/SC-01(a) names as the one that must be caught (absent prior, disagreeing witness). The
caveat that narrows real-world exposure without eliminating the defect: the *host's own* Edit tool
(Claude Code's built-in Edit) already refuses a nonexistent `file_path` before this hook ever sees
the payload, making probe 1 dormant under normal host-mediated use — but probe 2's `count==0` route
is NOT covered by that host guard (the file exists; only the string match fails), so a stale or
mistyped `old_string` against a real, present `state.yaml` reaches this exact bypass through any
caller that is not the specific host tool assumed here (a raw hook replay, a different agent
runtime, or a future host revision). **Rulable-at-ship with this finding in front of the operator**
at cycle 12 (last authorized cycle) given: (a) the live host's own tool closes probe 1's specific
shape today, (b) the gap is proven pre-existing rather than introduced by this delta, and (c) a
correct fix is small and well-precedented (mirror cycle-11's fix: check `RE_STATE_YAML` /
`RE_RUN_DIGEST` / `RE_HANDOFF` path-and-witness-existence BEFORE calling
`_edit_reconstructed_content`, refusing on `None` rather than exiting 0, exactly as F-04 did for
`RE_RUN_IDENTITY`) — but it does require code, and does not currently have it. This is not mine to
decide to ship past; it is the operator's call, made with full visibility into both the confirmed
defect and its narrowing caveat.

`git -C .../BUG-1305-run-state-clobber status --porcelain` (same as the body of this note,
re-verified after this addendum): only my own note is newly modified; the other four untracked
files are pre-existing sibling agents' notes, none touched by me.
