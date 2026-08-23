# Plan amendment — FEAT-32, eight items, observed at `62f861c`

**BLUF.** All eight items are applied. `plan.yaml` is 17 tasks / 10 decisions, `safe_load`s clean,
`check-plan-routes.py` exits 0 with 0 violations. **Both approvals are still `pending` and
byte-identical** — asserted programmatically before each write. Q3's ruling reshapes T-14 from a
plan.yaml-only denial into a check that READS `main_session.writes`, which generalises the same
denial to three files with one mechanism. Nothing was posted to GitHub.

## The one overturn to report

The dispatch cited **DEC-119** as check-domain.sh's fail-open-loudly precedent. It is not there:
`awk` over `DECISIONS.md:2356-2408` for `fail.open|loud` returns **zero lines**. The real precedent
is **DEC-127 @2805**, whose body at `DECISIONS.md:2839` reads "fail OPEN, LOUDLY, on our own bug,
matching `check-domain.sh`'s precedent" — plus check-domain.sh's own comments at `:798` and `:811`.
D-10 now cites those, not DEC-119.

## Anchors re-derived at `62f861c` (old → new)

| Claim | Old | New at `62f861c` |
|---|---|---|
| DEC-120 index row | ~`:141` (guessed) | `DECISIONS-INDEX.md:139`, entry `@2408`, carrying sentence `DECISIONS.md:2431` |
| DEC-112 index row | `:141` (guessed) | `DECISIONS-INDEX.md:131`, entry `@1915`, "writes `## Approval` on an explicit yes" at `:1931` |
| DEC-129 | cited as approval authority | `@2954`, **zero** occurrences of "approval" — citation was wrong |
| DEC-174 am.4 enumeration | `:4851-4853` | heading `:4836`, enumeration sentence **`:4859-4860`**, "category decides, list records" `:4860-4862` |
| fail-open-loudly | DEC-119 region | **DEC-127 @2805**, body `:2839`; code `check-domain.sh:798`, `:811` |
| `stop_hook_active` | comment cites `:838` | statement at **`:845`** (comment at `:580`) |

## Premises re-verified (all held)

1. `grep -c main_session check-domain.sh` → **0**. The list is read by no code.
2. `validate-digest.py:580` cites `:838`; statement at `:845`. Only three `stop_hook_active` hits: `:580`, `:817` (docstring, no line cited, correct), `:845`.
3. `team-config.yaml` cites DEC-129 on **three** lines: `:89`, `:90`, `:91`. Line `:108` cites DEC-129 *legitimately* (per-feature `DESIGN.md` layout) — this caught a defect in my own first draft of T-15's verify, which asserted `"DEC-129" not in src` and would have failed on `:108`. Now scoped to the three `except` lines.
4. **The hole is three files wide.** `team-config.yaml:89`/`:90` grant pm `BRIEF.md` and `PLAN.md` whole; `except ## Approval` beside them is a comment. With zero `main_session` reads in check-domain.sh, a pm writing `status: approved` into a BRIEF is unrefused today.

## Decisions I made

**T-15 → T-14 build order.** `T-14 depends_on: [T-03, T-15]`. **T-15 supplies the entry.** T-14's
behavioural cases use hermetic fixtures (which is what lets cases 9–11 vary the list at all), but
new case 14 reads the **real** `.harness/team-config.yaml` and asserts the entry. That case is what
keeps noticing a future deletion, because `test-check-domain.py` runs in the `integration` kind on
every CI run whereas T-15's verify runs once at build. T-15's `depends_on` stays `[]` — no cycle.

**REQ-11 vs SC-20 — both, minimally.** `BRIEF.md:64` said "a feature **plan's** approval block". A
`BRIEF.md` is not a plan, so REQ-11 did **not** cover the generalisation, and T-14 (which
`traces: [REQ-11]`) would have exceeded its source. So REQ-11's noun is widened to "a feature's
approval block — in any of the three forms `main_session.writes` names", and **SC-20** is added for
the two forms it previously excluded plus the load-bearing-list residual. SC-17 already covers the
plan.yaml half; SC-20 does not duplicate it.

**T-17 lane: `team` / `harness-documentor`, matching T-13's precedent** for `DECISIONS.md`.
`DECISIONS.md` is a doc, not a gate script, so DEC-174 does not reach it. `depends_on: [T-13]` to
serialise the two writers of that file and its index.

## SC-14, re-observed at `62f861c` (was `5d9b428`)

Metric is the SC's own: lines matching `^PASS |^FAIL |ERROR`, `CLAUDE_PROJECT_DIR` exported to this
worktree.

| kind | exit | metric lines | begins `FAIL` | contains `ERROR` |
|---|---|---|---|---|
| unit | 0 | **179** at `62f861c` | 0 | 0 |
| integration | 0 | **221** at `62f861c` | 0 | 3 |

Unit is unchanged from `5d9b428`'s 179. Integration moved **93 → 221** because FEAT-30 added to
`INTEGRATION_SCRIPTS`. The "three `ERROR` lines" claim from the old baseline still holds exactly.
SC-14 now binds exit-0-plus-no-`FAIL` as the mechanical gate **and** the counts as a shrink
detector, because exit 0 with no `FAIL` is also what a suite that stopped running tests returns.

## Item 7 — the template defect is ABSENT, zero cost

`grep -n phase .claude/skills/harness/templates/plan.yaml` returns **nothing**. The template carries
no `phase` key, so #635's playbook-vs-schema divergence does not reach it. No fix proposed, no cost.
The template's real defect is the approval comment naming the orchestrator — already T-15 item 1.

## Item 3 — T-10 restructured

The six out-of-scope files are now named **nowhere** in T-10. Its intent carries an
`OUT OF SCOPE - SEE ISSUE #639` heading that states the class is tracked in #639 and says the files
are enumerated **there and deliberately not here**, so a text search for one of them lands on the
issue that owns it rather than on a task that leaves it unfixed. T-10 still registers exactly two.

## Item 8 — occurrence 7, three places

`BRIEF.md` (the #551 evidence block, "six" → "seven"), `plan.yaml` D-06 `because:`, and T-13's
intent item 4. **D-09's `choice:` now cites it too** — occurrence 7 is the strongest evidence in the
feature for D-09's own argument that #551's harm is FALSE REPORTING, so D-09 was reasoning from 3–6
while its best datum sat unrecorded. `STATE.md` also carries occurrences 5/6 but is the
orchestrator's file, not mine.

## Open items for the signature

- **Q1 (non-blocking).** T-14's scope grew from one file to three. That is a consequence of sourcing
  the denial from the list rather than an independent widening, and refusing it would mean
  hardcoding a plan.yaml special case out of a list whose other two entries state the same rule —
  but it is the item's real scope cost and the operator should see it named.
- **Q2 (non-blocking).** T-17 amends a signed decision. The approval of this plan is the signature
  on that exact wording; the task says so and instructs the doer to STOP rather than improve it.
