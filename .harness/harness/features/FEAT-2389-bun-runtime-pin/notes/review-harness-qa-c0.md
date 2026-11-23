# QA gate — FEAT-2389 — run r-20261122-2-validate-validator — cycle c0

**BLUF: PASS (gate-only).** Pin fea15955785ac4d9202cccb43302c8ffefdc8152 (base 51c2efeb). Literal T-01 verify exits 0 at the pin; red baseline reproduced. SC-04 is pending-ci, NOT met; Main must confirm PR #2433 CI before merge.

## Phase 1 (BRIEF/plan only)
Expected: red equality check at baseline (packageManager absent, exit 1); green equality + `bun --version`=1.3.14 + typecheck at pin; 3-file diff (package.json one key, one workflow comment line, one README sentence); PR CI run. All SCs `verify: inspection`.

## Matrix
T-01 change_type=config → harness.json: always [], when integration if touches_config_shape. Judgment: adding a new string key to package.json (not harness.json/fleet.yaml; no gate script reads it) is not a container-shape change, so integration is not strictly required and unit is not required. The digest gate nonetheless refuses `suite: pass` without a unit/integration receipt (config row carries a `when`), so QA added `integration` as a conservative floor-raise and ran it once at the pin: `run-unit-tests.py --kind integration --shard 1/1 --manifest runs/r-20261122-2-validate-validator/qa/manifest-integration.json` exit 0, 95 files, ALL PASSED (HARNESS_AGENT_TYPE unset per G-07), tested_commit fea15955785ac4d9202cccb43302c8ffefdc8152, tree clean. Receipt is the runner's own file, unedited. Typecheck kind (active) run once as the task verify. Integration is regression evidence only; it does not discriminate SC-01..03.

## Evidence
- Provisioned: `bun install --frozen-lockfile` in managed pin, lockfile unchanged, tree clean after.
- Green at pin: literal verify block → packageManager ok, bun 1.3.14, `tsc --noEmit` ok, exit 0.
- Red (SC-01): `notes/receipts/T-01-red.txt` (head 51c2efeb, `packageManager: null`, exit 1); own reproduction on `git show 51c2efeb:package.json`: null, equality assertion exit 1 (genuine, jq ran). Natural RED, semantic. Green receipt `T-01-verify.txt` says "head + working tree" (pre-commit); re-run at the committed pin.
- SC-02: diff adds exactly one comment line before first Install Bun step; `oven-sh/setup-bun@v2` invocations unchanged, input-free. Met.
- SC-03: README adds one sentence (wrapped over 3 lines): runtime pin tracks production OMP host, bumped by hand only on host upgrade, never Dependabot. Met.
- Preserved: bun.lock, .github/dependabot.yml untouched; package.json diff is only the packageManager line.
- SC-04: pending-ci (PR #2433). Not verified here.

## Findings
None blocking. Observation (T-01): green receipt predates commit; re-verified at pin.

## Cleanup
Pin removed on return.
