# Plan-panel c3 — spec-compliance / scope reader — FEAT-53

**Verdict: PASS with two med notes, neither gating.** The three operator rulings from
`answers-2026-09-01-plan-signature-c2.md` are all faithfully applied in `ba5b4a50`. Mechanically
verified: 22/22 tasks, `depends_on` acyclic, no dangling task-id references, every `REQ-NN` in
`BRIEF.md` traced by at least one task and no task `traces:` cites a nonexistent REQ.

## Ruling 1 (T-16 bundle graph) — closes PF-45518258, confirmed by full-graph trace

`T-16 depends_on: [T-12, T-15, T-21]`. Traced every task that writes under
`dashboard/client/src/**`: T-04 (scaffold) -> T-13 (shell) -> T-14 (panels) -> T-15 (charts) ->
T-21 (mounts charts into panels.tsx). T-16 transitively depends on all five via the T-21 edge, so
T-16 cannot run before any client-source task completes. T-17 (docs) and T-22 (CI/suite adapter,
`depends_on: [T-03, T-21]`) are the only tasks downstream of T-16 or parallel to it, and neither
touches `client/src/**` — confirmed by grep across the whole plan. No task can invalidate the
committed bundle after T-16 runs. The fix is sound, not merely locally plausible.

## Ruling 2 (BRIEF-approval origin) — holds end to end, one architectural note (F-1)

D-14 states the rule once, in full. D-19, D-21, T-10 and T-19 correctly *cite* D-14 rather than
restate it — T-10/T-19 go further and explicitly forbid re-deriving it ("kpi.py is its only source
here... do not read plan.yaml for it"), sourcing `approved_on` from kpi.py's already-computed
field. T-06's read spec (locate `## Approval`, require `status: approved`, take `date:`, treat
date-only as `00:00:00Z`, four named gap states) points at real in-repo precedent
(`check-state.sh:257-263` `approved`/`has_approval_block`, `gh-sync.py:322` `parse_brief`'s
`section()` helper) and is buildable without inventing a parser shape. No literal `approval.date`
survives outside D-14's own `because` (sole sanctioned occurrence, verified via
`harness_yaml.load_plan` on the live YAML, comments excluded).

**F-1 is the one place this pattern isn't followed**: T-11's `feature_start()` (touchpoints.py)
independently *restates* the same BRIEF-read logic verbatim rather than citing/reusing kpi.py's
implementation the way T-10/T-19 do. No shared helper module exists anywhere in `bin/` for "read a
BRIEF approval date" (confirmed: `harness_yaml.py` has none). This is architecturally forced —
`touchpoints.py count --feature <FEAT>` is a standalone CLI called by the orchestrator/pm/validator
with no access to kpi.py's per-feature loop, and kpi.py *imports* touchpoints.py (T-11: "Wire count
into kpi.py"), so the reverse import would cycle. Given that constraint, two implementations are
required — but nothing enforces they stay identical after today. See DIGEST for severity/scenario.

## Ruling 3 (D-22/T-02/T-20) — closes PF-3b85f188, gate is real not decorative

T-02's compound verify: `merge-gitignore.sh --check` (existing rules already merged) plus a
`git check-ignore` assertion against `.harness/metrics/instrumented_at` and this feature's
`touchpoints.jsonl`, run through the real git mechanism — not a grep of the snippet. Reasoned
mutation: add `.harness/metrics/` to `.gitignore` → `check-ignore` returns 0 for both paths → `bad`
non-empty → verify reddens. This *is* a discriminating gate, and pairs the absence check
(`grep -q instrumented_at .../gitignore.snippet`, confirming the comment text landed) with the
presence-of-behavior check (git actually not ignoring the path) — the DEC-169 pairing the review
protocol asks for. One-shot-at-task-completion (no standing CI re-check) matches this same plan's
own convention for `dist/`'s non-ignore guarantee (T-16: `git ls-files` once, no continuous gate
either) — not a departure, so not flagged as a defect.

T-20 is the sole named commit owner; its verify requires `touchpoints.py record`, the event name,
`git add`, and `instrumented_at` to each appear in each of the three instruction files. Confirmed
by grep: today all three files contain **zero** of these tokens, so the check is genuinely red
before the task and can only pass once real instructions are written (no accidental prior-art
false-pass).

## F-2 — T-06's four named gap-state branches, only one gets a fixture

T-06's intent is explicit: "An absent BRIEF.md, an absent Approval section, a status that is not
approved, and an empty or unparseable date are ALL gap states, not crashes." The task's own
fixture-building instruction constructs exactly **one** of the four (`project-a`'s empty-date
feature). No fixture exercises an entirely absent `BRIEF.md`, an absent `## Approval` heading, or a
`status: pending` feature going through this specific code path. See DIGEST for scenario.

Everything else checked and found sound, not re-raised: D-20/D-08/T-18 byte-unchanged since c2;
B-12 stale-comment contradiction accepted backlog, confirmed still 191 lines before/after this
commit per the goalcheck note (not independently re-verified — out of scope); DEC-5 prototype gate
untouched.
