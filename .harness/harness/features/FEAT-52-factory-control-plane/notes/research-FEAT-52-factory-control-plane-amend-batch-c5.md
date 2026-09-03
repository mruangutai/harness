# Amend batch c5 — all 7 items APPLIED, 0 refused, 0 send-backs

**Applied 7, unapplied 0, 7+0=7.** Both digests were unambiguous on every item, so nothing was
refused. `plan.yaml` took six task-field amends through `plan-merge.py amend` (compare-and-swap,
no stale-hash refusals, no retries); `BRIEF.md` took one pure insertion. **Nothing gates either
way** — INV-32 passed before this batch and passes after it. The operator still signs.

## Item by item

|id|field|before → after|
|---|---|---|
|`T-01-files`|`files:`|2 entries → 3; appended `.claude/skills/harness/bin/test-check-domain.py`, both existing entries byte-identical|
|`T-01-verify`|`verify:`|1 line → 2, `&&`-chained; now invokes `test-check-domain.py` (`plan.yaml:105-107`)|
|`T-01-intent`|`intent:`|+13 lines: new step 3 after step 2's bullet list, before the existing "Do NOT register the test file anywhere new" paragraph. **Both "Do NOT register" paragraphs coexist** — the pre-existing one about `test-inflight-registry.py`, and step 3's own about `test-check-domain.py`|
|`T-11-verify`|`verify:`|2 lines → 3; `check-instruction-paths.py .omp/agents .claude/agents` prepended in T-04's directory shape (`plan.yaml:849-852`)|
|`T-14-intent`|`intent:`|opening sentence only: "no non-zero exit on any branch." → "no literal non-zero exit statement." (`:1032-1033`). Title NOT edited; the "second clause of SC-02" sentence NOT edited; line count unchanged (0 delta)|
|`T-15-fixtureA`|`intent:`|FIXTURE A bullet only, +3 lines: now says the wrongly-anchored token repeats `min_occurrences` times, spelling out row 6's TWICE. FIXTURE B and FIXTURE C verified intact|
|`BRIEF-SC-15`|`## Success Criteria`|inserted after SC-14, before `## Verification gaps` (`BRIEF.md:198-209`). `verify: automated  evidence: integration`|

## The three lead corrections — all three carried

1. **T-01's `verify:` gained the invocation**, not just the file. Without it the R1 case would land
   in a file no task's verify runs — PF-afe3e3d6's own defect reintroduced by the fix for R1.
   Field verbatim, `plan.yaml:106-107`:
   `python3 .agents/skills/harness/bin/test-inflight-registry.py \` / `  && python3 .agents/skills/harness/bin/test-check-domain.py`
2. **SC-15 is `evidence: integration`, not `unit`** — `test-check-domain.py` sits in
   `run-unit-tests.sh:31` INTEGRATION_SCRIPTS and in `harness.json:121` integration `detect`. And
   its assertion **pairs** the ALLOW-from-a-product-cwd with the same-fixture same-cwd REFUSE of the
   in-product twin, because `exit 0` alone is also what `check-domain.sh` returns for "no verdict".
3. **The phrase "no literal exit statement anywhere" appears nowhere in any amend text** —
   asserted programmatically over both new intents. The recorded finding summary carrying it
   (`plan.yaml:1241`) was left byte-untouched; correcting it would change its content-hash id.

## Two defects I caught while applying, not in either digest

- **A naive prepend of T-11's checker line would have shipped a shell bug.** The former first
  command had no leading `&&`, so prepending line 1 above it produced
  `check-instruction-paths.py … \` newline `python3 sync-agent-adapters.py --check` — one
  concatenated command, not two conjuncts. The former first command must GAIN the `&&` it never
  carried. Final block: 3 lines, 2 `&&`, and the trailing `python3 -c` one-liner **copied from the
  parsed field, never retyped** (byte-identity asserted, not eyeballed).
- **`git diff` cannot prove "no existing criterion altered" here.** The whole feature directory is
  UNTRACKED (`git status --porcelain` → `?? .harness/harness/features/FEAT-52-factory-control-plane/`),
  so a diff is empty for a changed file and an unchanged one alike — it reads like proof and is not.
  The BRIEF claim rests instead on the edit being a pure insertion plus an asserted
  `SC-01..SC-15` sequence equality.

## Verification (commands, not claims)

- `panel` **BYTE-IDENTICAL**: `sha256 4eb41f18b0ad70a299b2ab056a8c217d40dce8270c235cdaabd14d6208c978bf`
  before and after, over `yaml.safe_dump(panel, sort_keys=True)`. `cycle: 5`,
  `last_run: 2026-09-01-02-validator`, 17 findings; finding ids, severities and dispositions each
  compared element-wise as lists — all identical.
- `yaml.safe_load`: `len(tasks) == 15`, `len(decisions) == 8`, `status: plan`,
  `approval == {'status': 'pending'}`.
- Both amended `verify:` round-trip as literal `|` blocks with newlines intact — `T-01` 2 lines,
  `T-11` 3 lines; `verify: |` indicators confirmed in the raw text at `:105` and `:849`.
- `BRIEF.md`: 15 criteria, sequence exactly `SC-01..SC-15`, `## Approval` still `status: pending`.
- `check-plan-routes.py <this plan>` → **0 violations, exit 0**. The DEVIATION lines are the
  expected DEC-174 carve-out output (only VIOLATION gates); T-01's new file falls inside the same
  granted-but-`main-session-direct` set, so it added no finding.
- Traceability re-derived, not assumed: T-01 `[REQ-06]`, T-11 `[REQ-02, REQ-06]`, T-14 `[REQ-05]`,
  T-15 `[REQ-02, REQ-04, REQ-06]` — every REQ present in `BRIEF.md`. **SC-15's carrier is T-01**,
  which already traces `REQ-06` and whose step 3 now delivers the case, so no `traces:` edit was
  needed.

## Not done, deliberately

No commit, no signature, no station change, no new panel run, no production code. `panel:`,
`approval:`, `status:`, `decisions:`, `lanes:`, `source_issues:` and all 11 untouched tasks were
never opened for write.

## Open

Nothing blocking. The 06 digest's Q1/Q2 stand and are the operator's: all 7 items are
discretionary, and **SC-15 is a new success criterion** — the operator should be told an SC was
added, not only that tasks changed. It signs free with this batch because `BRIEF.md` is unsigned;
added after signature it would need an `approval.rulings` entry.
