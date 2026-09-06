# Goal-check — BUG-1290 — at `review_sha` 72a97b9942832169af84479ae36487398d27ca39 (B-27)

**9 of 9 success criteria MET. All three operator directives SATISFIED, each on evidence I took this
run, not on the panel's word.** Nothing is unmet, so nothing routes to a lane. The two-file shape of
the literal `5b` failure is real and is stated plainly below; it satisfies the directive as written.

Scope of the pin. `git diff --numstat c488218e 72a97b99 -- tests/` returns exactly two files,
`test-factory-claim.py` (+37/-8) and `test-factory-claim-mutation.py` (+63/-1), and the same range
over `.agents/ .claude/ tests/` adds nothing else;
`git diff --stat c488218e 72a97b99 -- .claude/skills/harness/bin/` is EMPTY — production is
byte-identical to the pin the b16 goal-check graded. `git diff --stat 72a97b99 efed18ab -- .agents/
.claude/ tests/` is also empty, so in-tree runs at HEAD grade the pin exactly. Working tree
`git status --porcelain` was empty on entry.

## Per-criterion table — every row re-derived at this pin

| SC | `verify:` as BRIEF writes it | What I ran / read this run | Observed | Verdict |
|---|---|---|---|---|
| SC-01 | test — `tests/unit/test-factory-claim.py` | suite in tree | `ok    BUG-1290 5a`; `125/125 checks passed.` exit 0 | MET |
| SC-02 | test — `tests/unit/test-factory-claim.py` | suite in tree + my own production-seam mutant (`/tmp/gc_collapse_probe.py`) | `ok    BUG-1290 5b` intact; under a module-level `_BlockerCache` key collapse the suite prints `FAIL  BUG-1290 5b`, `1 of 125 FAILING.`, exit 1 — the case is discriminating, not green by construction | MET |
| SC-03 | test — `tests/unit/test-factory-claim.py` | suite in tree | `ok    BUG-1290 5c` | MET |
| SC-04 | test — `tests/unit/test-factory-claim.py` | suite in tree | `ok    BUG-1290 5d` | MET |
| SC-05 | test — `tests/unit/test-factory-claim.py` + content at the pin | `git show 72a97b99:tests/unit/test-factory-claim.py \| grep -n FEATURES_ROOT` | `ok    BUG-1290 5e`; the only surviving occurrences are inside `5e`'s own absence assertion (`not hasattr(claim, "FEATURES_ROOT")` and its detail string) — no module-scope case pins a default. `git show 72a97b99:.claude/skills/harness/bin/factory_claim.py \| grep FEATURES_ROOT` returns nothing | MET |
| SC-06 | test — `tests/unit/test-factory-claim.py`, case `BUG-1290 5f` | suite in tree | `ok    BUG-1290 5f` (behaviour scan: `factory_claim.py` 0, `feature-worktree.py` 0, `factory_config.py` 1) | MET |
| SC-07 | test — `tests/integration/test-factory-integration.py` | suite in tree | `131/131 checks passed.` exit 0; case `(F)` drives decompose → claim → workspace → land with `--repo acme/widget` (segment `widget`, non-`harness`) and an explicit `--fleet`, all 24 `(F)` checks `ok` | MET |
| SC-08 | test — `tests/unit/test-factory-claim-mutation.py` | suite in tree + pre-change red-state probe (`/tmp/gc_prechange_probe.py`) | `BASELINE 3/3 ok`, `FAIL` for `5a`/`5b`/`5c`, `MUTATION PROOF: 3/3 cases reddened`, exit 0. Second clause re-derived: with `factory_claim.py`/`factory_config.py`/`feature-worktree.py` restored from `eb9d044e` and the pin's test file, all six new cases print their own `FAIL` marker (`26 of 125 FAILING.`, exit 1) | MET |
| SC-09 | test — `tests/integration/test-layout-migration.py` + T-04's reader-row probe | suite in tree (exit 0, `case 22: real root's harness/features surface is CLEAN with migrated evidence`, zero `^FAIL` lines) + T-04's probe verbatim from `plan.yaml` | `READER ROW PROBE: ok 5 {… '.agents/skills/harness/bin/factory_config.py': 'migrated' …}`, `factory_claim.py` absent from the five rows, `PROBE_EXIT=0` | MET |

## The three questions, in order

**1. Does any grade change from the b16 run?** **No — 9 MET then, 9 MET now.** Production did not
move (empty bin-dir diff above), and the test surface moved only in the direction of a stronger
proof: `5g`'s bare negation became a six-conjunct assertion, and a second whole-suite mutation arm
was added. Nothing weakened, so no grade could fall. Every row above was taken this run; none is
transcribed from the b16 note.

**2. Does the delivery satisfy the operator's directive (`notes/answers-2026-09-06-b27.md`)?**
Graded independently, three verdicts:

- **(i) B-27 fixed — SATISFIED.** Not read, measured. `/tmp/gc_b27_probe.py` builds four out-of-tree
  arms (real copy of the bin dir plus `git show <sha>:tests/unit/test-factory-claim.py`) and replaces
  `5g`'s mutant `issue_number` body with a bare `raise`:

  ```
  c488218e-INTACT  exit=0  125/125 checks passed.  5b=ok  5g=ok    other-FAIL=[]
  c488218e-RAISE   exit=0  125/125 checks passed.  5b=ok  5g=ok    other-FAIL=[]   <- B-27, reproduced
  72a97b99-INTACT  exit=0  125/125 checks passed.  5b=ok  5g=ok    other-FAIL=[]
  72a97b99-RAISE   exit=1  1 of 125 FAILING.       5b=ok  5g=FAIL  other-FAIL=[]   <- B-27, closed
  ```

  A merely-raising mutant satisfied the old bare negation and now does not. That is the row, closed.

- **(ii) The literal case-`5b` failure — SATISFIED, and it is NOT the rejected `5g`-only
  equivalent.** `/tmp/gc_collapse_probe.py` patches `factory_claim._BlockerCache` at module level and
  re-executes the real suite: `mutant reached: True`, exit 1, `1 of 125 FAILING.`, and the printed
  line is `FAIL  BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache
  bleed`. The real `check(name_5b, …)` call evaluates False. That is case `5b` itself failing under
  the issue-map-cache mutation — the directive's words.

  **Plainly, on the two-file shape:** the printed `FAIL  BUG-1290 5b` line comes from
  `tests/unit/test-factory-claim-mutation.py`, which re-executes the suite via `runpy` under the
  patched class. `tests/unit/test-factory-claim.py`'s own default run never prints a red `5b` — `5g`
  reruns `_emit_5b` through a non-printing capture shim, and on its own that IS the form the operator
  rejected. **This still satisfies the directive as written**, and the reason is not a technicality:
  a suite whose own default run printed `FAIL 5b` would be a red suite, which no gate could accept.
  The mutation is necessarily applied from outside the suite, so the observable necessarily lands in
  the file that applies it. The cost is real and is already recorded as panel residuals R2/R3:
  nothing binds the two files, so deleting the mutation arm would leave `5g` looking adequate while
  the directive's actual requirement lapsed. That is a backlog matter, not a delivery gap — BRIEF
  states no criterion over it.

- **(iii) No leakage of the mutant into `5c`-`5f` — SATISFIED, on three independent observations.**
  (a) In the same key-collapse run, the whole-suite case census is
  `5a ok, 5b FAIL, 5c ok, 5d ok, 5e ok, 5f ok, 5g ok` — exactly one case reddens.
  (b) `/tmp/gc_restore_probe.py` runs the suite in-process and compares `factory_claim._BlockerCache`
  by identity before and after: `restored: True`, `name after: _BlockerCache`, zero `FAIL` lines.
  (c) The abnormal path is covered too: in arm `72a97b99-RAISE` the mutant raises inside `_emit_5b`,
  and still `other-FAIL=[]` — the `finally` restores on the exception path.
  One caveat, not a defect: `5c`-`5f` run BEFORE `5g` in file order, so their passing in a normal run
  is not by itself evidence about restoration. The committed comment at `5g` asserts they run
  afterward; that sentence is wrong and is already panel residual R4. No SC quantifies over it.

**3. Is any SC unmet because it is UNPROVEN rather than because behaviour is wrong?** **No — none of
the nine is unmet on either ground.** Every criterion has a live, discriminating check at this pin,
and each of the four graded on more than a green line (SC-02, SC-05, SC-08, SC-09) was re-derived
with a mutant, a content read at the pin, or the plan's own probe. No lane owns anything here.

## Recommendations — not gates, and not mine to adopt

BRIEF is approval-gated and untouched. Two items, both **NEW — covered by no BRIEF criterion**:

1. **Bind the two files.** `5g` asserts the symptom, the mutation arm asserts the cause; nothing
   makes deleting either visible. Panel R2/R3 say the same from inside the review lens. A backlog
   row for the operator, not a rework cycle.
2. **Prefix the diagnostic `FAIL` lines** the mutation suite prints (panel R1): they are byte-identical
   to genuine markers on an exit-0 run, so a CI-log grep for `^FAIL` reports four failures on a pass.

Neither is a delivery gap. I did not adopt either as a criterion; the call is the operator's.

Anchors: content read via `git show 72a97b99:<path>`; every verdict rests on a command run this run.
No line number or match count is used as evidence. Probes live in `/tmp`, wrote nothing into the tree.
