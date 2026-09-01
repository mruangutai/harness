# Goal-check — FEAT-50 plan vs the operator's stated intent (cycle 0)

**Does this plan deliver the operator's stated intent?** **Yes — the intent is deliverable and
nothing in the intake is unrepresented — but two of the three remedies are at risk of landing dead
for reasons a build would discover late, and pm wrote the one mapping it may never write.** Graded
against `notes/answers-2026-08-31-plan.md`, not `BRIEF.md`. Nine findings, none `critical`, none
requiring a reframe; all nine are plan edits before signature. `BRIEF.md` and `plan.yaml` were not
modified.

## Part A — the six stated constraints

| # | Constraint | Verdict | Delivered by / gap |
|---|---|---|---|
| 1 | FEAT-50, FEAT-46 never referenced | `delivered` | greped the whole feature dir: the only `FEAT-46` occurrence is constraint 1's own text in `notes/answers-2026-08-31-plan.md:28`. `feature.json`, `BRIEF.md`, `plan.yaml`, `STATE.md`, all `runs/` digests: zero |
| 2 | FEAT-45's two fixes stay green | `delivered` | REQ-05; SC-08 (INV-32), SC-09 (zero-collection), SC-10 (both suites, exit status captured separately from `^FAIL ` count, floors 1463/1945 at `75daa3b`). They bind: `test-check-state.py:3203` exits 1 when any case returns false, so SC-08's exit-code command has teeth even though its five named "cases" are pm coinages (**F-07**) |
| 3 | Deterministic regression per issue, provably red | `delivered` | #1056 → T-02 case 4 `empty-red`/SC-02; #1057 → T-05 case 4 `feature-checkout-red`/SC-04; #1058 → T-05 case 7 `digest-clobber-red`/SC-06; plus SC-15's pre-change red for T-08. D-07's marker-free mutant copy **can** fire: `_root()` prefers the env chain over `_bin_dir` (`check-domain.sh:150-154`), so a copy in the gate's own directory roots at the fixture and resolves its sibling imports — this is the failure the existing suite works around by copying `harness_boundary.py` into a tmpdir (`test-check-domain.py:2250-2258`), and D-07 removes it. But the idiom is not concurrency-safe (**F-05**) and cases 5–7 do not pin the writer's identity (**F-08**) |
| 4 | Three canonical commands exit 0 | `partly delivered` — **handling is `delivered`** | The two suite commands are pinned by SC-10. `check-state.sh` is not claimed: SC-11 grades "no violation row names FEAT-50" (form (c)) and says so; SC-12 grades that a ruling or a recorded deferral exists; the three options, PRINCIPLES rule 15's veto on (b), and "neither pm nor the orchestrator may choose" are in `BRIEF.md:226-251`; the gap is restated in `## Verification gaps`. Re-measured: `check-state.sh` exits 1, 51 `INV-` lines, **zero** `FEAT-50` mentions today. The decider is named, the disclosure is at the signature, no option is taken silently. Residual: SC-11's teeth arrive only after approval, and the `panel:` key it then requires is owed by no `T-NN` (**F-09**) |
| 5 | Scope bounded to the three issues and their tests | `delivered` | see the two explicit calls below |
| 6 | Stop conditions not crossed | `delivered` | No task implements (a) or (b); (b) is recorded as available and not recommended with rule 15 cited (`BRIEF.md:75-76`, `plan.yaml` D-08). T-07 **appends** to `DECISIONS.md` and regenerates a generated index — no signed record is rewritten. One adjacency, not a crossing: pm wrote into the `approval:` mapping (**F-01**) |

### T-07 — `in-scope`

It records **this feature's own** three rulings, not unrelated documentation. Three new refusals
installed in two registered gates with no entry leaves the next reader inferring doctrine from three
scripts, which rule 15 and DEC-132 both bite on. The number is resolved at execution time against
the file (D-08), the grading anchor is heading text not `DEC-NNN`, and T-07's verify includes the
`gen-decisions-index.py --stdout | diff` regeneration and the hand-written ` :: ` ruling tail the
generator does not produce. Correctly specified and correctly lane'd (`harness-documentor`).
T-06's playbook sentence is in-scope on the same footing: it is D-06's named compensating control
for the unenforced `Edit`/Bash routes, not new prose.

### T-08 — `in-scope`

Not a review-round indulgence: the operator's own routing table pre-authorises exactly this shape
(`answers-2026-08-31-plan.md:95` — "a new module a gate *imports*" → `team`, "the cutover that makes
the gate use it is `main-session-direct`"), and without prefix selection #1057's remedy is silently
off for every short-form worktree, which this repository has measured in the wild
(`feature-worktree.py:236-248`). That is the remedy, not an addition to it. The
`inflight_registry.feature_root` cutover riding along is the weak half — see **F-02**.

## Part B

**Do the three defects get closed?** #1056 and #1058: yes, within their stated scopes. #1057: yes
only if **F-03** is fixed. Going looking for more of the two-dead-remedies class, three more turned
up, all in T-03: the placement anchor names a block that cannot host the check (**F-03**), the check
does not run at all in a PyYAML-bootstrap session because `domain_check()` is called under
`_run_domain and not _no_parser` (`check-domain.sh:872`) (**F-04**), and "otherwise ALLOWED" does not
say whether `outcome == "shared"` — a second allowance at `check-domain.sh:843` — counts (**F-06**).
Verified as **not** dead: T-04's PRE route does reach `shape_problems()` unconditionally
(`check-domain.sh:1361-1370`, no `has_shape_rules` gate, unlike POST at `:1377`) and problems become
exit 2 at `:1549-1552`; the POST-silent assertion holds because `RE_RUN_DIGEST` is out of
`SHAPE_PATTERNS`; T-03's raw-`rel` premise holds — `classify` returns `rel` unstripped
(`harness_boundary.py:481`) and worktrees nest under the owner root, so the anchored pattern reaches
main-checkout targets only, exactly as REQ-03 claims and no further.

**Anything in the intake unrepresented?** No. Walked it top to bottom: mission, the three verbatim
issues, all six constraints, all three measured premises (including the `feature.json`
`additionalProperties: false` premise, which D-03 answers by rejecting a `worktree` key), both
`75daa3b` baselines and the "count `^FAIL ` separately from the exit status" instruction (SC-10 does
precisely this), the full `--resolve` routing table (matched row-for-row against `plan.yaml`'s
`lanes:`), and the open ruling. `check-plan-routes.py` over this plan reproduces the expected shape:
exit 0, `0 violation(s) across 1 plan(s)`, five `DEVIATION` lines (T-01…T-05), `OK` for T-06/07/08.

**Any SC unverifiable as written?** No `<review_sha>` or `<FEAT>` placeholder is a defect —
`BRIEF.md:83` defines the substitution and `<FEAT>` is a fixture parameter. SC-10's floors are
floors, not equalities, and every task only adds cases, so correct delivery cannot redden them.
Three real problems: **F-07** (SC-08's five case names do not exist in the file), **F-10** (SC-13's
`examined 45 feature dir(s)` is 46 today, and SC-13's own file-argument command prints no `examined`
line at all — verified), **F-02b** (SC-15 declares `evidence: unit` while half its command,
`test-inflight-registry.py`, is in `INTEGRATION_SCRIPTS`, `run-unit-tests.sh:31`).

## Findings

- **F-01 · med · governance.** pm wrote inside `plan.yaml`'s `approval:` mapping: `rulings: []` plus
  two comments (`plan.yaml:11-14`). The template's `approval:` block has no `rulings:` key
  (`templates/plan.yaml:30-40`) and states "Neither pm nor the orchestrator writes it, and
  `check-domain.sh` denies an agent's write of this mapping"; `harness-spec-driven` says "Never the
  `approval:` block". Consequence: the block a signature lives in is no longer byte-attributable to
  the main session, and the mapping-level denial demonstrably did not fire because pm authored the
  file wholesale — so the guard cannot be relied on for the next plan either. The functional need is
  already met by `BRIEF.md:245-251`, which tells the operator to add `rulings:` at signature; the
  pre-created key buys nothing.
- **F-02 · med · scope.** T-08 step 2 replaces `inflight_registry.feature_root`'s loop
  (`:262-269`) with the new helper. #1057 does not implicate `inflight_registry`, and the change is
  observable — a short-form worktree now resolves where it previously fell back to `owner_root`.
  Consequence: a behaviour change to a module outside the three issues lands under a `bugfix` this
  feature's REQs do not require, and SC-15 pins only the ambiguity fallback, not the resolve-where-it
  -previously-fell-back case, so a consumer relying on the old fallback breaks with no criterion red.
- **F-02b · low · verification.** SC-15 declares `evidence: unit`; `test-inflight-registry.py` is an
  `INTEGRATION_SCRIPTS` entry (`run-unit-tests.sh:31`). Consequence: the qa gate looks for unit
  evidence and half of SC-15's assertions are not in that kind, so the criterion can be graded met
  on evidence the declared kind never ran.
- **F-03 · med · dead remedy.** T-03 says "inside the `if _run_domain:` block, positioned so it runs
  ONLY after the domain verdict … is otherwise ALLOWED" and "Inside `if _run_domain:` and nowhere
  else". That block is the fail-closed **import** guard at `check-domain.sh:366-400`; `_verdict`
  does not exist there. The only site that can host the check is the allow branch inside
  `domain_check()` at `check-domain.sh:833-841`, which already hosts a narrowing fragment denial
  and is the correct precedent. Consequence: a doer obeying the anchor literally writes a `NameError`
  — exit 1, which is non-blocking, so #1057's binding is off while looking installed. T-03's own
  verify would catch it, at build time, with the build spine open.
- **F-04 · low · undisclosed scope.** `domain_check()` is called under
  `if _run_domain and not _no_parser:` (`check-domain.sh:872`), so in a PyYAML-bootstrap session
  T-03's binding does not run at all while T-04's digest rule, which lives in the shape phase, still
  does. Consequence: a documented escape hatch (`check-domain.sh:731-739`) silently disables one of
  the three remedies, and neither `plan.yaml` nor `BRIEF.md`'s `## Verification gaps` says so — the
  one place this feature promised to be honest about what its rules do not reach.
- **F-05 · med · determinism.** D-07 places every mutant copy in the shared, tracked
  `.claude/skills/harness/bin/` under a fixed dot-prefixed name, removed in a `finally`. D-08 itself
  states "this harness runs features in parallel". Consequence: two suites running at once — two
  worktrees' qa gates, or a human running the file while the harness does — collide on the same
  mutant path, and one run's `finally` deletes the other's copy mid-read, producing `INCONCLUSIVE`
  or a false red against a correct tree. Constraint 3 asked for *deterministic* regressions. A
  unique suffix per process restores determinism without giving up D-07's import fix.
- **F-06 · low · incomplete rule.** T-03 branches on the verdict being "otherwise ALLOWED".
  `check-domain.sh` has two allowances: `outcome == "allow"` (`:835`) and `outcome == "shared"`
  (`:843`). Consequence: if a feature-artifact path resolves `shared`, the write is allowed and the
  worktree binding never fires — an unbound main-checkout write through the one outcome nobody
  thought to name.
- **F-07 · low · citation rot.** SC-08 grades that "the `no-panel`, `high-open`, `stale-ruling`,
  `reader-missing` and `inv32-red` cases all still pass". `test-check-state.py` has **one** case,
  `case_inv32()` (`:3091`), whose checks cover those five directions; `no_panel`/`high_open` are
  local variables (`:2997-2998`), `stale`/`missing` are others (`:3022`, `:3050`), and `inv32-red`
  appears only inside a print string (`:3107`). Consequence: a grader greping for `stale-ruling`
  finds nothing and either invents a pass or files a false red on a green suite.
- **F-08 · low · under-specification.** T-05 cases 5–7 do not state whether the digest write is
  fired as a governed agent. `domain_check()` runs before the shape phase, so a governed writer with
  no grant on `runs/*/digest.md` exits 2 for the wrong reason — case 5 passes spuriously and case 7's
  mutant then also exits 2, failing the red proof. T-04's own verify avoids this by omitting
  `agent_type`. Consequence: build-time thrash on a task whose intent is otherwise exhaustive.
- **F-09 · low · unowned dependency.** SC-11 states that INV-32 "binds FEAT-50's own approval to
  carry a complete `panel:` result", and no `T-NN` produces that key — it is the panel segment's
  out-of-band transcription. Consequence: the moment the operator signs, SC-11 depends on an
  artifact the plan does not name an owner for, and a reader six months on cannot tell whether it
  was owed or forgotten.
- **F-10 · low · stale baseline.** SC-13 records `examined 45 feature dir(s)` at `75daa3b`; it is 46
  now, and SC-13's own command (a plan-file argument) emits no `examined` line at all — verified.
  Consequence: a non-graded sentence carries a number the criterion's own command cannot produce, so
  a later reader cannot tell drift from falsification.
- **F-11 · low · incomplete anchor.** T-04 calls the tuple threading "the single call site's
  `targets` tuples (check-domain.sh:1359-1420, 1546-1547)". There are **three** construction sites:
  PRE `:1369`, POST named `:1381`, and the sweep append at `:1505`, which both ranges miss; the
  unpack at `:1546` is a strict 3-tuple destructure. The intent's prose does name the sweep route, so
  this is an anchor defect, not an omission. Consequence: a doer following the line numbers breaks
  every Bash sweep with a `ValueError` → exit 1 → the sweep silently off. Loud, because the existing
  sweep cases (`test-check-domain.py:1087-1091`, `:2092-2274`) would go red.
