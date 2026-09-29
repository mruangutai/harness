# Security review — FEAT-70 cycle 0

**PASS.** The security-sensitive pinned delta was audited at review SHA `138d11a4ac2b762a57bf0800bea2db95fc5d878a` against baseline `9e531b34fc04f752cedf51586dc13c460580901a`; no exploitable security regression was found.

## Scope and census

`git diff --name-status 9e531b34fc04f752cedf51586dc13c460580901a..138d11a4ac2b762a57bf0800bea2db95fc5d878a` reports **40 changed paths**: 12 CLI/runtime paths (the thin `plan-merge.py` entry plus 11 files in `plan_merge/`), 25 feature/evidence/receipt paths (including five executable receipt scripts), and three integration support/fixture paths. The delta is security-scoped **in** because it accepts operator- and agent-authored argv, paths, YAML, lead digests, and plan anchors; mutates signed plan and judgement records; invokes subprocesses; and emits logs/receipts consumed by humans and automation. This surface had pre-existing security controls, but the package split and receipt tooling are a new delta requiring remeasurement.

The audit covered CLI argument dispatch; resolved destination enforcement; anchor/path inputs; duplicate-safe YAML loading and safe serialization; approval identity checks; lock/atomic-replacement/rollback behavior; subprocess construction; archive extraction; clean-checkout/scratch handling; secrets/credential-shaped content; and interpreted output/log surfaces.

## Result

No findings. Subprocesses in the changed receipt scripts use list-form argv and do not enable a shell (`notes/receipt-scripts/feat70-cleanpin.py:27-35,49,73,80-81`; `feat70-grade-assert.py:29-33`; `feat70-scratch-plans.py:45-49`). Git refs and paths are operator-controlled receipt inputs, not lower-trust application inputs, and do not gain a shell interpretation. The grade exporter uses `tarfile.extractall(..., filter="data")` (`feat70-grade-assert.py:31-33`).

The production write boundary remains fail-closed: the target is resolved and checked against the owned-plan suffix before use (`plan_merge/guards.py:20-45`), YAML goes through `harness_yaml` and schema/reload checks (`guards.py:123-163,198-220`), mutating verbs retain the shared lock route (`guards.py:233-238`), and rollback replacement is same-directory atomic (`guards.py:241-268`). Free-form YAML output is emitted with `yaml.safe_dump`, not template/string evaluation (`plan_merge/text.py:81-101`). No new dependency, credential, network request, redirect, SQL, shell, or spreadsheet-export surface exists in the census.

The two accepted traceback divergences are restricted to Python frame file paths/line coordinates; the final error, exit status, stdout, and plan bytes remain compared. The five scratch divergences are restricted to exact anchor-check records caused by relocated symbols. `notes/divergence-rulings.json` keys each accepted record and stream exactly, while `feat70-cleanpin.py:99-148` still compares argv, exit, stdout, stderr, and plan bytes and treats every unruled difference as red. Thus neither ruling suppresses credential/data bytes or generalizes normalization in a way that masks a security-relevant difference.

## Threat model

- **Untrusted plan/proposal/digest → plan and feature ledger (T/I/E): mitigated.** Resolved destination guard, duplicate-safe parse, structural validation, compare-under-lock, reload verification, and atomic replacement constrain tampering and privilege-sensitive approval writes.
- **CLI path/anchor input → filesystem resolution (T/I): mitigated.** Plan destinations are checked after resolution; anchors are validated and resolved through the established anchor reader.
- **Receipt inputs → subprocess/git/archive/scratch execution (T/I/D): mitigated for the intended operator-only trust boundary.** Calls are argv-list based, archive extraction uses the data filter, and measurements execute in detached/scratch trees. Predictable temporary names are reliability concerns under concurrent operator runs, not a privilege gain for an actor with less authority.
- **Tool output → human/automation interpretation (I/R): mitigated.** Receipts preserve exact streams and plan bytes with only checkout-root replacement; accepted differences are exact-record rulings rather than broad filtering. No CSV/spreadsheet export exists.
- **Environment identity → approval mutation (S/E): mitigated within this delta.** The package retains the existing governed-agent refusal in `plan_merge/guards.py:222-230`; FEAT-70 does not loosen that boundary.

## Evidence

- Changed-file census: `git diff --name-status 9e531b34fc04f752cedf51586dc13c460580901a..138d11a4ac2b762a57bf0800bea2db95fc5d878a` → 40 paths.
- Diff size: 40 files, 5,902 insertions, 3,638 deletions.
- Pinned history: implementation `35b42d2ac73460255d1e6b78cac5d8101ad8ad28`; review seam `138d11a4ac2b762a57bf0800bea2db95fc5d878a`.
- Advisor scope records: `notes/divergence-rulings.json`; exact displayed differences: `notes/build-divergences.md` and `notes/clean-pin-byte-receipts.generated.md`.

Open questions: none.
