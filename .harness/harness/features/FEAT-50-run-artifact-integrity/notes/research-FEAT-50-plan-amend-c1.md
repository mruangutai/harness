# Plan amendment — FEAT-50, operator rulings applied (cycle 1)

**All four rulings are carried. The plan is complete and gates clean; it is UNSIGNABLE on an
external event, by the operator's own ruling.** `check-plan-routes.py` exits 0 with 0 violations,
`harness_yaml.load_plan` loads, `panel:` is byte-identical, `approval.status` is still `pending`
and `approval.rulings` is still absent. Two files changed: `BRIEF.md`, `plan.yaml`.

## What each ruling produced

**INV-32 (`choice: d`).** SC-11 now requires `check-state.sh` to exit 0 AND no violation row to
name FEAT-50 — form (c)'s weakening is refused, the FEAT-50 clause kept alongside. SC-12 regrades
onto the `## Operator ruling — INV-32` section that now exists, and is explicitly NOT met if that
section is ever restated in the (a)/(b)/(c) shape. `D-09` records the external blocker; `D-08`'s
stale "they wait on the operator" tail is replaced. BRIEF's old `## Open ruling required from the
operator — blocking` is gone, replaced by `## The INV-32 ruling, and the external blocker it
creates`, which states in one line that this plan is complete but NOT signable and its build MUST
NOT START until the external fix lands on the default branch. The `## Verification gaps` INV-32
bullet is rewritten from "known red SC-11 grades around" to "externally owned blocker SC-11 grades
directly". The rule-15 constraint bullet now records option (b) as offered, forbidden and NOT
taken.

**`PF-3d9ac1d0…` (high, Bash route) — CLOSED BY FIX.** `REQ-08` (route-completeness), `D-10`
(one seam, both surfaces, plus the scope fence), `T-09` (narrow the allow-continue at
`bash-write-guard.sh:747`), `T-10` (five cases in `test-bash-write-guard.py`), `SC-18`/`SC-19`,
and two `lanes:` rows. `T-09`'s intent names which `rel` the rule reads (the loop's ROOT-relative
one at `:706`, not the verdict's BASE-relative one — the file's comment at `:759-762`) and why,
and fences the `rel.startswith("..")` product-workspace continue at `:744` as load-bearing and out
of scope.

**`PF-964d6356…` (high, obsolete expectation) — CLOSED BY FIX.** `T-02`'s intent gains a numbered
step 5 naming the exact description string at `test-validate-digest.py:738-739`, ruling for
DELETION over rewrite and saying why (case 1 `empty-string` already asserts that direction more
strongly; a rewrite leaves a case whose name says "pass-through" while it asserts a refusal).
`T-02`'s `verify:` gains a `grep -cF … -eq 0` on that string, with the existing `-q` greps in the
same `&&` chain as its positive control. `SC-17` grades the removal at `<review_sha>` so it is not
merely instructed.

**Fourth defect (newly authorized).** `REQ-09`, `D-11`, `T-11` (`check_artifact_file` resolves a
relative artifact path through `inflight_registry.feature_root`, the file's own precedent at
`_hook_feature_dir` `:1359-1372`, falling back to `_root_or_none()`), `T-12` (four cases,
including the note that `_dec156_case` `:750-769` makes root and checkout coincident and therefore
cannot see this defect), `SC-20`/`SC-21`. **`D-11` heads off the false contradiction in writing:**
D-03's `harness_feature` ban is route-specific to `check-domain.sh`'s PreToolUse route; this hook
already consumes the key at `:1514` and `:1598-1599`. Provenance is recorded in a comment beside
`source_issues:` — the fourth item carries no issue number and entered by the operator's ruling.

## Verified

| check | result |
|---|---|
| `harness_yaml.load_plan` | LOADED — 12 tasks, 11 decisions, 7 panel findings, `approval` `{status: pending}`, `rulings` absent |
| `check-plan-routes.py <plan>` | `0 violation(s) across 1 plan(s)`, exit 0; 9 DEVIATION lines, all DEC-174 carve-outs |
| `panel:` byte-identity | `git diff -U0` hunks at 4, 135, 202, 332, 335, 422, 464, 852, 885, 930, 1038 — none inside `panel:` (original lines 12–127) |
| stale (a)/(b)/(c) framing | 3 surviving mentions, all historical: (b) offered-and-refused, (c) refused-as-weakening, SC-12's anti-restatement clause. None presents an option as open |
| `.claude/skills/harness/bin/` | untouched — `git status --porcelain` lists only BRIEF.md, plan.yaml and the orchestrator's own pre-existing uncommitted edit to the answers note |
| traceability | 9 REQs, all traced; 0 phantom traces; all 12 tasks carry every required field; `depends_on` acyclic; every `files:` entry has a `lanes:` row |
| `verify:` scalars | 0 folded `>` blocks; T-02/T-09/T-10/T-11/T-12 verify strings retain their newlines after `safe_load` |

## For the next agent

- **`panel:` is deliberately untouched and is now STALE.** Both `high` findings were reworded into
  the plan, so their content-hash ids no longer apply. A fresh panel must run and pm must
  re-transcribe `panel:` in a separate dispatch before signature.
- **`SC-13` records nine DEVIATION lines** (was five). Recorded, not graded — adding a carve-out
  task moves it.
- **`T-07`'s decision entry grew** from three rulings to five and its `depends_on` now includes
  T-09..T-12. The heading text SC-14 greps is unchanged.
- **The five `med`/`low` panel findings are untouched and still `open`.** No ruling was taken on
  them.
- **`REQ-06` was widened** from "the three defects" to "every defect this feature fixes", so T-10
  and T-12 can trace it honestly.

## Send-back c1a — SC-11's positive control was corpus-dependent (fixed)

**The defect, confirmed at source.** `check-state.sh:1868-1872` is the only output site: it prints a
`VIOLATION ` row per `bad`, a `note ` row per `warn`, and `  all state invariants hold.` when both
are empty. So a run with no `bad` and no `warn` contains no `INV-` substring at all, and SC-11's old
control `grep -q 'INV-'` rested on an accident of today's corpus. It was weakest exactly when the
criterion becomes gradeable — after the external INV-32 fix lands and the corpus is cleaner — and
would have turned SC-11 red over correct delivery. Same failure mode SC-13 and SC-14 already refuse.

**The fix.** BRIEF.md SC-11 only (prose at 201-210, command at 211). The control now keys on the
reporting block's own unconditional output:

```
out=$(bash .claude/skills/harness/bin/check-state.sh 2>&1); rc=$?; printf '%s\n' "$out" | grep -qE '^  (VIOLATION |note |all state invariants hold\.)' && test "$rc" -eq 0 && ! printf '%s\n' "$out" | grep -q 'FEAT-50'
```

Both graded clauses are byte-unchanged: exit 0 AND no row naming `FEAT-50`. Neither weakened —
operator ruling of 2026-08-31, `notes/answers-2026-08-31-plan.md` `## Operator ruling — INV-32`,
`choice: d`.

**Proof, measured 2026-08-31 in the FEAT-50 worktree.**

| case | `out` | `rc` | result |
|---|---|---|---|
| clean run | `  all state invariants hold.` | 0 | PASS — cannot go red on a clean corpus |
| errored/aborted run | empty string | 0 | FAIL — the case the control exists for |
| note row | `  note       INV-07 …` | 0 | PASS |
| FEAT-50 violation | `  VIOLATION  INV-32 … FEAT-50 …` | 1 | FAIL |

**Real run, command extracted verbatim from BRIEF.md:211: FAIL, exit 1.** Correct, not a defect. The
control clause itself is satisfied — 696 reporting rows, so the run reached the block — and it is the
exit-0 clause that fails on the 32 `INV-32` rows of the external blocker (D-09). Six rows name
FEAT-50, all in-flight state that the feature's own landing clears: unapproved BRIEF, unpinned
`review_sha`, three lead `digest.md` files failing the DEC-156 contract (the very defect T-09/T-11
fix), plus one `note` row for pending approval.

**No knock-on.** Grepped `plan.yaml` and the rest of `BRIEF.md` for any restatement of the old
control or its `INV-`-substring reasoning. `D-09` (`plan.yaml:363-384`) and the first bullet of
`## Verification gaps` (`BRIEF.md:320-329`) both discuss only the exit-0 and FEAT-50 clauses and the
external blocker — neither names the control command. Nothing else changed.

`plan.yaml` still loads through `harness_yaml.load_plan` (12 tasks, 11 decisions). `approval:` and
`panel:` untouched; `approval.status` stays `pending` and `approval.rulings` stays absent.

## Send-back c1b — SC-11's third clause was stricter than its prose (fixed)

**The defect, confirmed at source.** SC-11's prose grades "no VIOLATION row names FEAT-50"; its
third clause was `! ... grep -q 'FEAT-50'`, which matches ANY line. `check-state.sh:1868-1869`
prefixes the two row kinds distinctly — `  VIOLATION  {m}` and `  note       {m}` — and a `warn`
row is by design not a violation (`:1872` exits non-zero on `bad` only). Grepped the warn sites:
INV-22 (`:377`, `:382`, `:386`), INV-21 (`:1009`) and INV-28 (`:1150`) all interpolate `{feat}`
into a `note` row, so a perfectly healthy FEAT-50 emits feature-named notes. The clause was
therefore strictly stricter than the criterion it encodes and could go red over a benign note.

**The fix.** `BRIEF.md` SC-11 only — third clause now
`! printf '%s\n' "$out" | grep -qE '^  VIOLATION .*FEAT-50'`, plus two sentences at `:210-214`
saying why it is row-kind-scoped. The control clause and `test "$rc" -eq 0` are byte-identical to
before; the exit-0 clause is the operator's restored constraint and was not touched.

**Synthesised cases, full command line run verbatim.** (a) `all state invariants hold.`/rc=0 PASS ·
(b) `  note       INV-22 FEAT-50: run counting is INACTIVE`/rc=0 PASS · (c) `  VIOLATION  INV-32:
FEAT-50 ...`/rc=1 FAIL · (d) empty/rc=0 FAIL. All four as required.

**Discrimination probe, because (c) also fails the rc clause.** Ran clause three ALONE against (b)
and (c): new clause passes (b) and fails (c); the OLD clause failed BOTH. That isolates the delta
to the benign-note case and proves the narrowing did not make the clause vacuous — it still catches
a violation row naming FEAT-50.

**Real run against the worktree: FAIL, exit 1.** Expected and correct. The control passes, `rc=1`
on the external INV-32 blocker, and clause three also fails on in-flight rows (BRIEF not approved,
`review_sha` not pinned, four lead digests failing DEC-156) — none of them INV-32, all of them
pre-approval state. SC-11 stays ungradeable until the external fix lands and the feature is
approved and reviewed, exactly as its own text says.

**No knock-on.** Grepped `BRIEF.md` and `plan.yaml` for restatements of the third clause. Two
prose paraphrases exist — `BRIEF.md:410` and `plan.yaml:377-378` — and both already say "no
violation row names FEAT-50", which is the row-kind-scoped reading the command now matches. No
other copy of the shell clause exists. Nothing else changed.

`plan.yaml` still loads through `harness_yaml.load_plan`. `approval:` and `panel:` untouched;
nothing under `.claude/skills/harness/bin/` edited; nothing committed.
