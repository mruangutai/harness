# Handoff — FEAT-09, validate → ship — written at 3a5a245, seq-5

## Next

**Take the user's SC-08 ruling, then close the feature.** The briefing is written and returned:
`notes/ship-review-close.md`. Everything except SC-08 is done — build, review, fix, delta review,
goal-check, distillation, briefing. Do not re-run any of it.

On the ruling:
- **(c) accept-and-file** → record it in `feature.yaml` `must_fix_open`, add it to the backlog, and
  the feature ships. No code change, no re-signature.
- **(a) name the resolving agent in the checker's `OK` line** → an eng change to
  `check-plan-routes.py` + `test-check-plan-routes.py`, routed through eng-lead. NOT a DEC-174
  carve-out — neither file is an enforcement script. Counts as a rework cycle: `cycles_used` 2 → 3.
- **(b) amend SC-08** → pm re-plans under the user's approval; BRIEF is approval-gated and no
  amendment has been drafted, deliberately.

Then: user's ship acceptance → `gh-sync.py ship <feature-dir>`, and the unstruck backlog items
become issues.

## Trust

- 11 of 12 SCs MET at HEAD; SC-08 unmet-as-UNPROVEN, not broken — pm's verdict, re-derived at HEAD
  rather than relayed — verified-at 3a5a245
- SC-08's fixture provably cannot fail: live `--resolve` on the case-17 path returns TWO agents and
  a prefix-only implementation would grant SIX — **my own measurement, not pm's** — verified-at 3a5a245
- Nothing unreviewed is in the tree: `git diff --name-only 7354ad0 HEAD` is `feature.yaml` only —
  my own re-run — verified-at 3a5a245
- Gates at HEAD: unit exit 0 (32 PASS, 0 FAIL, 13 scripts), docs 0, state 0, index drift 0 — my own
  re-runs — verified-at 3a5a245
- All 12 Expertise files pass `check-expertise.sh` exit 0, including the two lead files their owners
  flagged as unverified — my own run — verified-at 3a5a245
- SC-04 is TRUE AS WRITTEN; the "FALSE" wording in older notes is superseded history — verified-at 3a5a245
- GitHub #100 (T-02) is still OPEN: its close condition is met but `gh-sync.py close-task` was
  BLOCKED by the permission classifier — my own attempt — verified-at 3a5a245

## Dead ends

- Do NOT dispatch SC-08 to a lead as a fix. It is a decision among three remedies, two of which
  change approved artifacts — routing it returns an escalation — product-lead's E1, twice pending
- Do NOT re-probe the hook with inline escaped-quote payloads: a hook exits 0 on unparseable JSON,
  which reads as a broken guard. Build payload FILES — verified-at 4918d06
- Do NOT reopen VF-2 / issue #132 — filed by user ruling, out of scope — verified-at 3a5a245
- Do NOT use base `ae2443d`. It still RESOLVES and returns the wrong scope silently: 71 files vs a
  true 14 at 3c245c3, 84 vs 30 at HEAD. Base is `47ed11f` — my own re-measurement — verified-at 3a5a245
- Do NOT write a cost line or invent a figure — the harness no longer meters spend (DEC-178)
- Do NOT change `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`, `check-state.sh` or
  `check-docs.sh` through a team run — DEC-174 carve-out, main-session-direct only

## Working set

- `notes/ship-review-close.md` — the briefing, addressed to the user
- `feature.yaml` — pin, gates, `sc_status`, `must_fix_open`, backlog
- `runs/goalcheck-product/digest.md` — the 12-entry `sc_status` with evidence
- `notes/backlog-detail.md` — the 14 residual items, rationale
- `BRIEF.md` — the 12 SCs as approved
