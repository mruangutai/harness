# Security review — BUG-1716-build-amendments — c1

## BLUF

PASS at pinned SHA `f602c7eee7761ce4325accba7a04678794c7ed69`, with three medium advisory audit-integrity gaps. This diff is security-relevant: it accepts engineering-lead YAML, preserves approval while mutating signed plan text, writes an audit ledger, and lets an operator overrule ledger entries. I inspected the complete `origin/main...f602c7e` diff for auth, secrets, injection, validation, tampering, rollback consistency, ledger integrity, denial of service, and disclosure. No auth bypass, secret, injection, traversal, or data-exposure finding remains.

## Findings

1. **med · substance · task T-04 — a non-policy ledger-write failure can still leave amended plan text without its audit entry.** `plan-merge.py:2244-2255` replaces `plan.yaml`, then restores it only when `_record_amendment_judgements` raises `harness_merge.MergeRefusal`. The underlying writer can also raise an `OSError` from its tempfile/fsync/replace path; that exception bypasses restoration. An actor or environment able to induce an I/O failure on `feature.json` after the plan replacement gets approved amended task text with no corresponding judgement, defeating the ledger even though the command fails loudly. This requires unusual filesystem interference and grants no new write privilege, so severity is medium. Owner: T-04. Catch every post-splice ledger-write failure, attempt byte restoration, and preserve both failure causes.

2. **med · substance · task T-05 — one amendment still exempts every signed field on that task from INV-40.** `check-state.py:2940-2961` reduces each `T-NN.field` identity to `T-NN`, removes that whole task from the checked set, and therefore never compares its current hash again. A repository writer who can make or exploit one legitimate `T-01.intent` amendment can later change `T-01.files` or `T-01.verify` through another plan-writing route without another judgement; approval remains signed and INV-40 is silent. This is audit evasion by an actor who already has plan-write capability, not elevation. Owner: T-05. Track ledger coverage at field/version granularity or record the post-amendment task hash.

3. **med · substance · task T-04 — approved legacy records without task hashes still retain approval after generic task-text replacement and receive no replacement check.** `plan-merge.py:1024-1027` no longer resets approval for replacement of an existing task field, while `check-state.py:2926-2934` skips INV-40 when `signed_task_hashes` is absent. Thus a plan signed before BUG-1716 can be changed through generic `apply`/`amend` while staying approved and unledgered. The actor needs a governed plan-writing route, so this is an unusual-precondition tamper-detection gap. Owner: T-04. Preserve the prior approval reset for hashless approved plans or migrate/hash them before enabling approval survival.

## Prior-concern remeasurement

- **c0 V-01 / transaction defect: improved but not fully closed.** The new pin reverses write order, computes the splice before mutation, and restores the original plan on a schema/lock `MergeRefusal` (`plan-merge.py:2244-2255`), closing the previously reported “ledger landed, plan did not” path. Finding 1 is the remaining converse path for non-`MergeRefusal` failures.
- **c0 task-level INV-40 advisory: retained.** The refactor into `_signed_hashes_to_grade`, `_amended_task_ids`, and `_unledgered_task_edits` did not change task-level suppression; evidence is `check-state.py:2940-2961`.
- **c0 hashless-legacy advisory: retained.** The test explicitly preserves “signed before BUG-1716 is not graded” and production still returns no hash check for absent mappings; evidence is `check-state.py:2926-2934` and `tests/integration/test-check-state-feat59.py:488-490`.
- **V-02 through V-08: no security defect remains from those items.** The pin decomposes the selectors/commands/checks, centralizes the closed amendment contract in `amendment_contract.py`, and splits the affected tests. These were maintainability/test-grade failures rather than independent exploit paths; the security-relevant validation still rejects unknown keys, invalid task/field ids, multiline/overlong reasons, wrong value types, duplicate targets, stale `was`, illegal file anchors, and invalid ledger destinations before mutation.

## STRIDE / OWASP threat model

- **Tampering — digest → plan/ledger:** partially mitigated. Closed schema, duplicate-target refusal, under-lock `was` comparison, reload verification, and schema checks reject malformed/stale input; findings 1–3 are remaining audit-consistency gaps.
- **Spoofing / elevation — caller → amendment or overrule:** mitigated by existing governed main-session write routes, exact timestamp selection, unique-match refusal, kind check, and already-overruled refusal. The diff grants no OS/network privilege.
- **Repudiation — signed text → judgement history:** partially mitigated by signed hashes and append-only amendment entries; findings 1–3 describe the remaining ways history can fail to account for approved text.
- **Denial of service:** mitigated for ordinary contention by bounded locked writers and fail-closed refusals. The accepted digest/reason/entry shapes are bounded enough for this local CLI surface; no remote amplification exists.
- **Information disclosure / secrets:** no new exposure. Reasons and task text remain feature-local; the full pinned diff contains no credential material, tokenized URL, network request, or broader response/log surface.
- **Injection / traversal:** no exploitable shell, SQL, template, spreadsheet, or path interpolation was introduced. YAML/JSON are parsed as data, subprocess execution is not added, and plan file anchors use the existing validator.

## Inspected surface

Executable trust boundary: `.claude/skills/harness/bin/{amendment_contract.py,check-state.py,feature-record.py,feature-schema.json,plan-merge.py,validate-digest.py}`. Security-relevant tests: `tests/integration/{test-check-state-feat59.py,test-plan-merge.py,test-validate-digest.py,test-validate-feature-json.py}` and `tests/unit/test-feature-record.py`. Authority/procedure: both engineering-lead role copies, harness and code-review skills, briefing/ledger references, DECISIONS and index. Feature records and all remaining changed notes/receipts were checked for credentials, unintended disclosure, and authority drift. No tests, builds, linters, formatters, or validation commands were run, per dispatch.

## Open questions

None.
