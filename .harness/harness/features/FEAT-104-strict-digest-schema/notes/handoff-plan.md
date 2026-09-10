# Handoff — FEAT-104-strict-digest-schema, plan → build — written at 7e0c2ec1, seq-1

## Next

Once the operator signs BRIEF.md and plan.yaml, run `gh-sync.py open` on the feature dir (build
entry, orchestrator-owned, only after signed approval), then `plan-merge.py set-feature-station
--station building` as the eng segment starts dispatching, and dispatch **T-10 first** to
`harness-eng-lead`. T-10 captures the run-artifact baseline manifest at the OWNER ROOT and must
land before T-01, the first task that touches anything; T-01 declares `depends_on: [T-10]`.
Almost every other task is `main-session-direct` under DEC-174 — read `plan.yaml`'s `lanes:`
table before routing anything, and do not hand a carve-out file to a squad.

## Trust

- Panel finding PF-4bd91290deaf98062943319ff3ea5641 is high and gating; its premise is real —
  `tests/integration/test-validate-digest.py:30-33` records the vendored-fixture ruling and
  `:4008-4010` the shallow-clone proof — verified-at 7e0c2ec1
- CI clones shallow, so that finding's spurious red is immediate not latent —
  `.github/workflows/tests.yml:50` is a bare `actions/checkout@v4`, no `fetch-depth` — verified-at 7e0c2ec1
- The plan's legal key set is derived from the documented persona blocks, not from observed
  digests; the earlier observed-digest derivation would have rejected 16 documented fields —
  `notes/research-FEAT-104-planfix-c1.md` — verified-at 7e0c2ec1
- `check-state.sh`'s INV-26 red on this feature is a FALSE positive caused solely by T-02's
  `abandoned` status defeating its `all(status == "ready")` skip; measured directly, not inferred —
  `notes/ship-review-plan-signature-c1.md` B-1 — verified-at 7e0c2ec1
- `check-plan-routes.py` exits 1 on a pre-existing manifest deviation, not on any task; six of its
  seven DEVIATION lines are the intended DEC-174 shape —
  `notes/ship-review-plan-signature-c1.md` B-2 — verified-at 7e0c2ec1

## Dead ends

- Do not route PF-4bd91290deaf98062943319ff3ea5641 as a fix cycle; DEC-176 sends it to the
  operator's one batched signature review — `runs/planpanel-c1-validator/digest.md` — verified-at 7e0c2ec1
- Do not run `gh-sync.py open` before the signature; build entry is post-approval —
  `.agents/skills/harness/references/github-mirror.md` — verified-at 7e0c2ec1
- Do not set task stations to `plan` to silence INV-26; `ready` IS the not-started station and
  the change makes it worse — `.claude/skills/harness/bin/check-state.sh:2136-2148` — verified-at 7e0c2ec1
- Do not re-derive the digest/step key measurement; it is current as of 2026-09-09 —
  `notes/research-FEAT-104-triage-c0.md` — verified-at 7e0c2ec1

## Working set

- `.harness/harness/features/FEAT-104-strict-digest-schema/plan.yaml`
- `.harness/harness/features/FEAT-104-strict-digest-schema/BRIEF.md`
- `.harness/harness/features/FEAT-104-strict-digest-schema/notes/ship-review-plan-signature-c1.md`
- `.harness/harness/features/FEAT-104-strict-digest-schema/notes/research-FEAT-104-planfix-c1.md`
- `.agents/skills/harness/references/github-mirror.md`

## Done when

Scope: T-10 captures the run-artifact baseline manifest before any enforcement task lands
Authority: plan-task:T-10.verify
Authority: approval:.harness/harness/features/FEAT-104-strict-digest-schema/BRIEF.md#Approval
