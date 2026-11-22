# Goal-check — BUG-2253 validate c0

FAIL: both acceptance perspectives are partial; the green selected cases do not discharge the signed coverage and watchdog requirements.

- **operator — partial (SC-01):** supplied buried-file/fallback cases pass with refusal status 2, and the unchanged tail algorithm is retained; whitespace-containing file lines can still disappear above the tail (`validate-digest.py:2495–2513`; `notes/receipts/green.txt:3–4`).
- **code maintainer — partial (SC-02):** all six sites share 30 and the supplied six observation cases follow 0.05/0.10; six blocking cases report green, but the watchdog can miss the child and readiness is not established (`test-validate-digest.py:6504–6594`; `notes/receipts/green.txt:5–16`).

## Scope and evidence

Confirmed immutable base `3dd8bb677bb2936361e3952030fc24f15bf9afc6` and review pin `21e064c9475e35a4abfdd71b5b5cdd23517c0659` with git rev-parse; reviewed their diff, not HEAD. Executable changes are only the gate and coupled integration file (285 insertions, 9 deletions); inventory unchanged. T-01 traces both declared perspectives through SC-01/SC-02; neither perspective is orphaned. Product guidance absence is disclosed in BRIEF; no substitute requirements were inferred.

Existing evidence only: `notes/receipts/red.txt:1–32` records exit 1, buried-file failure and all six observed `[3, 3, 3]`; four blocking failures are FileNotFoundError, not defect-exposing timeout proofs. Its subject is `3769919f155aee2013b6539ec3cf3d6ed4f9f49b`, not the assigned base. Comparing those commits shows only feature records differ: executable subjects are identical, allowing source-equivalent evidence transfer, not a claim of execution at the assigned base. `green.txt:1–19` records 14 passing selected cases, a full-suite pass and unchanged inventory. These are supplied build receipts, not a QA digest. Green identifies no immutable execution SHA or elapsed duration; neither receipt supplies separately complete stdout/stderr. I ran no verification, created no checkout, and changed only this note.

## Findings and simplification deviations

1. **GC-01 — substance/high; T-01, SC-01.** One-token fullmatch narrows signed “every FAIL <file>/MUTATED <file> line.” For example, `MUTATED notes/my file.md` above 20 passing lines is omitted. The unchanged producer emits raw names (`run_pool.py:107–113,127–134`), without this restriction. The new negative case for echoed per-case failures does not authorize excluding legitimate filenames. Preserve the signed outcome or obtain explicit operator amendment; the existing selector amendment approves neither narrowing.
2. **GC-02 — substance/high; T-01, SC-02.** `_bug2253_watchdog` starts a same-process timer before fixture setup, reads a child-written PID once, and silently ignores an absent/partial file (`test-validate-digest.py:6533–6581`). With a missing subprocess timeout and child startup delayed beyond two seconds, it misses the child permanently and the subsequent 3600-second sleep hangs the regression. There is no independent parent supervising/reaping a probe/process group. Readiness-as-PID-channel also drops the signed handshake: TimeoutExpired can occur during delayed interpreter startup without reaching the blocker. The supplied green cases and literal-three-second red cases do not demonstrate the missing-timeout mutant under this condition.
3. **GC-03 — form/med; evidence only.** Execution provenance, complete streams and under-60-second duration remain unestablished by the supplied receipts. QA owns collecting these, not PM or the user. Source equivalence above resolves the different base's executable identity, not these record gaps.

**Accepted deviation:** timing only the real helper/subprocess call retains the selected budget plus 0.5-second bound and excludes unrelated setup latency; it does not narrow either SC. Reusing `--only run_bug2253_cases` is explicitly operator-approved. The regex and readiness/watchdog changes are not approved acceptance amendments.

**Out-of-scope advisory — substance/info, operator decision only:** the existing runner-launch failure branch still returns 0 with an unverified-suite diagnostic (`validate-digest.py:2480–2483`). This unchanged fail-open rule is expressly outside this patch and is not a blocker here.

## Judgment rules and open questions

Applied `harness-verification-rules`: named green cases are evidence only for their actual assertions; no reruns or inferred missing-timeout proof. Applied Principles “No more specific than necessary” and “Never falsify the record”: accept call-only timing, but retain unsigned behavioral omissions and receipt limitations. Open questions: none requiring product clarification; the signed outcomes already specify what must hold. Restore them or seek an explicit operator scope ruling, and route evidence gaps to QA.
