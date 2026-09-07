# Panel c2 closed — four findings, one new task, cycle-2 panel transcribed

**All four cycle-2 findings are closed and the panel is on record at `cycle: 2` with 15 findings.**
Three were factual errors in `D-12`'s own text and are fixed in `D-12`; one was a real coverage gap
and now has an owner, `T-13`. `approval:` is byte-identical. Nothing here gates the re-signature.

`plan.yaml`: tasks **13** (T-01…T-13), decisions **12** (D-01…D-12), loads under `yaml.safe_load`.

## How each finding closed

| # | reader | sev | id | closed by |
|---|---|---|---|---|
| 1 | should-not-exist | med | `PF-19b21c0368b50e92665fe15a49db267f` | the corrected unit-ruling note (no plan node carried the claim) |
| 2 | scope | med | `PF-14faae5d430e5c49df19e30751ad2784` | **`T-13`**, new task |
| 3 | scope | med | `PF-98762207d33d7c905df8a1c0c410c33a` | `D-12.because` amended |
| 4 | should-not-exist | info | `PF-67da25de71e5be289b53782778feed02` | `D-12.choice` amended |

- **F4, the anchor.** `D-12` now cites the retention test at `post-merge-sweep.sh:228` (the `elif`
  over the allow-set) and says plainly that `:222` is only the `entry =` read that feeds it. Block
  bounds `:221-228` kept. Re-derived at source (`post-merge-sweep.sh:214-232`), not from plan prose.
- **F3, DEC-174.** The foreclosure claim is **dropped, not reworded.** `because:` now stands on two
  feet: DEC-217's Over clause, plus the structural fact that the surface admits no import at all. It
  states explicitly that DEC-174's *"library a gate calls"* clause (`DECISIONS.md:4377-4380`, read)
  **sanctions** the extraction shape and only makes the cutover main-session-direct — a price, never
  a bar.
- **F1, the recurrence count.** True set is **two** (`post-merge-sweep.sh:29-293`,
  `bash-write-guard.sh:42`). `gh-close-gate.sh:59/:79` and `plan-sign-gate.sh:43/:62` are
  counter-examples — comment *"THE DECISION LIVES IN A FILE, NOT A HEREDOC"* and `exec` a sibling
  `.py`. Corrected in `notes/…-unit-ruling.md` at the head, the anchor bullet, the Recommendation
  section, the `dec:` paragraph and Q1. One dated correcting bullet appended to
  `observations/harness-pm.md` through `observations-merge.py` (nothing rewritten).
- **F2, the vehicle.** A new `T-13`, **not** an extension of `T-07`: `T-07` is `status: done`, and
  editing a done task's declared case list and `verify:` would falsify what was verified when it
  completed.

## The DEC-217 sibling recommendation — **WITHDRAWN**

Decided on the evidence, not on the lead's framing. A standing DEC exemption is earned by a shape
that recurs; this one is **receding**. Two of the four candidates have already been converted to
decision-in-a-file, deliberately, with the mechanical reason written in their own comments (a
`python3 - <<'PY'` eats the stdin the hook's JSON arrives on), and both survivors are convertible by
the same move — `bash-write-guard.sh` already proves the payload can travel by env. An entry that
exempts a shape the repo is retiring would outlive its subject and be cited as licence to skip the
`unit` floor on any awkward surface, which is what `D-12`'s own "WHAT THIS IS NOT" paragraph guards
against. So: `D-12` stays **plan-local**, and the generalisable move is the **conversion** of the two
survivors (backlog chore, main-session-direct per DEC-174's clause), never an exemption. Q1 is
re-put on that narrower question.

## `T-13` — what it pins

`tests/integration/test-post-merge-sweep.py`, `change_type: scaffolding` (D-10's own precedent
sentence), `execution_mode: main-session-direct` citing the signed `lanes:` row that places this file
in the DEC-174 carve-out, `depends_on: [T-07]`, `status: ready`, `traces: [REQ-09, REQ-02]`.

- **Traces, checked against BRIEF.** REQ-09 *is* the retention requirement (worktree kept until
  recovery and Ship both succeed) and is confirmed. REQ-02 is added beside it because this case
  asserts the **removal** side ("release the worktree"), and it mirrors `T-07`'s own trace pair
  exactly — `T-07: [REQ-09, REQ-02]`.
- **The case, literal:** a merged feature recording `github.build_entry "not-applicable"` under
  ENABLED `github.sync` has its worktree REMOVED. One row appended to the existing names/shapes zip
  at `test-post-merge-sweep.py:886-905` — `("FEAT-9001-fixture-non-era", "not-applicable", True,
  True)` — no registration change, no duplicated loop, T-07's eight names untouched.
- **Reachability, in the task text:** the sweep re-reads `github.sync` from the main checkout's
  `.harness/harness.json` at `post-merge-sweep.sh:214-215` at merge time, while `"not-applicable"` is
  written at Build entry by the sync-not-enabled skip (D-09) — so a project that flips sync on
  between Build entry and merge arrives at `:228` with `"not-applicable"` recorded.
- **No red-first claim.** The production code already handles this state, so the row is green on
  arrival; the intent instead demands a mutation proof (delete the member from the allow-set literal,
  confirm this row alone reddens, restore, re-run). Claiming test-first here would be a false record.

`grep not-applicable tests/integration/test-post-merge-sweep.py` at `bbe9bd0a` → **zero matches**,
which is the gap `T-13` closes. `D-12`'s coverage sentence now names all three carriers: T-07's eight
cases, T-10's red-proof, T-13's case.

## Panel transcription

One `set-panel`. `last_run: 2026-09-07-panelc2-validator`, `cycle: 2`, 15 findings. Summaries lifted
from the digest's `finding` column unaltered; every id computed with `panel_findings.py id`, and all
15 recomputed after the splice — **zero mismatches**. Readers: `should-not-exist`/`fable-advisor` and
`scope`/`harness-code-reviewer` both `ran` at `cycle: 2`; `goalcheck` **retains `cycle: 1`**, because
no goalcheck reader ran in cycle 2 (panel scope was T-12 and D-12 only). `transcription_rule` was
**extended**, never replaced, with the goalcheck-row scope, the `scope` reader's envelope refusal
(harness defect, not a reader outcome), and the note that finding 2's `:216-217` citation of the sync
re-read is off by two — the sync read is `:214-215`; the finding text stays unaltered because any
alteration mints a different id.

## Evidence

- Eleven pre-existing findings: id order identical, and each one's severity / disposition /
  `resolved_by` / reader asserted equal before and after (assertion inside
  `/tmp/bug1309_c2_panel.py`; it would have refused the write otherwise).
- Four operator rulings → **all four LIVE**: `PF-1aa3b36c…`, `PF-8bfef7ee…`, `PF-23f51fd8…`,
  `PF-6030c547…`.
- `approval:` raw block, before **and** after: 898 bytes,
  `sha256=b6515d5c68e8a238f3163518d5e8dbaa4e68cea5550245907b6e12450299dff6` — byte-identical.
  (`panel:` moved as intended: 6640 → 10163 bytes.)
- `check-plan-routes.py <plan>` → `0 violation(s) across 1 plan(s)`, `exit=0`. `T-13` prints the
  expected carve-out line: `DEVIATION T-13 tests/integration/test-post-merge-sweep.py granted to
  harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct`.

## Open questions

- **Q1 (non-blocking).** Raise the conversion of the two surviving heredoc-hosted gates
  (`post-merge-sweep.sh`, `bash-write-guard.sh`) as a backlog chore, or accept the shape where it
  stands? Either answer leaves `D-12` intact. The repo-wide DEC-217 sibling is withdrawn.
- **Q2 (non-blocking, harness defect, second cycle running).** `validate-digest.py` refuses a plan
  reviewer's envelope during a re-panel of an already-approved plan (`review_sha: none`,
  `approval.status: approved`, so neither contract mode is satisfiable). The panel only survives
  because the lead adopts the note from disk.
- **Q3 (non-blocking).** `plan-merge.py apply` added `T-13` to an approved plan and left
  `approval.status: approved`; nothing in the tool resets approval on a changed task set, and pm
  cannot write that block. The operator's re-signature is the only thing that reconciles it.
