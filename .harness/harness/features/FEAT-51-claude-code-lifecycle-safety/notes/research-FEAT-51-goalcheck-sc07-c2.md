# Goal-check c2 — SC-07 re-grade (and re-anchor of the ten standing grades)

**SC-07 is `met`.** The OMP case now reddens when the exemption is removed, at **both** hook-level
surfaces, and its fixtures hold a genuinely live supervisor. The c1 vacuity (a pruned claim that
passed for the wrong reason, `research-FEAT-51-goalcheck-build-c1.md`) is closed. Nothing was
committed and the worktree is byte-identical to HEAD.

Graded at pin `aab31504`. Worktree HEAD `69de8ca7`; `git diff --stat aab31504..HEAD` touches only
`features/**` records (feature.json, three delta review notes, one observations log) — no reviewed
code moved, so the working tree IS the pinned tree for every file below.

## (a) Liveness — the fixture's claim survives `_expire`

Probe mirroring `test-check-domain.py:3416-3426`'s `claim_with_receipt(... runtime="omp",
supervisor_pid=<live Popen>)` against the real module, reading the registry file back:

- claim as written: `runtime=omp, supervisor_pid=13497, supervisor_started_at=1788312609`
- supervisor ALIVE → `_omp_claim_live` True, `_expire` → `live=1 expired=0` (`inflight_registry.py:173-193`, `:204-225`)
- supervisor terminated → `_omp_claim_live` False, `_expire` → `live=0 expired=1`

So the fixture reaches the omp branch instead of being pruned. Registry-level control, same probe:
alive omp claim alone → `orphan_write` False (allow); alive omp claim **plus** a live non-omp claim
→ True (refuse). The allow is produced by the exemption, not by an empty registry.

Note for future graders: at the registry level a *dead*-supervisor omp claim also returns False —
allow, but for the pruning reason. A registry-level allow alone is therefore not discriminating;
only the hook-level mutation below is.

## (b) Discrimination — mutation actually run, both hook cases go red

Mutant: `copytree` of the bin dir to `/tmp/sc07mut/bin`, then in the COPY only,
`inflight_registry.py:304-306` `any(claim.get("runtime") != "omp" ...)` → `any(True ...)`.
Control: an unmutated `copytree` at `/tmp/sc07ctl/bin`, to prove the copy itself is not the cause
(Expertise O-06). Suites invoked through their own seams `CHECK_DOMAIN_BIN` (`test-check-domain.py:18`)
and `PLAN_SIGN_GATE_BIN` (`test-plan-sign-gate.py:24`).

| run | test-check-domain.py | test-plan-sign-gate.py |
|---|---|---|
| baseline, real bin | exit 0, 263 ok, 0 FAIL — omp case `ok` | exit 0, 58 ok, 0 FAIL — omp case `ok` |
| control copy | exit 1, 262 ok, 1 FAIL — omp case `ok` | exit 0, 58 ok, 0 FAIL — omp case `ok` |
| **mutant copy** | **exit 1, 261 ok, 2 FAIL — `FAIL an omp-runtime writer is never quarantined`, exit 2** | **exit 1, 57 ok, 1 FAIL — `FAIL an omp-runtime writer is never quarantined on the Bash route`, rc=2** |

The mutant's extra FAIL over the control is exactly the omp case on each side; both refusals carry
the quarantine text (`…holds no live claim for FEAT-99-fixture…`). The control's single FAIL is
`schema/a CRASHING schema module DENIES the write` — a case that patches the real bin dir and is
insensitive to the hook path; it fails identically with and without the mutation and is not SC-07's.

## (c) Restore

Mutations existed only under `/tmp/sc07mut` and `/tmp/sc07ctl`; the worktree was never edited.
`git -C <worktree> diff --exit-code` → **exit 0, no output**; `git status --porcelain` → 0 lines.

## (d) Remaining SC-07 clauses

- `python3 .claude/skills/harness/bin/check-omp-port.py` → `OMP port surface: ok`, **exit 0**.
- `.omp/agents/harness-*.md`, per file: `ai-dev, backend-dev, code-reviewer, data-engineer, dev-ops,
  documentor, eng-lead, frontend-dev, pm, product-lead, qa, security-reviewer, ui-reviewer,
  validator-lead, visual-designer` — all 15 declare `blocking: true`. `harness-orchestrator.md`
  declares no frontmatter `blocking:` (only the digest template mentions the word, `:135`), which is
  the criterion's own exception.
- Suites: taken from the measured gate of record — `--kind unit` exit 0 / 519 PASS / 0 FAIL;
  `--kind integration` exit 1 / 755 PASS / 7 FAIL, all seven the accepted `test-check-plan-routes.py`
  manifest-DEVIATION family. Not re-run here.

## Re-anchor of the ten standing grades (`4f97dfe5..aab31504`, 19 files)

The diff touches `plan-sign-gate.py`, `quarantine.py`, `validate-digest.py`, `test-check-domain.py`,
`test-plan-sign-gate.py`, `test-quarantine.py`, `test-validate-digest.py` plus feature records.

- **SC-08** (two `SKILL.md` files) and **SC-09** (`DECISIONS.md`, `DECISIONS-INDEX.md`) — untouched
  by the diff. Grades stand unchanged.
- **SC-13** reads the two test files AT the sha and the diff touches both, so re-read at
  `aab31504`: `test-check-domain.py:3471-3481` and `test-plan-sign-gate.py:553-566` each still carry
  the raising and the unimportable fail-open case, each asserting exit `0` AND
  `"boundary was not enforced"`. Four cases, both surfaces. Grade stands.
- **SC-01..SC-06, SC-11** rest on suite results, and the suites in the table above were measured at
  the pin, after the diff. Anchored correctly; nothing re-graded.

## Open

- SC-10 stays `pending_uat`; script at `notes/uat-FEAT-51-c1.md`.
- `PF-e380f685c0697fb709ff29f65af0cf24` remains open and the UAT note states plainly that it does
  **not** answer it.
