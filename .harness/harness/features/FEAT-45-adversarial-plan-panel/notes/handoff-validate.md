# Handoff — FEAT-45-adversarial-plan-panel, validate → ship — written at d78f393, seq-7

Supersedes the seq-6 note. Validate is CLOSED. Four panel cycles, three main-session fix rounds and
two goal-checks. Nothing is unmet; three criteria plus one post-merge check are operator carve-outs.

## Next

Ship decision is the main session's. Present `notes/ship-review-2026-08-31.md` (rendered alongside as
`.html`), take the operator's ruling on the 16 proposed backlog rows, then `gh-sync.py ship` and the
merge — both user-gated. **B-1 is the one row worth deciding before signature rather than after**: the
32-bit finding id is a ratchet that is free to widen now and permanently more expensive once a signed
plan carries an overrule. On acceptance, unstruck rows become backlog issues; anything not listed dies.

## Trust

- **Goal-check final: 14 met, 0 unmet, 3 deferred-to-live-run** — `notes/research-FEAT-45-goalcheck-final.md`.
  Both criteria that were open at the first goal-check are closed: SC-05 (was unmet-behaviour) and
  SC-03 (was unmet-unproven) — verified-at d78f393
- **Panel cycle 3: F1, F2, F3, F4 CLOSED; qa, security and ui all PASS.** The single remaining finding
  is V1 — `runs/c3-validator/digest.md` — verified-at d78f393
- **V1 is conditionally closed on the operator's ruling, and the diagnosis is mine, measured not
  inferred.** `gateRoot()` in `.omp/extensions/harness-hooks.ts` is
  `join(dirname(import.meta.url), "..", "..")`, so `gatePath()` always resolves
  `<main checkout>/.agents/skills/harness/bin/validate-digest.py`, and `.agents/skills` is a symlink
  to `../.claude/skills`. That executing file is 1525 lines with ZERO occurrences of
  `_hook_feature_dir` or `inflight_registry.feature_root`; the branch's fixed copy is 1643 lines and
  never runs for a subagent. The fix is therefore unverifiable pre-merge BY CONSTRUCTION — verified-at d78f393
- I separately ran `inflight_registry.feature_root(<main root>, 'FEAT-45-adversarial-plan-panel')`
  and it resolves correctly to this worktree, matching on basename across 8 linked worktrees. That
  eliminates the mismatch hypothesis the panel could not decide between — verified-at d78f393
- **The test gate genuinely runs now**: `--kind unit` gives rc=0, 0 `^FAIL ` lines, 433 script-result
  lines over 57 registered scripts, no KIND-DRIFT. Before `e7626f5` it collected ZERO — verified-at d78f393
- Roster census holds: 16 `harness-*.md` in `.omp/agents` and 16 in `.claude/agents` (SC-06) — verified-at d78f393
- The `main` merge left no duplicate DEC numbers: 204, 205 (main's), 206, 207 (FEAT-45's), both
  FEAT-45 entries intact — verified-at 5685a3a

## Dead ends

- Do NOT edit `validate-digest.py` to close V1. The branch code is not what executes; an edit there
  cannot change the observed behaviour and would spend the last cycle — operator ruled conditional
  close — verified-at d78f393
- Do NOT run a cycle-4 panel. It would re-observe the same non-running code and return the same
  finding. Cycle 10 of 10 is preserved on the operator's instruction
- Do NOT treat SC-11, SC-12 or SC-16 as failures. Each names operator judgement or a live
  `/harness-plan` in its own text; one live run settles all three plus the F5 confirmation together
- Do NOT read `check-state.sh` green as a precondition. It stays red on recorded retroactive
  repository violations unrelated to this feature, including FEAT-38's missing handoff
- Do NOT reuse an existing run dir for a new cycle. The cycle-2 panel did and destroyed the cycle-0
  lead digest permanently; that is backlog row B-6

## Working set

- `.harness/harness/features/FEAT-45-adversarial-plan-panel/notes/ship-review-2026-08-31.md` — the briefing
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/notes/research-FEAT-45-goalcheck-final.md`
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/runs/c3-validator/digest.md`
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/feature.json`
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/STATE.md`
