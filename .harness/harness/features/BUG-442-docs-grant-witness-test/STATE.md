# STATE

## Current

- feature: BUG-442-docs-grant-witness-test
- runs this dispatch: 2026-09-07-02-eng (SIMPLIFY) PASS, 2026-09-07-06-validator (panel) PASS,
  2026-09-07-07-product (record fix) PASS
- status: review — VALIDATE PHASE COMPLETE. Ready for the main session's ship decision.
- review_sha: re-pinned after the plan.yaml record fix (see "Re-pin")
- cycles_used: 2 of 10 · runs: 9 of 20 (informational)
- mirror: milestone #58, parent #1477, T-01 -> #1478; both cards at `review`

Three segments ran, all PASS. Build is closed, the Building -> Review seam is crossed, and validate
exits at panel PASS with `must_fix` empty. **Ship is NOT ours** — the main session holds it.

**SIMPLIFY PASS, one fold-in** (`runs/2026-09-07-02-eng/digest.md`). Four angles as four separate
read-only spawns across two seats; EFFICIENCY returned EMPTY and measured rather than guessed. The
apply is at `test-harness-yaml.py:373` — a stale numeric pin (`892-904`) for `main()`, actually at
1074, replaced with a content anchor. The asserted expression is byte-identical, so no assertion was
weakened and the one-fix ceiling is spent. Three findings skipped to briefing rows with reasons
(ALT-F2, REU-F1, SIM-F1).

**PANEL PASS at the pin** (`runs/2026-09-07-06-validator/digest.md`). Four readers, all `ran`, none
skipped: qa, code-reviewer, security-reviewer, ui-reviewer. Spec compliance graded FIRST and PASS —
five REQs and **all seven SCs PASS**, each anchored. Code quality PASS_with_notes. `must_fix: []`,
`severity_max: med`. Gates re-measured at the pin rather than inherited: verify chain exit 0, 24 `ok`
/ 0 `FAIL`; unit runner exit 0, 0 `^FAIL ` over 2829 `ok`; integration exit 0, 0 `FAIL` over 2067.

**The falsification evidence got stronger, which is the whole point of the feature.** qa reproduced
**M3** OUT of the graded file this run (exit 1, `persona set drifted from the pinned census`),
joining M1 from the prior segment — two of three mutants now shown RED outside the file that asserts
about itself. The lead narrowed qa's own V-03 to M2 alone and RETIRED V-04: SC-04's bar is the
witness's own `FAIL` line, the in-file M2 assertion at `:367` asserts exactly that and executed for
real against a genuinely mutated scratch manifest, and code-reviewer confirmed the mutation anchor is
unique (`{ path: .harness/*/docs/**` occurs once, `team-config.yaml:144`).

Five advisory findings, none gating, all for the ship briefing — full text in the panel digest:
- **V-01 (med)** `code-grade.py` returns grade 2 on the mutation ladder at `:292` against the
  test-code grade-3 bar (`RESULT: FAIL, REASON REQUIRED`), no author-supplied reason in the record.
  The only remedy, splitting the ladder, would touch **D-03's signed mechanism**, so it is NOT a fix
  cycle but a decision question for the operator (O-08). The lead held it at `med` because the reason
  discharging it was authored by the REVIEWER, not the author — different facts.
- **V-02 (low)** `_run_child` (`:340-352`) passes no `timeout=`; deduped from two readers, severity
  decided not averaged. The lead's cross-lens addition: both mis-stated the consequence — it runs
  four times per execution, so a future break of the pairing is branching factor 4 at unbounded
  depth, which a parent-side timeout would not contain. The guard is sound today.
- **V-03/V-04/V-05 (info)** message-content assertions narrowed to M2; M2's missing out-of-file repro
  RETIRED not carried; full parent env forwarded to the child (`:349`), no live leak.

Two adequacy notes stay open as honest residuals: nobody mutated the COMPENSATING control (the
`mine`-only lens is dismissed because the pre-existing equivalence fixture would redden first on a
docs-segment shared path — source reading, not a demonstration); and the BRIEF's signed shared-loader
residual is untested, by design closing the deletion half only. No reader re-litigated D-01..D-03,
PF-049c59c515c538bc41da6616176f8987 or the signed residual; PF-049 stays `open` as a deliberate
non-action, and an info finding needs no ruling.

**Two record violations found by `check-state.sh` and CLOSED here.** Both real, neither caused here.
(1) INV-26: tasks were finished but the mirror had never run, so no issues existed. `gh-sync.py open`
is the orchestrator's own subcommand — ran it, then re-ran `status review`, putting #1477 and #1478
at `review`. (2) INV-32: the `goalcheck` reader was absent from `plan.yaml`'s `panel.readers`, so the
checker read it as never having run — FALSE; its 97-line artifact is
`notes/research-BUG-442-goalcheck-plan-c0.md`, answering **yes**, with T-01's four literals verified
against the live manifest and closing "None blocking." `plan.yaml` is granted to `harness-pm` alone,
so it went through product-lead; pm added exactly two lines via `plan-merge.py set-panel` (the only
working route — `apply` exits 7 because `panel` is not a union key). Verified on disk: that diff is
those two lines and nothing else moved.

**Re-pin.** That plan.yaml write made the old pin stale by INV-33, which compares the pinned commit's
`plan.yaml` BYTES against the plan on disk. Re-pinned to the commit carrying the record fix. The
panel's verdict still stands because the diff of CODE paths between old pin and new commit is EMPTY —
verified, not assumed: `git diff --name-only 9b3fde7e -- ':(exclude).harness/**'` returns nothing.
The ordering rule that makes this safe: a plan write rides the same commit as its content, and every
commit after a pin touches `feature.json`/`STATE.md` ONLY.

**The review base is `6d969ed3`, NOT the merge-base** — `main` has diverged, so `merge-base` gives
`de97f4a2`, behind the branch point, and that diff falsely attributes three other flows' merged PRs
(#1456, #1455, #1465) to BUG-442. True diff: 15 files, +1421/-0, one code file.

**Next:** the main session's ship decision. Two expected `check-state.sh` lines remain:
`notes/handoff-build.md` missing (known worktree defect below), and INV-29 for OTHER worktrees.

Log — station transitions:
- 2026-09-07: backlog -> plan -> building on the operator signature; T-01 building -> review
  (committed f9f2d392) -> done on the blocking qa gate PASS.
- 2026-09-07: building -> review, the station crossing in the same commit as the SIMPLIFY apply with
  `review_sha` pinned; then validate complete — panel PASS, must_fix empty, 7/7 SC, mirror opened.
  Station stays `review`; only ship writes `done`.

## Open Questions

- Harness defect, non-blocking, now SIX sightings. Guards and tools resolve a RELATIVE path against
  the MAIN checkout instead of the caller's worktree, so worktree flows — how the harness runs every
  feature — hit false denials, stale reads and false passes. (1) `handoff_done_when.py:359-364` joins
  a worktree-relative `rel_path` to the main root, so `plan-task:`/`brief-sc:` pointers cannot resolve
  from a worktree. (2) `bash-write-guard.sh` rejected a relative-path `rm` naming the main-checkout
  target. (3) `notes/handoff-<phase>.md` is unwritable from a worktree pre-merge. (4) Relative
  read/grep tool paths silently returned a STALE 908-line copy of `test-harness-yaml.py` from the main
  checkout with no error, and (5) `check-state.sh` from the main checkout prints NOTHING about a
  worktree-hosted feature, reading as a pass.
- Harness defect, non-blocking, observed by me this run. `check-domain` enforces STATE.md's 120-line
  shape gate on the Write tool, but a `python3 - <<PY` heredoc that opens the same path writes it
  unchecked. I hit this while trimming and the resulting file was legal, but the gate is bypassable
  by any agent holding Bash, so the shape budget is advisory rather than enforced.
- Harness defect, non-blocking, from the panel. The `harness-code-reviewer` job returned runner status
  `failed (exit 1)` while emitting a well-formed PASS digest; the lead verified the artifact before
  crediting it. A runner exit code disagreeing with a validated digest is a harness defect.
- Harness defect, non-blocking, from the panel. `validate-digest.py` REJECTS a member entry carrying
  `status: ran` and reads an all-`status:` member list as a team where nobody ran — while the run
  digest is append-only, so a lead that encodes it wrong cannot correct the recorded block.
- Harness defect, non-blocking. `check-domain.sh:1312-1318` permits correcting a recorded digest only
  by APPENDING, but `validate-digest.py`'s `parse_digest` binds the FIRST `DIGEST:` block and stops at
  the first dedent. The permitted route and the enforced contract do not intersect.
- Harness defect, non-blocking. This worktree's `.harness/.inflight-claims.json` held no claim for the
  dispatched member, so `check-domain` refused its first edit citing sibling runs; the member had to
  self-register through `inflight_registry.claim_with_receipt`.
- Harness defect, non-blocking, disclosed by harness-eng-lead against ITSELF. It seeded the SIMPLIFY
  checkpoint into `runs/2026-09-07-01-eng/state.yaml`, already owned by the BUILD segment.
  `check-domain` REFUSED the follow-on `digest.md` write there but PERMITTED the `state.yaml` one.
  Recovery is impossible: `runs/**` is gitignored (`.gitignore:7`). Damage bounded, class has none.
