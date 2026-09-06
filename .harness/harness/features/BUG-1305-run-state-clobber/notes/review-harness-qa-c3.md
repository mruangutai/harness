# QA re-gate — cycle 14 — review_sha `5ed929bd`

## Verdict: SC-01 MET (literal `FAILS if`), with one high-value wording gap flagged

Every case the `FAILS if` clause tests for is present, non-vacuous on exit code, and (where
required) shown RED at the pre-change copy (`1b11bc18`) and GREEN at the pin. Case (iii) — the
mandatory omp-shaped payload — is present, non-vacuous, RED pre-fix, GREEN at pin. **But**: the
message the fix emits for every reconstruction-`None` state.yaml Edit (cases i, ii, iii-refused)
is a single fixed string that never actually computes or names a conflicting value — it fires
identically whether the witness truly disagrees or the payload is merely unmatched/absent. That is
a real gap against BRIEF's descriptive text for (a) ("names the identity conflict rather than a
generic shape error"), but it is not what the literal `FAILS if` clause tests, so it does not by
itself flip the verdict — reported as `Q1`.

## Method

All case functions called directly from the review-sha test module (not a scratch reimplementation)
via `importlib.util.spec_from_file_location` against a disposable worktree at `5ed929bd`
(`git worktree add --detach <abs>/.claude/worktrees/qa-c3-scratch 5ed929bd`, removed after use).
Pre-fix guard extracted with `git show 1b11bc18:.claude/skills/harness/bin/check-domain.sh` into a
scratch file, selected via `CHECK_DOMAIN_BIN=<path>` (the module reads this env var at import,
`test-check-domain.py:27`) — no working-tree file was ever touched.

Replay recipe (swap `CHECK_DOMAIN_BIN` to the pre-fix copy or omit it for the pin):
```
python3 -c "
import importlib.util, sys
spec = importlib.util.spec_from_file_location('tcd', '<WT>/tests/integration/test-check-domain.py')
tcd = importlib.util.module_from_spec(spec); sys.modules['tcd']=tcd; spec.loader.exec_module(tcd)
print(tcd._bug1305_absent_prior_edit_case())      # case i
print(tcd._bug1305_unmatched_edit_case())         # case ii
print(tcd._bug1305_omp_edit_cases())              # case iii + control
print(tcd._bug1305_identity_refusal_cases())      # b, c, f-half-1
print(tcd._bug1305_identity_allow_cases())        # d, e (identity variant)
print(tcd._bug1305_marker_recovery_cases())       # d (marker variant)
print(tcd._bug1305_marker_witness_precedence())   # f-half-2
"
```

## Per-case table

| Case | Present (fn) | Non-vacuous | RED @ `1b11bc18` | GREEN @ `5ed929bd` |
|---|---|---|---|---|
| (i) absent prior + Edit, `run_id: A`→`B` | Y `_bug1305_absent_prior_edit_case` | Partial — exit2 + 3 stderr substrings, but see Q1 | Y (exit 0, `''`) | Y (exit 2) |
| (ii) present prior, unmatched old_string (count==0) | Y `_bug1305_unmatched_edit_case` | Y (exit2 + message) | Y (exit 0, `''`) | Y (exit 2) |
| (iii) **omp-shaped `{file_path}`-only payload, witnessed state.yaml — MANDATORY** | Y `_bug1305_omp_edit_cases` (refused half) | Y (exit2 + message) | Y (exit 0, `''`) | Y (exit 2) |
| control: unique `old_string` still reconstructs | Y `_bug1305_omp_edit_cases` (allowed half) | Y (exit0, distinguishes fail-closed-on-`None` from deny-by-path) | Y (exit 0 — pass) | Y (exit 0 — pass) |
| (b) Write+Edit, equal seed fields, different `run_uid` | Y `_bug1305_identity_refusal_cases` ("different minted uid is/Edit is refused") | Y (names U1 **and** U2, no field-disagreement wording) | Y (both halves: exit 0, `''`) | Y (exit 2, message intact) |
| (c) Write+Edit, PRESENT prior U1, incoming carries no `run_uid` | Y `_bug1305_identity_refusal_cases` ("modal collision Write/Edit omitting uid") | Y (names U1, "run identity", excludes "field disagreement") | Y (both halves: exit 0, `''`) | Y (exit 2) |
| (d) recovering owner, absent prior / zero-byte prior | Y ×2 conventions: `_bug1305_marker_recovery_cases`, `_bug1305_identity_allow_cases` | Y (exit0, no non-zero assertion anywhere) | n/a (do-no-harm, not required red) | Y (exit 0 both halves, both conventions) |
| (e) resumed owner, same `run_uid`, different session id | Y `_bug1305_identity_allow_cases` ("DEC-154 resumed owner...") | Y (exit0) | n/a | Y (exit 0) |
| (f) half 1 — witness+prior agree run_id A/U1, incoming run_id B/U1 → Issue #1124 wording | Y `_bug1305_identity_refusal_cases` ("run_id disagreement keeps Issue 1124 precedence") | Y (asserts `Issue #1124` present, `Issue 1305` absent — message, not code) | (not required) | Y |
| (f) half 2 — witness A, prior parses w/ no `run_uid`, incoming B → Issue 1305 wording | Y `_bug1305_marker_witness_precedence` ("witness outranks legacy run_id ladder") | Y (asserts `Issue 1305` present, `Issue 1124` absent) | (not required) | Y |
| digest Write-append beside witness (do-no-harm) | Y `run_bug1305_digest_repair_cases` | Y (exit0) | Y (exit0 — pass, unaffected by this diff) | Y (exit0) |
| unrelated-file Edit control | Y `run_bug1106_edit_route_cases` | Y (exit0, "no PRE check runs at all") | Y (exit0 — pass) | Y (exit0) |

Digest-repair / unrelated-file re-runs at pre-fix showed 2 and 4 unrelated FAILs respectively (the
refusal cases these files also carry, e.g. "an unmatched old_string fails closed" — expected, those
are the exact cases this fix closes, not part of the do-no-harm set). The allow-half assertions this
table cites all passed at both pins.

## SC-01 verdict, stated against the literal `FAILS if` clause

- (a): present, asserts exit 2 (never 0), and graded on a run directory where the prior is **wholly
  absent** — not "a parsing prior carrying a run_uid." Literal clause: **not tripped**.
- (d)/(e): both present, both assert exit 0 only. **Not tripped.**
- (b)/(c): both present, both shown RED on the pre-change copy (table above). **Not tripped.**
- (f): both halves present, both assert on message text (`Issue #1124` / `Issue 1305`), neither
  asserts "only an exit code." **Not tripped.**

**SC-01: MET**, on the literal clause. Case (iii) — the mandatory omp-shaped payload — is verified
present, non-vacuous, RED pre-fix, GREEN at pin; this was the case whose absence voided SC-01 last
cycle and it is the one this cycle actually closes.

## Findings

- **Q1 — `inside-delta:message-wording`, severity `med`.** The fail-closed branch added at
  `check-domain.sh:2058-2072` (pin `5ed929bd`) emits one of two *fixed* strings keyed only on
  `RE_STATE_YAML.match` — never on whether the incoming edit's target content would actually agree
  or disagree with the witness. Confirmed by direct call: cases (i) absent-file, (ii)
  unmatched-old_string, and (iii) omp-shape-only all produce the byte-identical stderr string. BRIEF's
  descriptive text for (a) calls for a message that "names the identity conflict rather than a
  generic shape error" — this message never computes or shows a conflicting value, unlike the
  pre-existing seed-field-refusal messages a few lines away in the same file (e.g. "run identity
  witness run_id is 'A', but the incoming ..." from `_bug1305_marker_witness_precedence`). The exit-2
  safety property is real and correctly gates production traffic; only the diagnostic specificity is
  short of the brief's prose. Exact remedy, if taken: have the `RE_STATE_YAML` branch at
  `check-domain.sh:2059-2065` read the witness's own recorded `run_id`/`run_uid` (already parsed
  earlier in this same function for the seed-field path) and interpolate it into the message, e.g.
  "...cannot be verified against this run's recorded run_uid '<U>' because the Edit cannot be
  reconstructed..." — this does not change the exit-2 behavior, purely widens the message. Not
  blocking SC-01 under the literal clause; raised because the dispatch asked this exact question by
  name and the answer is "no, not for the three cases that hit `_content is None`."
- No other findings. Do-no-harm set (Part 2) is fully green at both pins for every allow-case
  checked; nothing in the pinned diff regresses SC-02–SC-13 or the SIMPLIFY/matrix items (untouched
  by this diff, not re-run per Part 3 instruction).

## Not re-run (per dispatch Part 3)

Full `test-check-domain.py`, BUG-1106 Edit suite total, BUG-1305 digest suite total, marker suite
total, identity suite total — all already measured green by the main session; only targeted
selections above were replayed to settle the SC-01(a)/(iii) claims specifically.
