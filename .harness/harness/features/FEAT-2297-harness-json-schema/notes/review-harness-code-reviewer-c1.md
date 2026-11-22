# Code review — FEAT-2297 c1

**ESCALATE:** literal SC-08 personal review remains unproven; delegated authorization and Kaya landing are not disputed. One medium schema-boundary mismatch and one low record defect accompany this conclusion.

Reviewed `9fd1f6b414ed683cd5f5bcca4ad5fe17c35e0568..47d2e50243ad7fb080e13ef48115756d7d3b7c61`, derived from `merge-base(origin/main, pin)`, not HEAD. Feature worktree status was clean; no `[harness:human]` commits appeared in range. Pinned blobs, not installed control-plane bytes, supplied implementation evidence.

## Stage 1 — compliance

- **med · substance · T-01 · SC-01/D-03:** `config-schemas/harness.json:144,181` uses `$` for repository and DEC identifiers. REASONED: `github.repo = "acme/repo\n"` matches Python's regex because `$` accepts the position before a terminal newline; the loader therefore accepts whitespace in the supposedly pinned repository. Likewise `signed = "DEC-187\n"` passes the decision pattern. These present malformed values escape the central boundary; callers receive a malformed remote identity / signature instead of a source/key/rule refusal. Require whole-string matching semantics and concrete rejection regression cases. Not dynamically probed here; focused QA probe requested.
- **low · form · T-08 · SC-07:** `notes/changes-config-contract.md:48-49` points readers to nonexistent `notes/receipts/t09-kaya.txt` and calls it operator-review evidence; actual landing/delegation evidence is `notes/uat-kaya-migration.md:37-59`. Correct the pointer and describe the delegated review honestly; no product re-gate.
- **SC-07 inspection:** pinned `SPEC.md:91-119,187,1430-1441`, `DECISIONS.md:7312,8361,8472-8535`, template `README.md:37-48`, and change receipt agree on schema-owned defaults, conditional requirements, refusal, v3 upgrade, closed vocabularies and the budgets-only TypeScript exception, apart from the receipt defect above. DEC-221/254 amendments and DEC-256 index entry are present; condition evaluation is explicitly not shipped.
- Loader/default/conditional paths, strict non-config migrations, governed-command-first gates, remote config refusal, pre-write upgrade validation/atomic writer, shared fixture delegates, generated TypeScript budgets, census controls, and reduction checker/dispositions have corresponding changes. Accepted Gate A/B measurement, INV-13 retirement and deferred #2393 are not findings. Prior matrix/reduction receipts are historical evidence, not current-run verification.
- **SC-08 decision required · T-09:** `uat-kaya-migration.md:39-47` records standing delegated approval and advisor review, explicitly not personal operator review. This supports authorization, but does not establish BRIEF's literal personal-review condition. Operator acceptance/amendment or actual personal-review evidence must settle it; landing alone cannot.

## Stage 2 and verification limits

Stage 1 is not cleared; the requested independent Stage 2 quality verdict is withheld. The mandatory mechanical Python grading prerequisite ran against the exact range: **154 passing records; no high or grade-2 records** (`code_grade: pass`). This is not a behavioral test result or a complete quality clearance.

No build, suite, lint, formatter or reported-failure rerun. Real-owner failure attribution is supported independently: `test-corpus-real-owner.py:102-133` invokes candidate check-state with the real owner as root; both installed owner config and `origin/main` config remain v2, while candidate config is v3. Production-runner proof remains QA-owned under DEC-255. No managed checkout was created. A temporary-output redirect was refused by the read-only guard; no file was written and no permission workaround was used.

## Open questions

1. Does the operator accept delegated advisor review as satisfying SC-08, or supply personal-review evidence? Blocking ship acceptance.
2. QA: confirm the two terminal-newline rejection cases and refresh pinned production-runner/reduction receipts; no claim of those checks is made here.
