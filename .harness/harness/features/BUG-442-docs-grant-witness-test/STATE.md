# STATE

## Current

- feature: BUG-442-docs-grant-witness-test
- run: 2026-09-07-06-validator (validation panel) — PASS, 0 send-backs
- squad: validator (panel closed)
- status: review — VALIDATE PHASE COMPLETE. Ready for the main session's ship decision.
- review_sha: `9b3fde7ea270eeb30e71cd0efa56839cef21133c` (pinned; the panel graded this commit)
- cycles_used: 2 of max_total_cycles 10
- runs: 8 of max_total_runs 20 — informational, nothing to surface

Two segments ran this dispatch, both PASS: SIMPLIFY (eng), then the panel (validator). The build
phase is closed, the Building -> Review seam is crossed, and validate exits here at panel PASS with
`must_fix` empty. **Ship is NOT ours** — the main session holds it.

**SIMPLIFY PASS, one fold-in** (`runs/2026-09-07-02-eng/digest.md`). Four angles, four separate
read-only spawns; `harness-backend-dev` owned `tests/integration/**` by the plan's lane
(resolved_at 6d969ed3) and took REUSE + SIMPLIFICATION + the apply, `harness-dev-ops` took
EFFICIENCY + ALTITUDE. EFFICIENCY returned EMPTY, measured not guessed. The apply is at
`tests/integration/test-harness-yaml.py:373`: the anti-false-red control's message pinned
`test-harness-yaml.py:892-904` for `main()`'s try/except, but `main()` is at 1074 and T-01 inserted
182 lines above it, so the pin was never true post-commit. Replaced with a content anchor; the
asserted expression is byte-identical, so no assertion was weakened and the one-fix ceiling is
spent. Three findings skipped to briefing rows with reasons (ALT-F2, REU-F1, SIM-F1).

**PANEL PASS at the pin** (`runs/2026-09-07-06-validator/digest.md`). Four readers, all `ran`, none
skipped: qa, code-reviewer, security-reviewer, ui-reviewer. Spec compliance graded FIRST and PASS —
five REQs and **all seven SCs PASS**, each anchored. Code quality PASS_with_notes. `must_fix: []`,
`severity_max: med`. Gates re-measured at the pin rather than inherited from me: verify chain exit 0,
24 `ok` / 0 `FAIL`; unit runner exit 0, 0 `^FAIL ` over 2829 `ok`; integration exit 0, 0 `FAIL` over
2067 `ok`.

**The falsification evidence got stronger, which is the whole point of the feature.** qa reproduced
**M3** OUT of the graded file this run (exit 1, `persona set drifted from the pinned census`),
joining M1 from the prior segment — two of three mutants now shown RED outside the file that asserts
about itself. The lead narrowed qa's own V-03 from three mutants to M2 alone and RETIRED V-04:
SC-04's bar is the witness's own `FAIL` line, the in-file M2 assertion at `:367` asserts exactly that
and executed for real against a genuinely mutated scratch manifest, and code-reviewer confirmed the
mutation anchor is unique (`{ path: .harness/*/docs/**` occurs once, `team-config.yaml:144`).

Five advisory findings, none gating, all carried to the ship briefing as candidate rows — full text
in the panel digest:
- **V-01 (med)** `code-grade.py` returns grade 2 (cyclomatic 15, ABC 33.1) on the mutation ladder at
  `:292` against the test-code grade-3 bar — `RESULT: FAIL, REASON REQUIRED` — with no
  author-supplied reason in the record. The only remedy, splitting the ladder, would touch **D-03's
  signed mechanism**, so this is NOT a fix cycle but a decision question for the operator (O-08).
  The lead held it at `med` on a ground worth preserving: the reason discharging it was authored by
  the REVIEWER, not the author, and those are different facts.
- **V-02 (low)** `_run_child` (`:340-352`) passes no `timeout=`; deduped from two readers, severity
  decided not averaged. The lead's cross-lens addition: both reporters mis-stated the consequence —
  `_run_child` runs four times per execution, so a future break of the
  `BUG442_MUTANT_CHILD`/`HARNESS_PROJECT_DIR` pairing is branching factor 4 at unbounded depth and a
  parent-side timeout would not stop grandchildren. Advisory: the guard is sound today and the base
  commit already omits `timeout=` at `:310` and `:377`.
- **V-03/V-04/V-05 (info)** message-content assertions narrowed to M2; M2's missing out-of-file repro
  RETIRED not carried; full parent env forwarded to the child (`:349`), no live leak.

Two adequacy notes stay open as honest residuals: nobody mutated the COMPENSATING control (the
`mine`-only lens is dismissed because the pre-existing equivalence fixture would redden first on a
docs-segment shared path — source reading, not a demonstration); and the BRIEF's signed shared-loader
residual is untested by any reader and unchanged, by design closing the deletion half only.

No reader re-litigated D-01, D-02, D-03, PF-049c59c515c538bc41da6616176f8987 or the signed residual.
PF-049 (info, hand-pinned census) stays `open` as a deliberate non-action; info needs no ruling.

**Two mechanics recorded because both are load-bearing and neither is guessable later.** (1) INV-33
compares the pinned commit's `plan.yaml` BYTES against the plan on disk, so a station written after
the pin makes the pin stale — the station write therefore rides the SAME commit as the code
(`9b3fde7e`), and every later commit touches `feature.json`/`STATE.md` only, never `plan.yaml`.
`gh-sync.py status <dir> review` ran at the seam, exit 0. (2) The review base is `6d969ed3`, **NOT
the merge-base**: `main` has diverged, so `merge-base(main, 9b3fde7e)` is `de97f4a2` — behind the
branch point — and that diff falsely attributes three other flows' merged PRs (#1456, #1455, #1465)
to BUG-442. Verified before dispatch and passed to every reader. The true diff is 15 files, +1421/-0,
of which exactly one is code: `tests/integration/test-harness-yaml.py`.

**Next:** the main session's ship decision. `gh-sync.py open` has never run for this feature, so no
parent issue is recorded — `status review` said so and exited 0. The mirror never gates, but ship
needs `open` first.

Working memory lives here, in `## Current`, deliberately: `notes/handoff-<phase>.md` is unwritable
from a worktree for a feature not yet on the default branch. Diagnosed, raised below, NOT
re-diagnosed.

Log — station transitions:
- 2026-09-07: backlog -> plan; plan -> building on the operator signature.
- 2026-09-07: T-01 building -> review (committed f9f2d392) -> done (blocking qa gate PASS).
- 2026-09-07: building -> review. SIMPLIFY closed, suites green, station crossed in the same commit
  as the apply, `review_sha` pinned at 9b3fde7e.
- 2026-09-07: validate complete. Panel PASS, must_fix empty, 7/7 SC. Station stays `review`.

## Open Questions

- Harness defect, non-blocking, now FOUR sightings. Guards and tools resolve a RELATIVE path against
  the MAIN checkout instead of the caller's worktree, so worktree flows — how the harness runs every
  feature — hit false denials and stale reads. (1) `handoff_done_when.py:359-364` joins a
  worktree-relative `rel_path` to the main root, so `plan-task:`/`brief-sc:` pointers cannot resolve
  from a worktree. (2) `bash-write-guard.sh` rejected a relative-path `rm` naming the main-checkout
  target; the absolute worktree path was allowed. (3) `notes/handoff-<phase>.md` is unwritable from a
  worktree pre-merge. (4) NEW, from harness-code-reviewer: relative read/grep tool paths silently
  returned a STALE 908-line copy of `test-harness-yaml.py` from the main checkout with no error — a
  review reading the wrong bytes and never knowing.
- Harness defect, non-blocking, from the panel. The `harness-code-reviewer` job returned runner
  status `failed (exit 1)` while emitting a well-formed PASS digest; the lead verified the artifact
  before crediting it. A runner exit code disagreeing with a validated digest is a harness defect.
- Harness defect, non-blocking, from the panel. `validate-digest.py` REJECTS a member entry carrying
  `status: ran` and reads an all-`status:` member list as a team where nobody ran — while the run
  digest is append-only, so a lead that encodes it wrong cannot correct the recorded block. Either
  accept `ran` or document the reserved-for-skipped rule where leads write `members:`.
- Harness defect, non-blocking. `check-domain.sh:1312-1318` permits correcting a recorded digest only
  by APPENDING, but `validate-digest.py`'s `parse_digest` binds the FIRST `DIGEST:` block and stops
  at the first dedent. The permitted route and the enforced contract do not intersect.
- Harness defect, non-blocking. This worktree's `.harness/.inflight-claims.json` held no claim for the
  dispatched member, so `check-domain` refused its first edit citing sibling runs; the member had to
  self-register through `inflight_registry.claim_with_receipt`.
- Harness defect, non-blocking, disclosed by harness-eng-lead against ITSELF. It seeded the SIMPLIFY
  checkpoint into `runs/2026-09-07-01-eng/state.yaml`, already owned by the BUILD segment.
  `check-domain` REFUSED the follow-on `digest.md` write there but PERMITTED the `state.yaml` one.
  Recovery is impossible: `runs/**` is gitignored (`.gitignore:7`). Damage bounded, class has none.
