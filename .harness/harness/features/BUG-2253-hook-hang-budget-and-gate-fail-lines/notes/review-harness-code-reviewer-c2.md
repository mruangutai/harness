# FAIL — T-01 still has two acceptance failure paths

Reviewed `3dd8bb677bb2936361e3952030fc24f15bf9afc6..2e96b583dadaff642873566c3234dde6af0eda74`, not HEAD. feature.json agrees. Full commit list inspected; no human-tagged commits or dirty tracked files observed. No source changes, executions, tests or grading by this reader. Failure scenarios below are REASONED, not executed probes.

## Stage 1 — spec compliance

1. **High · substance · T-01 / SC-01 — echoed headers poison the parser.** `validate-digest.py:2513-2524` pushes every header-shaped child-output line and only closes the stack top. Producer `run_pool.py:107-113` prints captured child output verbatim, without escaping. Concrete valid stream: outer header for `test-a.py`; child prints `----- fixture.py (exit 1, 0.10s) -----` as a diagnostic/fixture excerpt; actual outer footer `FAIL test-a.py`; subsequent ordinary passing blocks; final `MUTATED notes/my file.md`. The unmatched echoed header stays on top, so the real FAIL is ignored and the final mutation is treated as inside a block. With more than 20 later lines, the operator loses both diagnoses. The same poisoning can originate inside a successful block: its actual PASS cannot close below the echo. Must preserve real producer file lines despite echoed header markers; add a genuine gate-path regression for this stream. Current regression excludes ordinary echoed FAIL/MUTATED labels but never supplies an echoed header or a real successful block.

2. **High · substance · T-01 / SC-02 — watchdog still has no readiness-independent deadline.** `test-validate-digest.py:6551-6576` discovers the subprocess pid only through the file written after startup. At two seconds it begins polling; it cannot terminate a subprocess that has not written readiness, and has no terminal deadline. Concrete mutant/state: remove real helper timeout forwarding, and delay blocker readiness by 60 seconds (the blocker already supports inherited `BUG2253_DELAY`, :6532-6535). The probe remains in subprocess.run for that entire delay instead of being contained at the watchdog deadline; a pre-readiness stall never terminates. The 2.5-second/60-second-timeout containment row proves eventual kill after readiness, not a bound independent of readiness. Must give the watchdog termination authority over the launched process before the readiness handshake and bound the entire missing-timeout probe. Add a delayed/no-readiness mutant case that demonstrates the bound. This is the remaining part of the previous SC-02 finding, not a demand for the plan's particular process-group implementation.

## Re-derived closure and supplied evidence

- Previous whitespace defect is closed for ordinary producer blocks: raw names with spaces are captured and compared whole (`validate-digest.py:2495-2524`). stdout+stderr concatenation, duplicate retention, tail slicing, heading, exit 2, suite selection and rerun timeout are preserved. Normal PASS closure is implemented, but echoed markers expose finding 1.
- Previous one-shot watchdog defect is partially closed: polling catches the supplied 2.5s late starter; all six block assertions now require readiness (:6618-6621). It remains unbounded before readiness, finding 2.
- Shared 30s rationale and all six actual callsite replacements satisfy inspection at test lines 1025-1031,3033,3066,3286-3288,3316-3318. Neither SC is marked verify: inspection; automated acceptance remains required.
- Supplied `notes/receipts/red-c2.txt` identifies exact base with carried-in regressions and reverted six sites; red stdout shows the diagnostic red and six `[3,3,3]` observations. `green-c2.txt` identifies clean fix 6cbdc417, selected exit 0/9.33s and full exit 0/22.91s; green stdout contains 15 passing rows. These repair prior provenance concerns but do not cover the scenarios above. Git diff confirms no .claude/tests differences from that fix to the review pin.
- Main supplies code-grade exit 0, PASSING:25, no failing rows for base..6cbdc417: byte-equivalent Python evidence for this pin, not reader execution. code_grade: pass. Stage 2 withheld because Stage 1 fails.

## Principles applied

Model the Domain: the parser's stack assumes every header-shaped payload line is an actual nested producer block; unchanged run_pool does not guarantee that invariant.

## Open questions

None. Settled missing unit-kind coverage and pre-existing runner-launch fail-open remain nonblocking, out-of-scope advisories; neither is re-raised as a gate. QA owns execution of `python3 tests/integration/test-validate-digest.py --only run_bug2253_cases` after fixes.
