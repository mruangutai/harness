# Goal-check — BUG-1290 — at `review_sha` c488218eb448be1a6cffda103fcdd7275a366069 (B-16)

**9 of 9 success criteria MET. SC-02's residue is DISCHARGED — no residue remains.** The B-16 fix
does what it was directed to do: with case `5g` committed, deleting the harness fixture's
`depends_on=["T-99"]` reddens the suite instead of silently restoring the pre-B-3 blind state.
Two known limits of `5g` are recorded below; neither bears on SC-02's own words.

Scope of the pin: test-only. `git diff --stat 7104aa43 c488218e -- .agents/ .claude/skills/ tests/`
returns exactly one file, `tests/unit/test-factory-claim.py` (+57/-8), with hunks confined to `5b`'s
comment/scenario region and the appended `5g` block — cases `5a`, `5c`, `5d`, `5e`, `5f` textually
untouched. Production is byte-identical to `7104aa43`. The worktree's tracked code and tests are
identical to the pin (`git diff --stat c488218e` names only `feature.json`), so in-tree runs grade
the commit.

## Per-criterion table

| SC | `verify:` as BRIEF writes it | What I actually ran / read | Observed | Verdict | Basis |
|---|---|---|---|---|---|
| SC-01 | test — `tests/unit/test-factory-claim.py` | full suite in tree + arm A0 | `ok BUG-1290 5a`; `125/125 checks passed`, exit 0 | MET | re-derived |
| SC-02 | test — `tests/unit/test-factory-claim.py` | my own 5-arm scaffold (below) | `5b` ok intact, `5b` FAIL under my production mutant; `5g` FAIL when the fixture dep is deleted | MET | re-derived from scratch |
| SC-03 | test — `tests/unit/test-factory-claim.py` | same suite, case `5c` | `ok BUG-1290 5c` | MET | re-derived |
| SC-04 | test — `tests/unit/test-factory-claim.py` | same suite, case `5d` (calls production `fc.features_root("owner/harness")`) | `ok BUG-1290 5d` | MET | re-derived |
| SC-05 | test — `tests/unit/test-factory-claim.py` | case `5e` + content read of `git show c488218e:tests/unit/test-factory-claim.py` for `FEATURES_ROOT` | `ok BUG-1290 5e`; the only surviving `FEATURES_ROOT` occurrences are inside `5e`'s absence assertion — no module-scope case pins a default | MET | re-derived |
| SC-06 | test — `tests/unit/test-factory-claim.py`, case `BUG-1290 5f` | same suite, case `5f` (behaviour scan, counts 0/0/1) | `ok BUG-1290 5f` | MET | re-derived |
| SC-07 | test — `tests/integration/test-factory-integration.py` | suite in tree | `131/131 checks passed` | MET | re-derived (production carried from `7104aa43`) |
| SC-08 | test — `tests/unit/test-factory-claim-mutation.py` | suite in tree — it re-runs the CHANGED file in-process, so it could have moved | `BASELINE 3/3 ok`, `MUTATION PROOF: 3/3 cases reddened`, `5a`/`5b`/`5c` all FAIL under the mutant | MET | re-derived |
| SC-09 | test — `tests/integration/test-layout-migration.py`, plus T-04's reader-row probe | suite (exit 0, case 22 ok) + T-04's probe verbatim from `plan.yaml` | `READER ROW PROBE: ok 5 {... factory_config.py: migrated ...}`, `factory_claim.py` absent, `PROBE_EXIT=0` | MET | re-derived |

Carried forward: nothing is carried on assertion alone. SC-07 and SC-09 rest on production that is
byte-identical to `7104aa43`, but I re-ran both suites and the probe at this pin rather than citing
the earlier grade; the carry is therefore only the *reasoning* that the test-file change cannot
reach them, and it is backed by a run.

## SC-02, from scratch

Scaffold: `/tmp/sc02_scaffold.py` builds five out-of-tree arms, each a real copy of
`.claude/skills/harness/bin` plus `git show c488218e:tests/unit/test-factory-claim.py`. No worktree
file was touched. Raw output:

```
=== A0 intact                                   exit=0  125/125 checks passed.   5b: ok    5g: ok
=== A1 prod issue-map key -> feature only       exit=1  1 of 125 FAILING.        5b: FAIL  5g: ok
=== A2 fixture drops depends_on=[T-99]          exit=1  1 of 125 FAILING.        5b: ok    5g: FAIL
=== A3 fixture empties harness issue map        exit=1  1 of 125 FAILING.        5b: FAIL  5g: ok
=== A4 5g mutant's delegating call -> bare raise exit=0 125/125 checks passed.   5b: ok    5g: ok
```
(no other case reddened in any arm; `5a`, `5c`–`5f` ok throughout)

**A1 is my own production mutant**, independent of `5g`: in the arm's copy of
`factory_claim.py`, `_BlockerCache.issue_number`'s `key = (repo, feature)` becomes `key = feature`
— the real pre-B-3 defect in real code. Case `5b` reddens.

**(a) Is SC-02 MET at this pin, on the criterion's own words?** Yes. SC-02 requires that with one
feature id under two served segments carrying different DAGs, each verdict is computed from its own
plan, and that a case proves the second candidate does not receive the first's cached task. Case
`5b` is that case; A1 shows it is discriminating against the actual production defect, not green by
construction.

**(b) Is the recorded residue discharged?** Yes. The residue was "the property is proven, not
defended": at `7104aa43`, deleting the fixture fragment `depends_on=["T-99"]` restored the blind
state with a fully green suite. At this pin that same deletion (A2) yields `5g: FAIL`, `1 of 125
FAILING`, exit 1. The fixture fragment SC-02's proof depends on can no longer be removed silently.

**(c) Does `5g` satisfy the operator's directive as written?** Yes, on both clauses of
`notes/answers-2026-09-06-b16.md`. `5g` mutates the issue-map cache to discard the repository key
(a `_BlockerCache` subclass routing every lookup through the first repo seen for a feature id) and
requires `5b`'s property to be FALSE under it — the "must fail case `5b` when the issue-map cache is
mutated" clause, and it is a permanent committed case, not a one-off harness. The purpose clause —
"deleting the fixture dependency cannot silently return the suite to the pre-B-3 blind state" — is
A2: the deletion now reddens.

## The limit of the proof

1. **`5g` asserts a negation, so it also passes when `5b`'s own baseline is broken.** Measured
   myself as A3 (empty the harness segment's issue map): `5b` FAIL, `5g` ok. **No effect on the
   grade.** SC-02's evidence is the pair, and in every state where `5g`'s green is vacuous, `5b`
   itself is red and the suite exits 1 — there is no reachable state that returns a green suite with
   the property unproven. That is exactly the property B-16 asked for.
2. **Replacing the mutant's delegating `super()` call with a bare `raise` leaves both `5b` and `5g`
   green** (A4, 125/125). `5g` cannot distinguish "the mutant collapsed the key and broke the
   property" from "the mutant crashed". **No effect on the grade.** This is a hand-edit of the test's
   own mutant — a state neither production code nor any fixture can reach — and neither SC-02 nor
   the operator's directive quantifies over the robustness of `5g`'s mutant against being rewritten.
   It is a real, recorded weakness of the third-order proof, already a backlog row.

## Recommendation (not a gate)

**NEW — covered by no BRIEF criterion.** Give `5g` a positive control: assert inside the mutant that
the delegating call was reached (or assert `5b`'s property holds unmutated in the same block) so a
crashing mutant reads FAIL rather than ok. This closes limit 2. It is not a delivery gap: BRIEF says
nothing about `5g`, and B-16's directive is discharged without it. Route it as a backlog row for the
operator, not as a rework cycle.

Anchors: content read via `git show c488218e:<path>`; no line numbers or glob counts were used as
evidence.
