# STATE

## Current

- feature: BUG-1309-mirror-build-entry
- run: c16 routing — `runs/2026-09-08-c16-planamend-product/` (pm, plan amendment, PASS). No
  validator run this cycle: the remedy is DEC-174 main-session-direct and no squad may execute it.
- squad: product (plan only)
- station: **building** (`plan.yaml` `status:`), T-05 moved `done` → `building`. The feature left
  review because the remedy is code, not a re-read.
- budget: **`cycles_used` 15 of `max_total_cycles` 16** — the operator raised the cap 14 → 16
  (ruling R-5, `feature.json`). c16 is this remediation cycle; the re-validation that grades it is
  the sixteenth and last.
- `review_sha` still reads `e374c9a29e4321968e4c2a6bbae045da9203440c` and is now **STALE**:
  `plan.yaml` has changed since the pin, and the pin must move to the tip that carries the parser
  fix before any validator run (INV-6, INV-33). Nothing is dispatched against it until then.
- Approvals: `BRIEF.md` `## Approval` approved 2026-09-08; `plan.yaml` `approval:` approved
  2026-09-08 but now **stale over T-05 text amended after that signature** — `sign-approval` is
  required before ship, and it is the main session's act.

### The operator's two rulings, transcribed and acted on

`notes/rulings-2026-09-08-c16-parser.md` (orchestrator transcription of an inline main-session
relay; there is no answers file on disk for this round and this note is not that channel).

- **R-4 — fix the parser comprehensively.** Four clauses: value-taking options handled as a CLASS in
  both positions and both spellings; FAIL CLOSED when a merge is identified and its ref is not;
  merge CONTROL operations (`--abort`, `--continue`, `--quit`) ALLOW at exit 0; `git_merge` grades 4
  or better. Q1 and Q2 of the c15 return are answered FIX; Q3 (the grade) is answered FIX.
- **R-5 — budget 14 → 16.** Recorded in `feature.json` (`max_total_cycles: 16`, `cycles_used: 15`).

### The plan now specifies what the operator is to build — verified on disk

pm amended T-05 (`notes/research-BUG-1309-planamend-c16.md`, run digest
`runs/2026-09-08-c16-planamend-product/digest.md`). Confirmed by the orchestrator against the file,
not from the digest: T-05 `intent` carries all four R-4 clauses (`--abort`/`--continue`/`--quit`,
FAIL CLOSED, `--attr-source`, `--cleanup`, `-F`, the GRADE 3 measurement); `verify:` gates **26**
case names, up from 19, plus a `code-grade.py` assertion whose qualname set **excludes `main`**;
`D-16` and `D-17` exist; `approval:` is byte-identical. Diff: plan.yaml only, +136/-6.

### The four ruled forms, re-measured at the current tip

`/tmp/bug1309-c16-parse-probe.py` against `merge_ref` at `e374c9a2` — every case the packet calls
red is red, and the fenced bounds are intact:

| form | `merge_ref` today | consequence | after R-4 |
|---|---|---|---|
| `git merge -F /tmp/msg feature/test` | `('git', '/tmp/msg')` | wrong ref → silent allow | deny |
| `git merge --cleanup strip feature/test` | `('git', 'strip')` | silent allow | deny |
| `git --attr-source HEAD merge --no-ff feature/test` | `None` | not seen as a merge | deny |
| `git merge --file /tmp/msg` (no ref) | `('git', '/tmp/msg')` | silent allow | deny, fail-closed |
| `git merge --abort` / `--continue` / `--quit` | `('git', None)` | local fallback → **deny** | allow, exit 0 |
| `git merge --no-ff feature/test` | `('git', 'feature/test')` | correct deny | unchanged |
| `git commit -m 'merge notes'` / `git merge-base …` | `None` | correctly ignored | unchanged |

`code-grade.py .claude/skills/harness/bin/merge-gate.py` at the tip: `git_merge` GRADE **3** FAIL,
`main` GRADE 2 FAIL (pre-existing, out of scope and excluded from the new assertion by name); the
other twelve functions PASS.

### Next, in order

`notes/direct-packet-2026-09-08-c16-parser.md` — main-session-direct, and the whole of it:
seven new discriminating cases red first → the `git_merge` edit → the suites, T-05's `verify:` and
`code-grade` → commit + `set-task-station T-05 done` + the two `gh-sync.py` mirror writes (the main
session owns them for a `main-session-direct` segment). Then back to the orchestrator: re-pin
`review_sha` → `gh-sync.py status <feature-dir> review` → qa `test_matrix` → panel c17 over the
delta → pm goal-check → extend UAT Step 3b → operator SC-10 UAT → rewritten briefing → ship.

## Open Questions

- Q1 (blocking, operator — **signature**) — R-4 clause 3 traces to no success criterion, and SC-04
  read literally MANDATES the deny it reverses (`BRIEF.md:108-110`: "a merge command … is denied";
  `git merge --abort` is a merge command). pm recommends a new **SC-11**, drafted verbatim in
  `notes/research-BUG-1309-planamend-c16.md:48-53`; the alternative is an exclusion sentence inside
  SC-04; declining both leaves a disclosed verification gap. `BRIEF.md` is approval-gated — the
  operator's edit and re-signature either way. **Does not block the implementation.**
- Q2 (non-blocking, operator) — `plan-merge.py sign-approval` must re-sign the plan over the T-05
  amendment before ship.
- Q3 (non-blocking, pm recommendation) — the code-grade bar stays OUT of the success criteria: a
  quality gate, gated by T-05's `verify` and recorded as D-17. Consequence: no goal-check reports
  the grade; only T-05's verify and the panel's code-grade reader do.
- Q4 (non-blocking, plan hygiene, pre-existing) — T-05's enumerated case-name contract lists 21
  names while `verify:` gates 26; the five D-13/D-14 names never reached the enumeration. Harmless
  today (those cases exist and pass), but the enumeration no longer is the contract it claims.
- Q5 (non-blocking, harness defect) — `harness-pm`'s terminal yield carried null data (job status
  `failed (exit 1)`) while a complete, well-formed VERDICT/DIGEST/artifact block was present and
  every claimed change verified on disk. Seen again this cycle; no re-spawn was spent.
- SC-10 UAT is still NOT requested and still blocks the ship; its Step 3b needs the three
  previously-allowed forms once they deny.
- The stale briefing at `notes/ship-review-2026-09-08-resume.md` and its B-1..B-13 backlog still
  await operator disposition; rewritten after the fix lands, before the ship decision.
