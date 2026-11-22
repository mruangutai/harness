# Apply — FEAT-2340

All six cycle-1 findings are resolved in the pending proposal; goal-check remains separate. Exactly T-01 → T-02 and the four authorized implementation files remain. No implementation, tests or implementation documents were changed.

## Finding dispositions

- PF-fee65e0b3e6f0b4b7dae160d9a142676 — resolved: T-02 uses Main's supervised 55-second aggregate deadline. No timing measurement or completion guarantee is asserted. Completed-suite receipts and host timeout evidence are retained; incomplete suites remain unverified and their buffered partial output is explicitly unavailable. Timeout fails verification rather than silently extending its budget. BRIEF Verification gaps records this limitation.
- PF-bb5500c92fdee2e4ba87141aaf2396cb — resolved: SC-03 now claims only existing single-cycle and mixed-case exit-status coverage. SC-02 and T-02 retain multi-cycle canonicalization, mixed-case canonical names and legacy-versus-shape diagnostic ordering as pinned-content inspection obligations against baseline e239d88156c508c948d49cd31238ea13b3b39865. No test rewrite is authorized.
- PF-8e525443bca2a4b93860ade43e50b604 — resolved: decisions_affected adds DEC-159, DEC-180 and DEC-182 keeps with verbatim source fragments; T-02 consultation and BRIEF Constraints include them. No decision amendment or strike.
- PF-26d7495059a59d5eccd61711c5bd0888 — resolved: bespoke executor removed. T-02's small launcher only discovers scripts, clears persona contamination, enables unbuffered output and execs existing run_pool.py. Its CLI accepts explicit scripts; run_one gives each suite private TMPDIR/TMP/TEMP and merges stderr into stdout; _run_scripts emits completed results; main exits nonzero for nonzero suite exits. Main must also reject FAIL output because zero-exit textual failures are not detected by the pool.
- PF-ef5d4f47d2be59676374c1e07a072321 — resolved: live VERB replacement is SHAPE_DIAGNOSTIC_LABEL, neutral between PRE blocking and POST already-written reporting. Diagnostic bytes remain unchanged.
- PF-1fef2d0cfe0c6465f0c9c7475072923c — resolved: duplicate ship/backlog sentence removed from T-02; BRIEF Out of scope retains every excluded group and ship-time backlog responsibility.

All recorded findings retain reader severity/kind and are marked resolved_by T-02 via set-panel. Non-greedy phase/cycle handling, asymmetric plan flags, aligned byte-stable declarations, bootstrap literal equality, frozen fixture and no unrelated renames remain mandatory.

## Receipts and limits

plan-merge record-panel --cycle 1 exited 0 from runs/r-20261122-1-plan-product/panel-c1.md. Final plan-merge check exited 0: two tasks, four anchors, zero failures. Task-changing stdout was captured and printed; no APPROVAL-RESET receipt occurred, so no gh-sync call was made. Approval mappings were not written.

The first proposed env-prefixed verify was rejected by the runnable-command schema before landing; the accepted Python exec launcher invokes the same existing runner without duplicating execution logic. Mutation hooks reported unsigned BRIEF and missing Build-entry receipt; those remain visible pre-build conditions, not claimed fixed or reasons to write approval. No builds, suites, lint, formatting or runtime measurements ran.

Open questions: none. Goal-check follows separately; implementation verification and pinned review evidence remain future obligations.
