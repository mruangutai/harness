# Security review — BUG-1898 validate-c5

**FAIL.** The c5 delta closes the c4 persona/parent omission for the observed direct nested row, but the oracle still accepts a deeper lineage as the sole nested child while omitting it from cross-persona validation. SC-07's retained operator receipt is PASS 29/29, yet this remaining synthetic false-positive keeps the security gate open.

## Pin, ranges, and scope

- Reviewed SHA: `7893fe7a23e493dcd1554e439f28e3c9832b4de4`.
- Canonical range: `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..7893fe7a23e493dcd1554e439f28e3c9832b4de4` (merge-base of `origin/main` and the pin; 65 paths, +6628/-554).
- Focus range: `f73c999482fd931021a3eb50d30aa8ab2a885283..7893fe7a23e493dcd1554e439f28e3c9832b4de4`; the shipped-code delta is only `tests/manual/probe-inflight-claim-lifecycle.py` (+22/-6), alongside retained evidence/metadata.
- In scope: sampled runtime identity/persona/parent data crosses into the SC-07 merge-gate oracle. This surface was security-reviewed at c4; c5 changes the previously failed security assertion.

## Finding

### F-SEC-C5-01 — deeper lineage bypasses the nested persona/parent oracle (`med`, must-fix)

- **Kind:** substance. **Scope:** task. **Owner task:** T-04. **Reader:** security-reviewer.
- `tests/manual/probe-inflight-claim-lifecycle.py:433-465`: `nested_ids` accepts every sampled id with prefix `governed + "."`, including `Nest.Probe.Deep`. `crossed_rows`, however, validates nested identity only when the id's immediate lexical parent is itself in `governed`. A deeper id has parent `Nest.Probe`, so it reaches neither the nested check nor the direct governed/plain checks.
- **Concrete failure scenario:** a runtime regression produces the sole sampled lineage row `agent_id=Nest.Probe.Deep`, `agent=harness-qa`, `parent_agent_id=Nest.Probe`, rather than the dispatched direct `Nest.Probe` lead. `len(nested) == 1` passes, `crossed_rows == []` passes, settlement/no-row can pass, and the receipt can claim that the nested row is the dispatched lead under its governing parent although the wrong persona and lineage depth were never checked. A reviewer can accept SC-07 on false identity-boundary evidence.
- Fix the oracle by defining direct nested rows once (exactly one dot beyond a governed id, or an explicit expected child id) and treating every prefixed-but-not-direct lineage row as crossed; validate the sampled row's persona and `parent_agent_id` against that same governing id.

## Offline oracle and receipt evidence

- `git diff --exit-code 7893fe7a... -- tests/manual/probe-inflight-claim-lifecycle.py` → exit 0, proving the exercised worktree probe is byte-current with the immutable pin.
- Synthetic import/calls at the pin → **PASS 9/9**: dotless `Plain` is excluded from `nested_ids`; exactly `Nest.Probe` is the one lineage id; `harness-eng-lead` with `parent_agent_id=Nest` is green; wrong persona and wrong parent are red; a real plain row is red; top-level orchestrator and correct nested rows are green; settled empty registry is green.
- Adversarial synthetic call → `nested_ids=['Nest.Probe.Deep']`, `crossed_rows=[]`, so both the one-lineage and no-crossing checks would pass for a wrong-persona deeper row. This is the remaining fail-open oracle path.
- The retained final operator receipt is `notes/live-omp-probe.md` run `2026-09-25T12:54:34+00:00`, **PASS 29/29**. Its S3 observed row is `Nest.Probe`, persona `harness-eng-lead`, parent `Nest`, and therefore matches the fixed direct-row oracle. SC-07 is stated only from that receipt.
- This differs from the immediately preceding `2026-09-25T12:52:48+00:00` **FAIL 28/29**, where dotless top-level `Plain` was misclassified as nested/crossed. The pinned c5 logic excludes dotless ids and does not reproduce that failure.
- No live/credentialled probe, formatter, linter, project-wide build, or project-wide suite was run.

## Other OWASP/STRIDE checks

No new dependency, request/redirect, SQL/shell/template interpolation, export, path traversal, auth route, credential value, PII, or secret logging is introduced. Credential-shaped review found only retained API-key existence lookup; no value is emitted. Input is bounded to in-memory probe samples. The material risk is tampering/repudiation at the evidence boundary described above, not production credential or data exposure. INV-43 seq-3 and the operator-owned dirty overlay remain declared residuals, not findings.

| Boundary | STRIDE | Mitigated | Basis |
|---|---|---:|---|
| Direct nested sampled row → SC-07 persona/parent assertion | T/R/E | yes | Correct `Nest.Probe` persona and governing parent are rejected on mismatch; dotless ids are excluded. |
| Arbitrarily deep prefixed lineage → SC-07 assertion | T/R | no | Prefix collection and immediate-parent validation use different sets, permitting the demonstrated bypass. |
| Credential environment/store → receipt | I | yes | Only credential existence/count is read; values are not printed. |
| Settled identities → final registry emptiness | T | yes | Correct nested and top-level ids are included in the no-row check for the observed direct lineage. |

## Cleanup

No archive, temporary directory, scratch checkout/worktree, registry mutation, or live session was created. Scratch cleanup: **not applicable; nothing created**. Only this persona-owned review artifact was written.
