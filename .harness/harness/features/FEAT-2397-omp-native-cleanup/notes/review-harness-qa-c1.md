# QA gate — FEAT-2397 — run r-20261122-5-validate-validator (c1) — pin 9c380403

**VERDICT: PASS.** At the pin the unit kind (67/67), integration kind (95/95) and typecheck are green, each in my own managed pinned checkout. Fresh full check-state exits 0 with positive discovery (34 tracked features). The two c0 unit regressions are fixed. Disclosures below: the committed env-i clone logs are red but baseline-equivalent, and that is not CI-green evidence.

Policy: repo mruangutai/harness, commit 9c38040397bb115583e71b13f1a7ca4bf2f10c2e, path `.harness/harness.json` (git show). Matrix: T-01 and T-04 cross_module (unit + integration); T-02 config (integration if touches_config_shape); T-03 and T-06 scaffolding; T-05 docs. Kinds: unit active, integration active, typecheck active; functional and eval excluded (DEC-187); component and ui unresolved with no triggering task; omp_session_accessor locally_run (SC-10 uat, covered by T-06 receipt audited at c0).

## Phase 1 (BRIEF and plan only), and result
Expected tests: SC-01 bytes parity and four-file outcomes; SC-02 single decode and retry; SC-03 agent/task, legacy `stop_hook_active` rejected, claim retention; SC-05 root-negative preservation; SC-06 perCallModel=="off"; SC-07 finite usage.tokens; SC-11 probe identity/measurement tables. Phase 2 found no gap against that list. Changed migration tests `test-lead-stop-and-wake.py` and `test-no-distribution.py` are in the unit manifest's `completed_files` and green.

## Runner receipts (DEC-255), recorded once each, serial, one host
Checkout: `.pins/FEAT-2397-omp-native-cleanup--r-20261122-5-validate-validator--harness-qa`, HEAD 9c380403, clean. `HARNESS_AGENT_TYPE`, `HARNESS_PROJECT_DIR` and `CLAUDE_PROJECT_DIR` unset. Command: `python3 .agents/skills/harness/bin/run-unit-tests.py --kind <k> --shard 1/1 --manifest <F>/runs/r-20261122-5-validate-validator/qa/manifest-<k>.json`.

| kind | receipt (tested_commit 9c380403) | selected/completed | runner_exit | wall |
|---|---|---|---|---|
| unit | qa/manifest-unit.json | 67/67 | 0 | 23.2 s |
| integration | qa/manifest-integration.json | 95/95 | 0 | 147.7 s |
| typecheck | `bun run typecheck` (tsc --noEmit) | n/a | 0 | n/a |

**Disclosure — first integration run was red, rerun green.** The first integration run (self-captured output sha 4a84.. is unit; the red integration output was `/tmp/qa5-int.txt`) exited 1 on exactly one script: `test-typescript-typecheck.py` — `no installed compiler at <pin>/node_modules/.bin/tsc: run bun install --frozen-lockfile`. It is a missing prerequisite in a fresh pinned checkout, not a code failure. I supplied it (`bun install --frozen-lockfile`, 7 packages), reran integration once, and it was green with the receipt overwritten by the runner's own file. I did not hand-edit any receipt. Full outputs are session-local (`/tmp/qa5-unit.txt`, `/tmp/qa5-int2.txt`); QA cannot write logs under `runs/`.

## Clone base/head comparison (from committed receipts, not rerun)
`c1-evidence/unit-522c94b2-clone-cleanenv.txt` (base, 66 files) vs `unit-b9a8c3ad-clone-cleanenv.txt` (head, 67 files), read via git show at the pin:
- Non-zero scripts are identical: `test-factory-config.py` and `test-omp-hooks.py`, both exit 1, in both logs.
- The FAIL-line set per script is identical (same md5 of the sorted `script: FAIL…` rows). The BUG-1290 5a/5b/5c lines in `test-factory-claim-mutation.py` are deliberate mutation-proof prints in a passing script (exit 0) and appear in both.
- The only difference in the script list: head adds `test-session-accessor-probe.py` (exit 0).
- So the clone-run reds are baseline-equivalent and pre-existing in that environment (standalone clone under /var temp, `env -i`). They are not green CI. In my pinned checkout, with the runner env cleaned, both scripts passed and the unit runner exited 0. I did not reproduce the clone reds and I do not claim CI is green on a clean runner; the unit receipt above is the only fresh evidence.

## Fresh evidence at the pin
- **check-state (SC-12 INV26):** `git ls-files '.harness/*/features/*/feature.json'` = 34 (positive); `check-state.py` exit 0; five output lines, all `note` rows (INV-32 and INV-17). This is fresh execution at 9c380403 in my pinned checkout. It is distinct from the pinned receipt `c1-evidence/check-state-b9a8c3ad.txt` (ref b9a8c3ad, same 34/exit 0) and from the post-pin README append (not at the pin; not used). Files differing between b9a8c3ad and the pin are evidence notes only, so the source is identical.
- **Other T-05 cumulative gates at the pin (exit 0):** DECISIONS-INDEX regeneration diff clean; canonical-reader audit 0 unresolved across 101 files; instruction paths 68 files, 0 violations; layout 2 surfaces clean; plan route check 0 violations (the T-06 DEVIATION row is the disclosed GC-03 #2387 team-config provision wording, not a failure).
- **SC-04 / T-02 transient check at the pin:** the plan's CHECK heredoc, extracted from the pinned plan.yaml, exits 0 with 17 OK, 0 FAIL. Committed base receipt shows 16 FAIL; committed f5c89121 receipt shows 17 OK. All eight T-02 target files are blob-identical between f5c89121 and the pin.
- **Code-grade binding (SC-12):** I ran canonical `code-grade.py --base 522c94b2 --head 9c380403 --json`: 93 records, 93 passing, 0 ungraded. Its normalized JSON is identical to the committed `grade-522c94b2-to-b9a8c3ad.json`; no non-evidence file changed between b9a8c3ad and the pin, so the committed blobs bind to the pin. The canonical selector (`gated_set`) takes new functions and those whose grade regressed against the base pre-image. The c0 changed-body selector (155 then) takes any function whose body changed. Independently, I graded every changed-body function (171 by qualname body-hash against base, 78 beyond the canonical 93) with the same grader and bars: zero are below bar. SC-12's literal "new/changed" wording is therefore met under both selectors. Binding rule used for the verdict: canonical `code-grade.py` for the report, the superset as a literal-reading check.

## Fail-first audit (verify: automated)
Tier labels per c0 note; the builder's retained runs remain the evidence and were re-read, not rerun (the user directed no reruns of reported failures).
| SC | evidence (notes/…) | tier |
|---|---|---|
| SC-01 | t01-red-green/red-A (bytes/drift), red-B (subprocess checker), red-C (mutants m1–m4) | natural RED (semantic) for A and B; mutation tier for parity |
| SC-02 | red-D | natural RED, semantic |
| SC-03 | red-E dispatch-guard, **red-H validate-digest**, red-I, red-J, red-K | natural RED, semantic |
| SC-05 | unchanged-preservation exception (BRIEF Verification gaps): no new baseline red claimed; the T-02 transient is RED at base (16 FAIL) and GREEN at the pin (17 OK, freshly run) | preservation exception, not a fabricated red |
| SC-06 | red-G (live pin, absent/on/eval) | natural RED, semantic |
| SC-07 | red-L (accessor rows signature-absent; handler rows semantic) | mixed |
| SC-11 | t04-red-green/red-baseline-2346a777 (signature-absent), red-mutants | signature-absent natural RED plus mutation |

**c0 SC-03 red-H correction confirmed at the pin.** `red-H-validate-digest-baseline.txt` carries natural reds: case 3 "truthy legacy `stop_hook_active`, an invalid digest still exits 2" (exit 0), case 3 "correction completes the same job and releases its claim", and case 9 "truthy legacy with a live child is refused (exit 2)" (exit 0). The claim-retention `ok` rows pass at base because the old bypass retained claims too; they are preservation. The c0 gap about SC-03 claim retention stays withdrawn.

The c1 migrations (`test-lead-stop-and-wake.py`, `test-no-distribution.py`) are fixes of c0 reds, not new SCs. Their red evidence is the c0 run: failing at the c0 pin and green at base, now green at the pin.

## Residual items for the lead (not blockers for this gate)
- The clone-run reds are baseline-equivalent host-environmental behaviour (see above), not feature-caused; I verified the comparison from receipts only.
- Independence: the fail-first runs are the builder's own captured runs. I reran only the T-02 transient, grading, check-state and the matrix kinds.
- SC-04, SC-08, SC-09, SC-12 inspection items and the SC-10 uat acceptance are for other panel members and PM.
- Installed control-plane hook is the pre-change copy; candidate behaviour is claimed only from tests run at the pin.

## Principles applied
Verification-rules: no green claimed from the first integration run; the prerequisite was supplied and the runner's own rerun is the receipt. Baseline-equivalent reds are reported as such, not as green CI. Fail-first tier labelled per SC.
