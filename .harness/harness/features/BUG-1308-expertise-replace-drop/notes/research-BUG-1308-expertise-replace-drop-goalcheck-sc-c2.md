# Goal-check — BUG-1308 — SC-01..SC-12 at review_sha 48d2285b

**All twelve criteria are MET at `48d2285be7770a7e630b0a11c8136a55b2d351e3`. The feature's goals are
met.** No criterion is unmet; no criterion is undeterminable; no criterion is unmeetable as written.
No code defect and no test-only gap found. Nothing routed back.

Graded by the method each criterion declares. Every automated criterion was RUN, not read. File
content was read with `git show <review_sha>:<path>`, never the working tree (G-15).

## Suite baseline at the pin

| Suite | Command | Exit | `^FAIL ` lines | Files |
|---|---|---|---|---|
| unit | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | 0 | 0 | 28 |
| integration | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 0 | 0 | 46 |

Counted with `grep -c '^FAIL '`, not a tail read (G-08). Matches the contract exactly.
Named files run directly: `test-expertise-ops.py` exit 0 (69 `PASS` assertions),
`test-expertise-merge.py` exit 0 (143), `test-gen-decisions-index.py` exit 0.
`HARNESS_AGENT_TYPE` cleared before every suite invocation (O-01).

## The twelve

| SC | Verdict | Method | Command | Observed |
|---|---|---|---|---|
| SC-01 | **met** | automated / integration | `python3 tests/integration/test-expertise-merge.py` | case11 ×6: exit 0; `REPLACED P-07`; Patterns still 15; **7th** entry line is P-07 and carries new text |
| SC-02 | **met** | automated / integration | same | case12 ×8: exit 0; `DROPPED G-03`; `- G-03:` absent; G-01/02/04/05 each still present |
| SC-03 | **met** | automated / integration | same | case13 ×7: exit 10; `MISSING TARGET` + id `P-99` + section `Patterns`; sha256 unchanged; byte-identical; following apply exit 0 |
| SC-04 | **met** | automated / unit+integration | both files | see clause table below — all four conditions fixtured |
| SC-05 | **met** | automated / integration | integration | case15 ×3: non-zero exit; sha256 equals pre-invocation; following add-only apply exit 0 |
| SC-06 | **met** | automated / integration | integration | exit 0; case4 exit 7 CONFLICT, case5 exit 8 CAP EXCEEDED, case16 re-asserts both; diff `4b0d04e9..48d2285b` removes **no** pre-existing `check(`; `expertise-merge.py` is purely additive (+308/−0) |
| SC-07 | **met** | automated / unit | `python3 tests/unit/test-expertise-ops.py` | exit 0; u10 feeds the same replacement input to `compute_union`: "returns non-empty conflicts" + "merged Patterns still carries **OLD** text at index 6" — reverting the resolver reddens |
| SC-08 | **met** | automated / integration | integration | `check-expertise.sh` exit 0 on the replace-produced file (case11) **and** the drop-produced file (case12); also case19 |
| SC-09 | **met** | automated / integration | integration | case17 ×11 — see clause table |
| SC-10 | **met** | automated / integration | `git show …:DECISIONS-INDEX.md` + `python3 tests/integration/test-gen-decisions-index.py` | `DEC-219` row at :219; phrase count = **1**; generator test exit 0 |
| SC-11 | **met** | automated / integration | integration | case18 ×5 — see clause table; **2.04s observed** hold |
| SC-12 | **met** | automated / unit+integration | both files | case19 ×7 + u11 ×7 (incl. reversal) + u12 ×2 |

## Clause-by-clause for the four multi-clause criteria (P-04)

Graded item by item, never by a file-global grep.

**SC-04** — four conditions, all four exercised:
- duplicate id already in the file → case14(b): exit 11, `AMBIGUOUS TARGET`, id `P-04`, section, reason, sha256 unchanged.
- two ops in one proposal naming same section+id → case14(c): exit 11, same five assertions, id `P-01`.
- `section` **absent** → exit 12 `MALFORMED OPS` naming key `section` and `index=0`: u13 (×4 verbs) at the resolver, case20(a) through the CLI.
- `section` **empty** → same: u13 "replace empty section" ×4, case20(b) ×4.
- The trailing gloss ("sha256 unchanged across the refusal and a following `apply --entries` exits 0") binds to case20 as a whole; (a) and (b) each assert sha256 unchanged and case20 asserts the following apply exits 0. Met (P-05).

**SC-09** — normalisation, both directions, three copies:
- `_normalise` (`:632`) strips `` ` ``, `*`, `_` then collapses whitespace runs — exactly as written.
- `merge` detected by **AND** of both phrases (`:713`): `replace on the surviving id` **and** `drop of the absorbed id`.
- anchor asserted to match the real SKILL.md **exactly once** (bounds the region — G-04).
- copy (a) phrase removed → reddens FIRST direction, asserted **not** the second; copy (b) extra verb `prune` → FIRST, not second; copy (c) `drop` removed from vocabulary line → **SECOND** (`ACCEPTED − CONTRACT`), not the first. Each copy asserts WHICH direction. Second direction reachable via `_harvest_help_verbs()`, as the criterion states.

**SC-11** — deterministic, and no bypass. Verified structurally, not by the pass:
- test takes the production lock itself: `with harness_merge.acquire(lock_path)`, `lock_path = path + ".lock"` (`:907`) — same primitive and path `locked_update` uses.
- both writers spawned **inside** that block via `subprocess.Popen`; polled every `0.05s` across a `2.0` hold; asserts neither exited. 2.0 ≪ `LOCK_TIMEOUT_SECONDS = 10.0`, so a correct child waits rather than refusing at exit 6.
- post-release: `communicate(timeout=20)` each, both exit 0; census = original eight **+ P-09 + P-10**; `P-07` carries child B's marker.
- **No production test bypass:** `harness_merge.py` is **untouched** by the feature (`git diff --stat 4b0d04e9..48d2285b` on that path is empty — its two `time.sleep` calls are pre-existing lock retry). `expertise-merge.py` contains no `getenv`/`environ`/`sleep`/test-only flag; the only two matches are comments asserting the absence. Determinism comes from the test holding the lock, not from timing.

**SC-12** — composition, reversal, second shape:
- case19: drop `P-01` (low index) + replace `P-05` (higher index), one proposal → exit 0; **file-order** sequence exactly `P-02,P-03,P-04,P-05`; marker on P-05 and on no other entry.
- u11: same outcome asserted **forward and reversed**, plus "forward and reversed produce identical merged Patterns".
- u12: two drops at distinct original indices → `[P-02,P-03,P-05]`, length 3.

## Emergent — flagged, never adopted

- **case24** (`add` whose target matches a duplicated occurrence → exit 11, sha256 unchanged, "not the pre-fix outcome") and **case20(c)** (a digest-shaped `expertise_update` mapping → exit 12) assert behaviour **no SC states**. Judged **covered in spirit** by REQ-05/REQ-06 but **new** as criteria. Recommendation: leave as-is — they are strictly additional safety landed by the cycle-1 panel fix, and widening the BRIEF at goal-check would be deciding the verdict first (P-17). No action.

## Anchor drift note

As anticipated, cycle-1 shifted `expertise-merge.py`; I anchored every grade on **content strings**
(`REPLACED P-07`, `MALFORMED OPS`, `replace and drop through the ops subcommand`), never on a line
number or a measured count from the plan. No anchor defect surfaced.

## Proof nothing was changed

`git status --porcelain` after grading — the single entry is this artifact:

```
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/research-BUG-1308-expertise-replace-drop-goalcheck-sc-c2.md
```

HEAD unmoved at `2d5503a1`. No commit, no formatter, no linter. BRIEF.md, plan.yaml, STATE.md and
feature.json untouched.

## Open questions

None blocking. No unmet criterion, so no owning task and no code-vs-tests routing is required.
