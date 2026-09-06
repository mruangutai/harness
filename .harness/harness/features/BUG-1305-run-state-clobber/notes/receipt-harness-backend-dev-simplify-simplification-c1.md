# SIMPLIFICATION angle + risk grading — BUG-1305, cycle 1

## BLUF

Reachability question: **both compares ARE reachable and neither is dead code** — proven by
execution, not inference (below). One real simplification finding in `check-state.sh`'s new
INV-36 block (APPLY candidate). Part 2: no grade regression in the three named production
files' changed functions; `uid_conflict` (new, `run_identity.py:123`) fails the production
bar at grade 3; `main()` in `tests/integration/test-check-domain.py` genuinely worsened
grade 2→1 from this diff's added case calls.

## Part 1 — SIMPLIFICATION

### The two-compare reachability question — ANSWERED: both reachable, neither dead

`check-domain.sh`'s `state.yaml` route (~1603–1707) gates the witness compare on
`prior_has_uid` (line 1628) and the minted-uid ladder (`uid_conflict`, line 1695) is reached
only past `if prior_state:` — the two are mutually exclusive **by design** (D-01), never both
live for one input, but each is independently reachable for a *different* input shape:

| prior state | witness compare (1635–1650) | ladder `uid_conflict` (1695) |
|---|---|---|
| absent (`prior_state == ""`) | fires (only check; `if prior_state:` false, ladder never entered) | unreachable |
| zero-byte (reads as `""`) | fires (same as absent) | unreachable |
| unparseable, non-empty | fires; **if no conflict, falls through** to ladder's own `does not parse` refusal (line 1653) — a *second*, independently reachable refusal | reached only if witness raised nothing (see proof) |
| parses, no `run_uid` (legacy) | fires | reached, but `uid_conflict` silently returns `None` (no `run_uid` to compare) |
| parses, `run_uid` equal | **skipped** (`prior_has_uid` true) | reached, returns `None` (equal) |
| parses, `run_uid` differs | **skipped** | reached, refuses |

Executed proof, not inference:
1. Existing committed fixtures already exercise both fire points and both PASS when run
   directly (`python3 tests/integration/test-check-domain.py 2>&1 | grep bug1305`, 28/28):
   `"witness outranks an unparseable prior"`, `"witness outranks legacy run_id ladder"`
   (witness fires), `"different minted uid is refused"`, `"run_id disagreement keeps Issue
   #1124 precedence"` (ladder fires).
2. I additionally built the untested cell — unparseable prior **and a witness that agrees**
   (no conflict) — a synthetic payload via `/tmp/bug1305_reach_probe.py` (kept in `/tmp`,
   nothing written to the tree): result `returncode=2`, message is the ladder's
   `"run state already exists but does not parse"`, and `"Issue 1305"` is **absent** —
   confirming the witness compare ran, found no conflict, and control fell through to the
   ladder's independent parse-error branch. This is the case the existing suite does not
   cover and it is the one that proves the two branches are truly separate code, not one
   shadowing the other.

**Verdict: no defect.** This is the valuable negative result — retire the question.

### Finding — redundant conjunct masks an unguarded consumer (`check-state.sh:1502–1514`)

```
_wuid = _marker.get("run_uid") if isinstance(_marker, dict) else None
_suid = sdoc.get("run_uid")
if (_wuid is not None and str(_wuid).strip()
        and _suid is not None and str(_suid).strip()
        and str(_wuid) != str(_suid)):
    _uid_reason = run_identity.uid_conflict({"run_uid": _wuid}, {"run_uid": _suid})
    bad.append(f"... disagrees ...: {_uid_reason}. ...")
```

- **Cost**: `bad.append` is unconditional — it is never gated on `_uid_reason` being
  truthy. Its only guard is the caller's own re-derivation of exactly what `uid_conflict`
  already checks internally (both non-empty, unequal). This works today only because the
  outer `if` happens to guarantee the *one* branch of `uid_conflict` that returns non-`None`.
  Two independent statements of the same precondition (the `if`, and `uid_conflict`'s own
  early-returns) must be kept in lockstep purely so an unchecked `.append()` stays safe.
- **Alternative**: shrink the guard to what the caller actually needs — `if isinstance(_marker, dict):` — call `uid_conflict` unconditionally, and gate the append on `if _uid_reason:`. This asserts the guard's own intent explicitly instead of leaning on a duplicated precondition, and removes the need to keep the `if`'s three conjuncts synced with `uid_conflict`'s internal branching.
- **Breakage risk**: a future edit that "simplifies" the outer `if` (e.g., drops the
  `str(_wuid) != str(_suid)` conjunct believing `uid_conflict` already checks it — which it
  does) would leave `bad.append` executing unconditionally with `_uid_reason` possibly `None`,
  emitting a bogus INV-36 line (`"...: None. The checkpoint..."`) for the exact case the
  adjacent comment says must stay silent (a witness uid with no live checkpoint uid yet,
  D-13's documented race).
- **Label: APPLY candidate.** This adds an explicit check (`if _uid_reason:`) rather than
  removing or weakening any assertion — the INV-36 finding text and its trigger conditions
  are unchanged for every currently-tested case (verified: `case_bug1305_run_identity_invariant`
  in `tests/integration/test-check-state.py` exercises exactly the U1/U2 mismatch this branch
  guards, run V).

**If only one could be applied: this one.** It is the only finding that changes behavior
(defensively) rather than restating settled design (D-01) or reporting on already-covered
files (reuse/efficiency angles).

### Rest of the sweep — nothing else found

- `check-domain.sh`'s rewritten comments (`RE_RUN_DIGEST`/`RE_PLAN_YAML`/`RE_RUN_IDENTITY`
  rationale, the #1058 digest-guard docstring) state present fact, not change narration —
  and are shorter than what they replaced. No dead references: I re-verified the `#1058`
  comment's "fires on Write and Edit" claim against the Edit-route dispatch at
  `check-domain.sh` ~2042–2048, which does include `RE_RUN_IDENTITY`/`RE_RUN_DIGEST` — accurate.
- `bash-write-guard.sh`'s `_run_artifact_guard` docstring was shortened and stays accurate
  (verified the `RE_RUN_IDENTITY` check precedes the digest/state check, matching "stays
  ahead of the DEC-153 worktree carve-out").
- No redundant conjuncts found in the new POST-mint block (`check-domain.sh` ~1568–1592) or
  `prior_has_uid` (~1628–1630) — every conjunct there gates a distinct, necessary precondition.
- The `case_bug1305_run_identity_invariant` fixture in `tests/integration/test-check-state.py`
  double-checks its clean-tree result via both `clean_code == 0` and `"INV-36" not in
  clean_out` — two spellings of "nothing was flagged." **BACKLOG, not apply** (weakening a
  test assertion is out of scope post-qa-gate).

## Part 2 — risk grading (`code-grade.py`, base=`4b0d04e9` merge-base, head=HEAD)

**No grade regression among the three named production files' changed functions.**
`harness_boundary.py`'s diff (import + one new regex constant) touches no function body —
nothing to grade there; its one FAIL (`worktree_owner`, grade 2) is pre-existing and untouched
by this diff (confirmed by grading the base file directly — same grade 2/FAIL/med).

| File | Function | Before | After | Note |
|---|---|---|---|---|
| `validate-digest.py` | `check_artifact_file` | **2 (FAIL, cyc16/cog16/abc36.2)** | split into 6 helpers, each **4–5 (PASS)** | improvement, not regression — the D-08 refactor fixed a pre-existing FAIL |
| `run_identity.py` | `uid_conflict` | — (new file) | **3 (FAIL vs. production bar 4**, cyc9/cog11/abc18.1, severity high) | new function, does not clear the repo's production threshold |
| `run_identity.py` | all other functions (`marker_path`, `read_marker`, `mint_uid`, `inject_uid`, `record_seed`, `conflict`) | — (new) | 4–5 (PASS) | clear |
| `validate-digest.py` | 6 new helpers (`_durable_artifact_path` etc.) | — (new) | 4–5 (PASS) | clear |

**Genuine regression, in scope of "changed Python under tests/":**

| File | Function | Before | After |
|---|---|---|---|
| `tests/integration/test-check-domain.py` | `main` | **2 (FAIL, abc 44.2)** | **1 (FAIL, abc 48.5)** — worsened a band, from the three added `fails += run_bug1305_*_cases()` lines |
| `tests/integration/test-check-state.py` | `main` | 1 (FAIL, abc 144.1) | 1 (FAIL, abc 145.8) — already at floor, band unchanged, not a regression |

New test functions that do not clear the test-code bar (grade 3): `_write_while_sweep_reads_fifo`
(2, med), `run_bug1305_digest_repair_cases` (2, med), `run_bug1305_marker_cases` (**1, high**),
`case_bug1305_run_identity_invariant` (2, med) and its nested `build` (**1, high**),
`case_uid_mint_and_injection` (2, med), `case_seed_conflict_guards` (2, med) — all in
`tests/unit/test-run-identity.py` / `test-check-domain.py` / `test-check-state.py`. These are
test-only, per-function `REASON REQUIRED` per the grading skill's own rule; flagging for the
record, not proposing extraction — splitting fixture-heavy BUG-1305 test cases risks losing
the single-git-init-per-case fixture shape these tests intentionally share (out of my domain
to redesign; QA/test-authoring call).

## `git status --porcelain` (verbatim)

```
 M tests/integration/test-check-domain.py
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/qa-testmatrix-c1.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/receipt-harness-backend-dev-simplify-reuse-c1.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/receipt-harness-dev-ops-simplify-altitude-c1.md
?? .harness/harness/features/BUG-1305-run-state-clobber/notes/receipt-harness-dev-ops-simplify-efficiency-c1.md
```

The modified `tests/integration/test-check-domain.py` (adds an `_bug1305_identity_edit`
`new_string` parameter and a `different_edit` case) is **not my edit** — I made no writes
beyond this receipt and `/tmp` scratch files. Reported as observed per O-06; a concurrent
sibling (qa or another reader) is the likely source.
