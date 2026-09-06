# Handoff — BUG-1308, plan → build — written at 8a0b568, seq-2

<!-- SUPERSEDES seq-1, written before the operator's REVISE ruling. -->

## Next

Take the operator's signature on `BRIEF.md ## Approval` and `plan.yaml approval` via
`plan-merge.py sign-approval`. No `--overrule` is needed: no high or critical finding is open. Then
build entry is T-01 (`plan.yaml` T-01, `depends_on: []`, the only dependency-free task) to
`harness-eng-lead`, with T-03 held for the main session under DEC-174 and T-02 gated on both.

## Trust

- No open high or critical panel finding: 14 findings, 13 `resolved`, 1 `open` (PF-12c69147, low) — `plan.yaml` `panel.findings` — verified-at 8a0b568, loaded and tallied by me
- INV-32 passes both halves: all three readers `ran`, and no open finding carries a severity outside info/low/med — I re-ran the invariant's own logic from `check-state.sh:519-547` against this plan — verified-at 8a0b568
- Approval is `pending` with no `rulings` in BOTH artifacts — `plan.yaml` `approval`, `BRIEF.md:154-156` — verified-at 8a0b568
- The operator's four rulings are implemented, not merely claimed: `section` required on every op (D-02, D-03 reduced to two conditions, D-05), stable-identity application with the invariant "no index resolved against the base snapshot is ever used to address the mutated list" (`plan.yaml` T-01 Step D), D-10's merge rewrite intact, contention forced by the test taking the production lock — verified-at 8a0b568, quoted from disk
- `lanes.resolved_at` is `c369fb1` and every lane row reproduces from `check-domain.sh --resolve` — I ran the resolver on all five surfaces — verified-at 8a0b568
- The issue's premise holds: `expertise-merge.py` exposes only `apply`, `compute_union` appends only — `.claude/skills/harness/bin/expertise-merge.py` — verified-at 8a0b568, read by me
- Goal-check c3 PASS and panel c2 PASS with severity_max med — `notes/research-BUG-1308-expertise-replace-drop-goalcheck-plan-c3.md`, `runs/2026-09-05-plan-panel-c2-validator/digest.md` — UNVERIFIED by me beyond the panel tallies and the three imprecisions I routed for repair
- SC-04's CLI half was WIDENED, not narrowed, on pm's reading that the op index is present in the CLI refusal line under D-05's message shape — `notes/research-BUG-1308-expertise-replace-drop-planpolish-c3.md` — UNVERIFIED by me; the builder should confirm it when writing the message

## Dead ends

- Do not re-open `section`-required, the deleted cross-section ambiguity condition, u4/case14(a), or merge-as-authoring — the operator ruled on all four at the cycle-1 signature review — `plan.yaml` D-15 — verified-at 8a0b568
- Do not action PF-12c69147 (u10 as a permanent red case) — the validator lead recommended against it twice and the operator upheld it — `runs/2026-09-05-plan-panel-c2-validator/digest.md` `cycle1_dispositions` — verified-at 8a0b568
- Do not run a third plan panel to chase remaining meds — cycle 2 returned no gating finding and every med it raised is now `resolved` — `plan.yaml` `panel.findings` — verified-at 8a0b568
- Do not run any `gh-sync.py` subcommand for this phase; the plan station is `board-station.py`'s at the `/harness-plan` door and the plan phase is one the main session holds — `references/github-mirror.md` station table — verified-at 8a0b568
- Do not treat a subagent's `failed (exit 1)` on this feature as a real failure without reading its digest — it recurred three times with a well-formed return each time — STATE.md `## Open Questions` — verified-at 8a0b568

## Working set

- `.harness/harness/features/BUG-1308-expertise-replace-drop/plan.yaml` — 15 decisions, 4 tasks, the 14-finding `panel`
- `.harness/harness/features/BUG-1308-expertise-replace-drop/BRIEF.md` — REQ-01..09, SC-01..12
- `.harness/harness/features/BUG-1308-expertise-replace-drop/runs/2026-09-05-plan-panel-c2-validator/digest.md` — cycle-1 dispositions and the seven cycle-2 findings
- `.harness/harness/features/BUG-1308-expertise-replace-drop/notes/research-BUG-1308-expertise-replace-drop-advisor-c1.md` — what A1/A2/A3 settle
- `.harness/harness/features/BUG-1308-expertise-replace-drop/notes/research-BUG-1308-expertise-replace-drop-revision-c2.md` — what the operator's ruling changed, per finding

## Done when

Scope: Operator signature on the plan-phase approval artifacts
Authority: approval:.claude/worktrees/harness/BUG-1308-expertise-replace-drop/.harness/harness/features/BUG-1308-expertise-replace-drop/BRIEF.md#Approval
