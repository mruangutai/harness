# Observations — harness-validator-lead — FEAT-20-migration-detector

- 2026-08-14: Review panel run `2026-08-14-1-validator`, four reviewers dispatched in one wave at
  `ea476fd`. Seeding `state.yaml` was BLOCKED: `check-domain.sh` rejected top-level keys `cycle` and
  `diff_base` as non-checkpoint (DEC-154), even though both values are a bare integer and a bare
  SHA. The allowlist is closed by NAME, not by value shape — `review_sha` passed, `diff_base` did
  not. Moved both into per-step `note:` strings.

- 2026-08-14: Lead-tier seam check that no single reviewer is positioned to make (P-06). The
  caller asked for BOTH exit-2 call sites verified. I read each at source rather than wait:
  - CI: `.github/workflows/tests.yml:233` ends the Layout gate step with `exit "$rc"`, `rc` being
    the detector's own code, so exit 2 fails the step. Lines 204-229 fail CLOSED on a missing
    summary line, a missing `examined` line, and any of the three zero counts.
  - Session entry: `check-state.sh:1266-1318` imports `layout_migration` in-process, appends a
    CANNOT RUN violation on import failure (`:1270`) and on a raising scan (`:1280`), and composes
    findings from the structured result — it never re-parses CLI text and never reads an exit code.
  Both hold. The seam is closed at `ea476fd`.

- 2026-08-14: The latent fail-open I found at that seam, which is a REGRESSION-PINNING gap rather
  than a live defect (P-08 — "the code does X" and "something holds it to X" are different claims).
  `check-state.sh:1302-1318` dispatches on `_srep.cause` through a four-branch `if/elif` chain with
  NO trailing `else`. `layout_migration.scan` (`:197-207`) sets exactly one of `no-rows`,
  `unreadable`, `neither`, `no-evidence` at every CANNOT_VERIFY construction site, so the chain is
  exhaustive TODAY and nothing falls through. But a fifth cause added by units 3-7 — or one branch
  deleted — makes that surface append NOTHING to `bad`, while the module still returns exit 2 that
  the session-entry call site never reads. Result: `check-state.sh` reports a clean tree over a
  surface the detector could not verify. Issue #148's shape at the call site, not in the verdict
  logic the feature hardened.

- 2026-08-14: CONFIRMED that gap with the discriminating measurement rather than leaving it as
  reasoning (Evidence rule). `test-check-state.py` carries exactly five INV-27 cases, x.1-x.5
  (`:1647-1714`). Only ONE renders a cause: x.2 (`:1670`) asserts `"CANNOT VERIFY"` and
  `"[neither]"`. NOTHING exercises `unreadable`, `no-evidence` or `no-rows` at this call site. The
  NAMEABLE SURVIVING MUTATION: delete `elif _srep.cause == "no-rows":` at `check-state.sh:1316-1318`
  (or `unreadable` at `:1303`, or `no-evidence` at `:1313`). Unit case 16 still passes — it tests
  the MODULE's exit 2, not the invariant's rendering. All five x.N cases still pass. NOT gated: the
  code is correct at `ea476fd`, the operator signed the no-mutation-proof class as non-blocking, and
  CI still fails via `exit "$rc"` even with a branch deleted.

- 2026-08-14: qa segment gated at `11cb644`; this panel was pinned at `ea476fd`. The caller called
  them "the equivalent tree". I asked the panel's qa step to run
  `git diff --name-only 11cb644..ea476fd` so the digest could STATE the delta instead of relaying an
  equivalence claim I had not measured (Evidence rule; G-07). Measured answer: only `STATE.md`,
  `feature.json`, `notes/handoff-build.md`, `notes/qa-c0.md` — ZERO of the eight source files.

- 2026-08-14: PANEL CALIBRATION. ui-reviewer scoped out in ~39s on a measured file-extension census
  over all 22 diff files plus a `git ls-tree` check that no `DESIGN.md` exists — it verified the
  dispatch's framing instead of accepting it. Its `severity_max: n/a` is the sanctioned spelling for
  a scoped-out reviewer (G-06), not drift. code-reviewer was by far the longest (~11.5 min vs ~5-6
  for qa and security) and produced the only executed perturbation; the runtime bought something.

- 2026-08-14: I MIS-NARRATED A MEMBER'S CONDUCT IN A SIGNED ARTIFACT, and the advisor caught it, not
  me. I wrote that security "filed it `info` as a pre-existing nit" about the false x.5 comment.
  Security's artifact says the opposite in as many words: "Info-level, IN THE DIFF, worth a one-line
  correction whenever this area is next touched" (`:74-75`). It scoped the item correctly; only its
  REMEDY framing (defer-until-touched) underweighted a false safety claim newly introduced. My
  re-rating to low survives on that narrower ground, but the sentence as first written was false
  about a member — rule 15, and precisely the G-09 failure where a relayed digest makes a member
  spend its distillation slot rebutting my error. ROOT CAUSE: I read security's artifact BEFORE its
  digest arrived, formed the "pre-existing" reading from its Q2 one-liner, and never re-read the
  artifact body when I wrote the finding up. Having the artifact open earlier is not the same as
  having it open AT THE SENTENCE (G-07's actual claim).

- 2026-08-14: qa's panel note narrates "cases 1-18 (18 required by plan, plus cases 17-18 added)",
  self-contradictory and overstating the plan: T-01 specifies cases 1-16 and T-02 adds the
  exit-code-contract case, so 17 are plan-required and 1 is extra. Its ANCHORS are correct; only the
  parenthetical count is loose. Info, NOT a send-back — cosmetic, visible from the same sentence,
  and looping a minor nit to max_cycles is a process defect, not diligence.

- 2026-08-14: code-reviewer's line anchors drift 3-8 lines from source throughout (it cites
  `reader_files` at `:199`, actual `:195`; `_evidence` returns at `~146/~156`, actual `:143/:152`),
  though it marked some approximate with a tilde and every MECHANISM I spot-checked was exactly
  right. P-01 earned its keep: I published the anchors I measured, not the ones it reported.
