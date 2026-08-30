# Security re-review — regate pin `37676244` — 4 named files

**BLUF: clean. Zero findings, no control weakened, gate integrity intact on measurement, no
credentials.** All four files verified with identity-level evidence (byte-diffs, regenerated output,
process exit codes), not read-and-conclude. One numeric claim in the handed-down contract is
unsupported by measurement — flagged below, substance unaffected.

## Per-file verdict

1. **`.harness/harness.json`** — CLEAN. Python-parsed `test_kinds.integration.detect` at all three
   shas: branch(4c192ab)=29, main(6d6d1cea)=26, pin=27, with `main ⊆ branch` (main_only = ∅). Pin =
   main's 26 + `test-check-decision-anchors.py` (FEAT-38's own addition, confirmed present in tree at
   pin). The two branch-only entries `test-context-watch-cli.py`/`test-context-watch-hook.py`
   (correctly excluded from pin) confirmed **absent** from the tree via `git cat-file -e`. Resolution
   is set-correct.
2. **`.claude/skills/harness/bin/run-unit-tests.sh`** — CLEAN. Parsed `UNIT_SCRIPTS`(26) /
   `INTEGRATION_SCRIPTS`(26) bash arrays at pin; `INTEGRATION_SCRIPTS` basenames == harness.json's
   `detect` list minus the `tests/integration/**` glob, exact set equality (`∆=∅` both directions) —
   `--check-kinds` genuinely agrees with harness.json, as claimed. Fail-open audit of the full script
   (not just the diff hunk): `set -uo pipefail`, no `-e`; every test invocation's `$?` is checked
   explicitly, no `|| true` / swallowed status anywhere; `--check-kinds`'s drift detector and kind
   cross-check both exit 2 (fail-closed) on mismatch/unparseable config; `cmd` values are fixed
   operator-authored literals, unchanged by this diff, not templated from any external input.
   Verified by direct test: `python3 <missing-file>` exits 2, so even a stale dead-file registration
   left by a bad merge would fail the suite LOUDLY (broken CI), never silently pass — the "silent
   narrowing" framing in the dispatch does not apply to this specific mechanism; the correct
   exclusion was still necessary, just for CI-breakage reasons rather than fail-open reasons.
3. **`.harness/harness/docs/DECISIONS-INDEX.md`** — CLEAN, identity-level. Ran
   `gen-decisions-index.py --stdout` against the pin's own tree (read-only, `--stdout` avoids writing)
   and diffed against `git show 37676244:...DECISIONS-INDEX.md`: **byte-for-byte equal** (41812/41812
   chars). This is the strongest possible proof the file was regenerated, not hand-merged. Separately
   confirmed against 4c192ab: 188/188 entries match, only DEC-201's tags/refs changed content (adding
   the `skills` tag and `DEC-204` ref) — exactly what the fold's DEC-201 amendment would produce.
4. **`.harness/harness/docs/DECISIONS.md` (DEC-159/198/201 only)** — CLEAN. `git diff
   141eca6..37676244` scoped to these three entries only (212 total diff lines, no hunks outside
   them); confirms the three amendment blocks were folded into their entries' prose with no other
   change, matching the prior code-reviewer read-back
   (`notes/review-harness-code-reviewer-readback-fold.md`) which I did not re-run but did spot-check
   at the security lens below.

## Security lens on DEC-159/198/201

- All three entries describe an **advisory-only** mechanism (`orchestrator_context_warn_tokens` /
  the in-flight context warning): explicitly "advises and never refuses," "no branch stops, no
  dispatch is denied, nothing is blocked on it" (DEC-198, unchanged by diff). Not a gate — its
  relocation from a retired Claude `PostToolUse` hook to an OMP `tool_result` injection is a delivery
  refactor with no enforcement semantics to weaken.
- Verified every path/symbol the fold's new prose asserts exists, actually exists at the pin (not
  assumed): `probe-omp-session-accessor.py` ✓, `FEAT-44-omp-context-advisory/evidence/README.md` ✓,
  `.omp/extensions/harness-hooks.ts` ✓ (containing `DEFAULT_CONTEXT_WARN_TOKENS`,
  `resolveContextWarnTokens`, `getSessionFile` — all three symbols present) ✓. Retired paths correctly
  asserted absent: `context-watch.py`, `context-watch-hook.py` — both confirmed absent via
  `git cat-file -e`.
- Read `.claude/settings.json` at the pin directly: the six real hook registrations
  (`check-domain.sh` Pre+Post, `bash-write-guard.sh`, `branch-create-gate.sh`, `gh-close-gate.sh`,
  `dispatch-guard.sh`, `validate-digest.py`) are untouched by this fold and outside the diff's blast
  radius — the enforcement surface is unaffected by anything in DEC-159/198/201.
- No new supersession, capability grant, or auth-relevant clause introduced by the fold text.

## Secrets/credential scan (P-14)

Ran a Python regex sweep (`(?i)(api[_-]?key|secret|password|token|bearer|credential|private[_-]?key|
-----BEGIN|ghp_|sk-...)`) over the pinned content of all four files and separately over the
`141eca6..37676244` DECISIONS.md diff hunks. Every hit is a false positive from "context token"
(LLM token-count) vocabulary or the `orchestrator_context_warn_tokens` config key name. Zero
credential-shaped values.

## Contract claims found FALSE or unsupported

- **"Reported 28 -> 27" for `test_kinds.integration`** — I cannot reproduce 28 from any measured
  state. Branch(4c192ab)=29, main(6d6d1cea)=26, pin=27. 28 does not match branch, main, pin, or their
  naive union (29). It may describe an earlier pre-branch baseline I have no commit to check, but as
  stated it is **not supported by measurement at any of the three cited shas**. The *substance* of the
  claim — correct exclusion of the two dead registrations, correct inclusion of the one new one, both
  arrays agreeing with `--check-kinds` — is independently verified TRUE regardless of this count.
- All other contract claims (union-not-taken reasoning for files 1–2, "purely generated anchors" for
  file 3, DEC-201's cited evidence paths) verified TRUE by direct measurement, not merely plausible.

## Open questions

None blocking.

```yaml
VERDICT: PASS
DIGEST:
  headline: "All four in-scope files verified clean at identity level; no control weakened, no credentials; one contract count (28) unsupported by measurement but substance confirmed true"
  in_scope: true
  scope_reason: "Delta is a merge-conflict resolution touching the project's sole blocking test gate (harness.json/run-unit-tests.sh) plus governance docs — gate integrity is a security property even with no classic injection surface"
  severity_max: info
  findings: 0
  must_fix: []
  threat_model:
    - { boundary: "test-gate config (harness.json detect / run-unit-tests.sh arrays) — silent narrowing of what CI discovers", stride: T, mitigated: true }
    - { boundary: "run-unit-tests.sh loop — fail-open on script error/crash", stride: D, mitigated: true }
    - { boundary: "DECISIONS-INDEX.md — stale/hand-edited generated file diverging from source", stride: T, mitigated: true }
    - { boundary: "DEC-159/198/201 fold — relaxing or misdescribing an enforcement mechanism", stride: I, mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/review-harness-security-reviewer-regate-pin.md
```
