# R2 closed, R3/R4/R5 corrected — and T-11 now carries two RED cases the operator must rule on

BLUF: T-11's BE-21/22/23 were 1:1 relabels of integration guards; they are now three decision-table
rows at the `_build_entry_preflight` seam, each reaching a state the integration bed cannot present.
**Two of them (BE-22, BE-23) are RED at HEAD** — measured, not predicted — because
`gh-sync.py:1360` omits `rstrip("/")`. T-11 forbids production edits, so its `verify` cannot reach
`VERIFY-PASS` until that defect is fixed outside T-11; the intent now says so in as many words and
routes the fix to the operator. R3, R4, R5 are single-field corrections.

## What changed (four `plan-merge.py amend` compare-and-swaps, nothing else)

| field | change |
|---|---|
| T-11 `intent` | BE-21/22/23 re-aimed (R2); FIXTURES sentence corrected (R3); SC-14 attributed to FEAT-34 (R5) |
| T-10 `traces` | `[REQ-02, REQ-09]` -> `[REQ-02]` (R4) |
| T-10 `title` | names the **FEAT-34** SC-14 merge fixture (R5) |
| T-10 `intent` | opening paragraph states the criterion is FEAT-34's and that BUG-1309 ends at SC-10; the id is kept because it is the reader's handle into the test file (R5) |

`T-11 verify` untouched in that pass. **SUPERSEDED by the send-back below: BE-21 is struck and the
`verify` now carries an explicit 29-id list.** `T-10 verify` untouched: its greps are the test file's
literal assertion names.

## The re-aimed cases, and why each is unit-only (BE-21 struck — see the send-back section)

All call `_build_entry_preflight(feat_dir, rec)` directly with a constructed `rec`.

- **BE-21** — **STRUCK.** It was `rec = {"build_entry": "reopened"}`, non-era, expecting no
  `SystemExit` and both streams empty. The lead rejected it as a same-path parameter row and the
  rejection is correct: that is BE-24's path and BE-24's observable. See the send-back section.
- **BE-22** — era member, `feat_dir + "/"`, entry `None`. Expected: continues, stderr `predates`.
  **RED at HEAD**: raises `SystemExit 2` with the recover-terminal refusal, because `:1360` takes
  `os.path.basename(feat_dir)` with no `rstrip`, so the basename is `""` and the era test misses —
  while `recovery_command_for` (feature_schema.py:326) rstrips and resolves the same string to an
  era member. A trailing slash is a property of the argument, not of the tree; the bed builds every
  `feat_dir` with `os.path.join`.
- **BE-23** — same input, entry `recovery-required`. Expected: stderr `is not refused`, no
  `gh-sync.py open`. **RED at HEAD**: the same missing rstrip routes an era member into
  `_build_entry_recovery_notice`'s non-era branch (:1387-1389), which tells the operator "the MERGE
  is refused until gh-sync.py open records opened" — false for an era feature under SC-04.

Probe evidence: both reds and BE-21's green were observed in-process at plan time
(`/tmp/probe_be_2123.py`, `/tmp/probe_be23.py`); CASE A of the first probe is the correct behaviour
the same input produces without the slash.

## How I checked no case restates integration

Compared each replacement against the **complete** T-04 set in
`tests/integration/test-gh-sync.py:3596-3624`, read as one block: `T-04 non-era absent refuses`
(:3602), `T-04 BUG-named non-era absent refuses` (:3608), `T-04 station discriminator` (:3612),
`T-04 era-exempt continues` (:3618), `T-04 era recovery-required does not claim a refusal` (:3623).
The old BE-21/22/23 mapped onto :3602/:3612/:3618 predicate-for-predicate. BE-23 shares the :3623
predicate but on an input that bed cannot supply and with the **opposite** outcome, so it is not a
copy of a passing guard. Also compared against the eight `T-02` guards (:3409-:3492) for the
read/write rows — no overlap with BE-21.

## R3, precisely

`_feature_dir_name` (feature_schema.py:307-321) reads the segment after `features`; its only caller
is the `RUNS_AGENT_EXEMPT` lookup in `_runs_agent_problems` (:351), which is on no seam T-11 drives.
`recovery_command_for` (:324-326) keys on `basename(feat_dir.rstrip("/"))` and reads no other
segment. The consequence is corrected too: the fixture path shape is load-bearing for realism and
for `feature_json_write`, **not** for `recovery_command_for`'s decision.

## R4 reasoning

REQ-09 (legacy recovery under GitHub outage keeps the worktree) is T-07's and T-03's; T-10 asserts
its complement — the sweep removing the worktree by the normal path. REQ-03 was considered and
rejected: T-10 relies on the local receipt rather than delivering it. `[REQ-02]` is the weakest
sufficient claim. REQ-09 remains traced by T-03 (:426) and T-07 (:1183).

## Untouched, proven

`approval` raw sha256 `b6515d5c…99dff6` and `panel` raw sha256 `8a0e056c…0ce9fa` are identical
before and after (21 and 75 lines; 7 findings, ids/severities/dispositions unchanged). Task count 11
(T-01..T-11). `T-11 title/verify` and `T-10 verify` sha256 unchanged from their pre-edit `--show`.
`yaml.safe_load` OK. `check-plan-routes.py <plan>` exits 0, 0 violations (four DEVIATION lines are
the standing DEC-174 carve-outs for T-04/T-06/T-07/T-10).

## Open questions

- **Q1 (blocking the T-11 gate, not this edit):** the `gh-sync.py:1360` missing `rstrip("/")` is a
  live defect with two consequences (wrong refusal, false merge claim). T-11 documents it and cannot
  green while it stands. Fixing it is a one-line change to `gh-sync.py` — T-04's surface, not
  T-11's. Operator ruling needed: widen T-04, or accept T-11 landing with two reported reds.
- **Q2 (non-blocking, out of this feature's criteria):** `gh-sync.py:1234` calls `int(parent_arg)`
  unguarded, so `recover-terminal --parent abc` raises `ValueError` (probed) and prints the stack
  trace the file's own comment at :1349 forbids. Nothing in this BRIEF covers it and no BE id was
  spent on it. Separate bug ticket. (The old reason given here — that a 31st id would break the
  `seq -w 1 30` range — no longer applies: the range is now an explicit id list. The ticket still
  belongs outside this BRIEF, on its own merits.)

---

# Send-back: BE-21 struck. T-11 is 29 cases, deliberately

BLUF: **exit (b).** No re-aim was available that is BOTH unit-only and unheld, so BE-21 is removed
and `T-11.verify` now enumerates the 29 surviving ids instead of `seq -w 1 30`. BE-22..BE-30 are
**not** renumbered. Nothing else in the plan moved.

## The lead's finding is correct, and measured

`_build_entry_preflight` (gh-sync.py:1357-1376) has exactly **four** terminal paths:

| # | condition | observable | held by |
|---|---|---|---|
| P1 | `entry is None`, non-era | `refuse`, two messages split on `recovery_command_for` | integration `:3602`, `:3608`, `:3612` |
| P2 | `entry is None`, era | stderr `predates`, continues | integration `:3618`; **BE-22** (slash variant) |
| P3 | `entry == "recovery-required"` | notice, era/non-era sub-branch at `:1380` | integration `:3623`; **BE-23** (slash variant) |
| P4 | **any other value** | falls through both, prints nothing | **BE-24** |

BE-21 sat in P4 with BE-24. Probed in-process at HEAD, `"reopened"`, `"opened"`, `"not-applicable"`,
`42` and `"REOPENED"` each returned with no exit and two empty streams — **byte for byte identical**.
The two rows are not merely similar; they are indistinguishable by construction. And BE-21's stated
justification (the `load_recorded:624-626` normalization) is already the assertion of BE-11 and
BE-12, so BE-21 asserted the permissive side of a state `load_recorded` can never emit — it would
have stayed green on the day that normalization broke.

## Why no re-aim (a) was taken

Every unit-only state I could name at the T-02/T-03/T-04/T-06 seams in these two files is already
held: BE-11/BE-12 (the normalizer), BE-13/BE-15 (`record_build_entry`'s only two branches — the
`== "opened"` no-op at `:947` and the write at `:949`), BE-16..BE-20 (the five skip branches),
BE-25..BE-30 (recover-terminal). Constructing a P4 row with a different literal, or a slash variant
of P1/P3, reproduces exactly the padding that was rejected — `realpath` normalizes the slash out of
every P1/P3 message, so those observables are not even distinct.

**Two unheld branches exist, and neither qualifies** — both are reachable through the subprocess bed,
so both belong to integration, not to a unit floor. Recorded here rather than smuggled into T-11:

- **`_build_entry_preflight` P3 non-era** (`:1387-1389`, the "MERGE is refused" line). The five T-04
  guards cover era `recovery-required` (`:3623`) but not the non-era complement. A non-era fixture
  with `build_entry: "recovery-required"` reaches it through `start-task`.
- **`_projected_for`'s vocabulary refusal** (`:1345-1354`). No guard in `test-gh-sync.py` drives it
  (greped); a fixture `plan.yaml` carrying an out-of-vocabulary station reaches it.

Both are T-04/T-06 integration surfaces. Out of scope here (no new task, no other task touched).

## The amended gate, and proof it discriminates

```
out=$(python3 tests/unit/test-feature-schema-build-entry.py && python3 tests/unit/test-gh-sync-build-entry.py) || exit 1
if printf '%s\n' "$out" | grep -q '^FAIL '; then exit 1; fi
for n in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 22 23 24 25 26 27 28 29 30; do
  printf '%s\n' "$out" | grep -qF "PASS BE-$n " || exit 1
done
echo VERIFY-PASS
```

Everything but the loop header is unchanged; still a literal `|` block. Exercised against stub
emitters: full set -> exit 0 `VERIFY-PASS`; **each of the 29 ids removed one at a time -> nonzero in
29/29**; one injected `FAIL ` line -> exit 1.

## Untouched, proven by sha256 (before -> after)

`approval` `b6515d5c…99dff6` and `panel` `8a0e056c…0ce9fa` byte-identical (21 and 75 lines).
`T-10.title` `463002b5…`, `T-10.intent` `d5aecda3…`, `T-10.traces` `44fe0221…`, `T-11.title`
`4a3a5d3b…` all SAME. Task count 11 (T-01..T-11).

**BE-22, BE-23 and the R3 FIXTURES sentence:** the pre-edit `T-11.intent` was reconstructed and
confirmed byte-exact against its recorded `--show` hash `0fd82b57…db06` (plan-merge hashes the raw
indented block, so the reconstruction had to be re-rendered in that form to compare). `diff` of the
reconstruction against the new value is **six hunks and nothing else**: the id-list sentence in
CONVENTIONS, `Twenty cases` -> `Nineteen`, `three states`/`none` -> `TWO`/`neither`, deletion of the
BE-21 bullet, `other 28 ids` -> `27`, and the appended strike note. The BE-22 and BE-23 bullets and
the FIXTURES paragraph are inside no hunk.

`yaml.safe_load` OK. `check-plan-routes.py <plan>` exits 0, 0 violations (the four DEVIATION lines
are the standing DEC-174 carve-outs for T-04/T-06/T-07/T-10).

## New open question

- **Q3 (non-blocking, not mine to act on):** `approval.status` is `approved`, and this is the third
  amendment landed under that signature. The task *set* is unchanged (11 tasks), but T-11's case set
  and its gate both changed. `harness-spec-driven` says re-planning resets approval; I am forbidden
  from writing `approval`, so the main session owns the call on whether the signature still covers
  the plan as it now stands.
