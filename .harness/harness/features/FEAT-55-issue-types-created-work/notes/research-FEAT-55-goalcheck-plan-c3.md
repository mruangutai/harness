# Goal-check c3 — does the REVISED FEAT-55 plan deliver the operator's stated intent?

**YES.** Both operator rulings are in the plan, neither widened; all eleven baseline findings
(F-01..F-09, N-01, N-02) are still CLOSED — none reopened by the c2/c4 revision; and REQ-07's
refuse-before-create is now enforced by the `verify:` blocks on all three creation routes.
Two findings open, highest **med**, neither gating and neither settled by a ruling: they go to the
operator, not into my own judgement.

Graded against `.harness/notes/grilling-issue-types-2026-09-04.md` (the stated intent, not BRIEF),
reading `plan.yaml` and `BRIEF.md` directly. Anchors are working-tree lines at
`plan.yaml` sha256 `d8f98dfc4491…`, `BRIEF.md` `ab2d6de25377…` (both unchanged by me, verified at
entry and exit). `approval: {status: pending}` in the loaded plan; BRIEF `## Approval` pending
(`BRIEF.md:205`). 12 tasks, 20 decisions, `status: plan`, 7 panel findings.
`check-plan-routes.py plan.yaml` → 0 violations, exit 0 (T-12's DEC-174 line is the carve-out).

## Ruling 1 — PF-f1031f76b4537f1cd9b60ddc0559b7d1 (high, gating): APPLIED, faithfully

Judged on the `verify:` blocks as read, per route — not on `intent:` prose and not on the repair note.

| Route | REQ-07 in `traces:` | case-letter loop enumerates the refusal case | required-string loop names its markers |
|---|---|---|---|
| open — T-03 red / T-04 green | `:448`, `:561` | **yes**, `F` in `:457` | **no** — `:460` lacks `partial`, `github.issue_types` |
| backlog — T-05 red / T-06 green | `:696`, `:787` | **yes**, `G` in `:706` | **yes**, `:709` |
| factory — T-07 red / T-08 green | `:859`, `:973` | **yes**, `I` in `:869` | **yes**, `:872` |

The green half is bound too: T-06's `verify:` runs `test-gh-backlog-issue-types.py` (`:795`) and
T-08's runs `test-factory-issue-types.py` (`:982`), so each writer's gate executes the file carrying
its route's new case. The refusal cases themselves (T-05 G `:770-783`, T-07 I `:954-969`) assert the
mode the panel named — zero `issue create`, zero `updateIssue`, non-zero exit, message naming both
`Task` and `github.issue_types` — and T-07 I binds the **parent's** create as well.
No widening found: no traces added outside T-05/T-07, no new task, no new decision id.

**BRIEF SC-08 (`:132-139`) reworded** — an edit to an approval-gated artifact, in scope of the ruling
and no wider: it names the three creation commands, requires the assertion per command in that
command's own test file, states one command's refusal never discharges another's, and keeps
`verify: automated / evidence: integration`. `## Approval` untouched. The operator's signature must
knowingly cover this reword.

## Ruling 2 — PF-610431f7d96408d23666cc4e60071501 (med): probe KEPT, D-19 `because:` only

`D-19.choice` (`:121`) still reads default-read-only + explicit opt-in naming the target repository —
unchanged. `because:` (`:122`) no longer asserts an absent grant: it records the grant, cites
`notes/answers-plan-panel-20260904.md`, bounds it to the flag, and keeps the
registered-kind-runs-unattended reason. Unchanged as required: T-10 §6 (`:1162-1179`), T-09's
"never register the create opt-in flag in cmd" (`:1099-1102`), SC-10's LIVE verdict
(`BRIEF.md:146-148`), and the eighth read-back purpose's third clause (T-11 `:1232`/`:1240-1241`,
T-12 `:1279`). No decision id added.

## The eleven baseline findings — each still closed

| F | Still closed, re-verified in the plan text |
|---|---|
| F-01 high | T-03 H/H2 `:533-543`, T-07 F `:928-936`; `adopted` in T-04 ×6 / T-08 ×4 intents |
| F-02 med | T-10 `verify` untouched — repo-resolving verdict leg + `PATH`-stripped SKIP leg intact |
| F-03 med | T-11 §3 and T-12 §1 pinned row still byte-identical: 511 chars, sha256 `7f065a7a5225` |
| F-04 med | zero-create diagnostics: T-03 D `:513-517`, T-05 D `:744-754`, T-07 G `:937-942` |
| F-05 med | D-18 `:117-118`, T-02 table, T-03 A `:498-503`, T-07 A `:900-906` |
| F-06 low | T-01 `verify` still greps `UnknownWorkNature` (unedited) |
| F-07 low | T-06 §5 receipt gated on `available` `:829-838`; T-05 C `:738-743`, F `:763-769` |
| F-08 low | D-19 `choice` unchanged; T-09 `:1099-1102` forbids the flag in `cmd` |
| F-09 low | compat controls: T-06 `verify:796`, T-08 `verify:983-984` |
| N-01 high | `ABSENT → NEVER typed` in T-08 §8 and T-04 §6; D-20 `:124-145`, D-10 tail; T-03 J `:546-557`, T-07 H `:943-953` |
| N-02 low | backfill set inside `missing_types` — T-04 §4 / T-08 §6 unedited |

c2's own advisories were closed by the c3 repair, not by this revision: N-03 → `SC-12`
(`BRIEF.md:164-174`) now grades REQ-10; N-04 → T-05 case E asserts `typed` **exactly false**
(`:755-762`). N-05 and N-06 stand as recorded info.

## The five unruled panel findings — untouched, still theirs to rule

`PF-1286544c197d1b0eb4a9b0dc8e1234dc`, `PF-452948136bf467869d223e027191ae49`,
`PF-e27f1c3018b6b8477547a1b028607f96`, `PF-0c12a033f69bb6bc60b8f96134f94fd0`,
`PF-9a71cb9a0c590b06b890ff1517b80385` — all still `disposition: batched_to_signature_review`
(`:199-239`). Not re-disposed, not softened, not dismissed here.

**Coupling the operator must see:** T-05's new case G is authored against T-06 §5's *currently
specified* receipt shape — a plain `json.dump` of `{"items": {...}}` at
`<featdir>/backlog-issues.json` (`:829-845`) — which is exactly the subject of the unruled
`PF-1286544c…`. Case G's "no `backlog-issues.json` exists afterwards" assertion (`:776`) would need
re-authoring if that finding is later directed as a fix, as would cases C, E and F.

## Findings

- **C3-01 · low · the ruled routes are gated harder than the unruled one.** T-03's required-string
  loop (`:460`) omits `partial` and `github.issue_types`, so on the **open** route case F is bound
  only by its `CASE F:` marker, while backlog and factory are bound by marker plus both strings.
  Ruling 1 is met on all three routes; the enforcement is uneven. One-line repair per loop. Neither
  ruling settles it → Q1, non-blocking.
- **C3-02 · med · the panel record is now stale.** `PF-f1031f76b4537f1cd9b60ddc0559b7d1` still reads
  `disposition: awaiting_user` (`:172`) after the operator ruled and the fix landed;
  `harness-spec-driven` requires a finding pm believes fixed to carry `disposition: resolved` with
  `resolved_by:`. This step is read-only, so I did not write it. → Q2, non-blocking.

## Open questions for the operator

- **Q1 (C3-01):** add `partial` and `github.issue_types` to T-03's required-assertion loop so all
  three routes are gated identically, or accept the open route's marker-only binding?
- **Q2 (C3-02):** who updates PF-f1031f76…'s disposition to `resolved` / `resolved_by: T-05,T-07` —
  a pm write dispatch before signature, or is it left for the `approval.rulings` write?
