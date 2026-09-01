# FEAT-50 — plan fix cycle 1, dispositions (final pre-panel)

**All thirteen findings dispositioned; F-L1, F-03, F-05 and F-02 applied. `plan.yaml` loads under
`harness_yaml.load_plan`, `check-plan-routes.py` exits 0 with `0 violation(s) across 1 plan(s)`,
max budgeted-field count 45 (T-03) against 50, `approval.status: pending`, no `panel:` key.**
Counts after the edits: 7 REQ, 16 SC, 8 tasks, 8 decisions.

## The INV-32 ruling's home — `notes/answers-2026-08-31-plan.md` (F-L1, applied)

Took the orchestrator's recommendation. `approval.rulings` is validated for panel-finding
overrules only: `check-state.sh:189-204` demands each entry carry a `finding` id present in
`panel.findings`, a non-empty `who`, and a `YYYY-MM-DD` `date`, so `{id: INV-32, choice: c}` emits
two rows naming FEAT-50 and the operator's signature becomes the act that falsifies SC-11. DEC-44
already makes the answers file the durable home for an operator answer and this feature has one.
`BRIEF.md`'s open-ruling section now names that file and the exact five-key section shape; SC-12
grades that section and nothing else; SC-11 and SC-12 are satisfiable together because the ruling
lands in a file `check-state.sh` never opens.

**Evidence for zero new INV-32 rows.** Read `check-state.sh:176-220` at source. Line 189 is
`rulings = approval.get("rulings", [])`, so an ABSENT key is the empty list and the loop at :194
iterates zero times — the only INV-32 rows a signature can then produce come from the `panel:`
block itself, which the panel segment supplies. `approval.rulings: []` is therefore **dropped**
(F-01): nothing grades it any more, the template has no such key, and its absence and its
emptiness are the same input to :189.

## Dispositions

| # | Sev | Disposition |
|---|---|---|
| F-L1 | high | **applied** — ruling re-homed to the answers file; SC-12 rewritten; `rulings:` key and its two pm-authored comments removed from `approval:` |
| F-01 | med | **applied** — same edit; `approval:` is back to the template's four keys, byte-attributable to the main session |
| F-02 | med | **applied** — T-08 step 2 bounded: signature, return type and fallback contract unchanged, no other function touched, and the verify now asserts the inline basename loop is gone, the call goes through the seam, `feature_root` is defined exactly once, and the no-worktree fallback still answers `owner_root`; intent orders `test-inflight-registry.py` run before and after with no case added, modified or deleted. New SC-16 grades that boundary |
| F-02b | low | **applied** — SC-15 narrowed to `test-harness-boundary.py` (`UNIT_SCRIPTS`); the `test-inflight-registry.py` half moved to SC-16 with `evidence: integration` |
| F-03 | med | **applied** — the false anchor sentence DELETED, not supplemented. T-03 now anchors on the allow branch at `check-domain.sh:835-841`, where `_verdict` is bound and `rel` is bound at :833, called immediately before `approval_guard(rel, agent)` — and states why that guard sits there: a check on the deny path never fires for an agent holding the grant. The intent names `:366` explicitly as the import guard NOT to write into |
| F-04 | low | **applied** — disclosed in `## Verification gaps` and in T-03's placement constraints: `domain_check()` runs under `if _run_domain and not _no_parser:` (`:872`), so the binding is off in a PyYAML-bootstrap session while T-04's shape rule still runs |
| F-05 | med | **applied** — D-07 now requires a mutant name unique per process (`os.getpid()`), propagated into T-02 case 4 and T-05 cases 4 and 7. `test-check-state.py`'s fixed-path idiom carries the same exposure and is recorded in D-07 as NOT fixed here: that file is run unchanged as the FEAT-45 regression (SC-08) and editing it leaves the three issues |
| F-06 | low | **applied** — the check is one function called from the `shared` branch at `:843-848` as well as the allow branch; D-85's second allowance is named |
| F-07 | low | **applied** — SC-08 now cites the one real case, `case_inv32` (`test-check-state.py:3091`), names the five directions as directions inside it, and grades on the suite's exit status plus `grep -q 'def case_inv32'` |
| F-08 | low | **applied** — T-05 cases 5–7 fire with NO `agent_type`, as T-04's own verify does, with the failure mode spelled out: a governed writer without a grant on `runs/*/digest.md` is denied by `domain_check()` first, so case 5 passes spuriously and case 7's mutant also exits 2 |
| F-09 | low | **applied as disclosure** — a gaps bullet records that the `panel:` key SC-11 depends on is the panel segment's out-of-band transcription and is owed by no `T-NN` by design; before approval INV-32 does not reach this plan at all (`:176-179`). No task added: producing `panel:` is not this feature's work |
| F-10 | low | **applied** — SC-13's `examined 45 feature dir(s)` is now a dated FLOOR, with the reason stated: it was 46 on 2026-08-31, and the file-argument command the criterion grades emits no `examined` line at all |
| F-11 | low | **applied** — T-04 step 3 names all THREE construction sites (PRE `:1369-1370`, POST `:1381`, sweep append `:1505`) and the strict 3-tuple destructure at `:1546`, with the ValueError-to-exit-1 consequence |

Nothing rejected. No finding needed one: each was either a real defect or a real undisclosed limit.

## One measurement worth carrying

SC-16's absence-grep was **non-discriminating as first drafted**. `grep -c
'os.path.basename(worktree)'` returns **0** against today's module — the parentheses are read as a
regex group — so the check would have greened on the pre-change file. `-cF` returns 1. The
criterion now specifies `-F` and records the measurement beside it.

## Open questions

None blocking. The operator's INV-32 ruling remains the one blocking input, unchanged in substance
and only relocated.
