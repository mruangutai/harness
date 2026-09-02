# Research — FEAT-53 plan c4: the seventh KPI in BRIEF and plan — 2026-09-02

**BLUF.** The 7th KPI (merged PRs over time, weekly buckets, sourced from the existing
`.harness/metrics/trend.jsonl`) is landed in BRIEF.md as **REQ-15 / SC-19 / SC-20** and in plan.yaml
as amended **T-10.intent, T-14.intent, T-21.intent, T-21.verify**. No new task, no new decision, no
`depends_on` edit, no third chart shape, no new CAP row. `approval:` and `panel:` are byte-identical
to HEAD; BRIEF `## Approval` is unchanged and still `status: pending`. **Two consequences fall
outside the fields this step was allowed to write and are open questions, not silently dropped:
T-22's adapter still hard-codes only two labels, and no task `traces:` REQ-15.**

## BRIEF.md — what landed

- `## Goal`: "six self-visibility KPIs" -> **seven**.
- **REQ-15** (new, appended): merged PRs visible over time as a windowed count in weekly buckets,
  with the sourcing rule stated where the number is shown — the count is of shipped features read
  from the durable ship record REQ-10 writes, one shipped feature is one merged PR per DEC-200, and a
  record carrying no `pr` still counts as one shipped feature. Empty week -> unavailable with the
  reason naming that week, never zero (REQ-11). Survives swapping every decision beneath it: the
  file, the bucketing code and the chart library can all change without touching the sentence.
- **SC-19** (`verify: automated`, `evidence: integration`): one bucket per week matching the payload's
  own returned week count; each bucket equal to the hand-labelled ship count for that week; a
  `pr: null` record counted, so a `pr`-non-null series fails; empty week `null` with the specific
  reason, asserted neither `0` nor `"0"` (exactly SC-17's shape). `integration`, not `unit`, because
  T-10's asserting script `test-metrics-trend.py` is registered in `INTEGRATION_SCRIPTS` — declaring
  `unit` would reproduce PF-d2fc9563 in a new criterion.
- **SC-20** (`verify: inspection`): the rendered-only clauses — sourcing rule as persistent inline
  text, no per-feature column, no `/features/$featureId` presence — read at `review_sha`. No `ui` SC
  invented; `ui` has no runner.
- `## Constraints`: "Five of six KPIs compute on request" -> **"Five of seven"**, naming the two that
  read an appended log instead (touchpoints, and merged PRs by week) and that neither adds a source.
- `## Verification gaps`: grid literal `3x2` -> **`3x3`**. The rest of that paragraph still holds —
  the digit `3` is still undiscriminating, now occurring twice in the literal.
- Coverage table balanced in both directions (below).

## The SC-18 decision — it DID need amending

T-21 now gates a **third** render case, so SC-18 as written under-described its own gate. SC-18 now
names three cases (grading panel, a trend panel, the merged-PR panel), keeps "the two chart shapes"
(still two shapes, four mounting panels), and reads "All three cases … each is demonstrated failing
first". The `## Verification gaps` sentence that said the gate "asserts the two chart mounts … and
nothing else" now names the three gated mounts, so BRIEF and T-21 agree. Not amending it was the
alternative and it was rejected: a criterion that describes two cases while its gate grades three
leaves the third un-owned by any SC.

## plan.yaml — the four amended fields

- **T-10.intent** — `read()` also returns the weekly merged-PR series: one bucket per week ascending,
  value = count of **shipped features** (not populated `pr` fields, with DEC-200's reason stated),
  empty bucket `null` with the verbatim D-19 reason `no ship record in the week of <YYYY-MM-DD>`,
  pre-segmented into contiguous runs like every other series. Bucket boundaries come from
  `kpi.resolve_window` (T-06) — the same one-authority rule the task already carried; DESIGN Q4 is
  satisfied by returning the window's **week bounds** (week count + empty-bucket count) so the tile's
  secondary line and each reason's week date are computable client-side. Six new test assertions
  appended in the existing list's voice, including neither `0` nor `"0"`.
- **T-14.intent** — `3x2` -> `3x3`, seven tiles named, tiles 1-6 across rows 1-2 and tile 7 last
  spanning the full third row at every breakpoint; four trend KPIs (1,3,5,7) get sparklines. New
  TILE 7 paragraph (40pt headline, secondary line taken from the payload's bounds rather than
  recomputed, last eight weekly buckets, `sourcing_rule` inline as the escaped-defects tile does,
  empty bucket via `UnavailableValue`/S-4 and never `0`) and a PANEL 7 paragraph (Shape B reused,
  mounted by T-21; the ships feature table takes no `TBL-n` id; an empty week is not a row). States
  explicitly that KPI 7 has no `/features` column, no `/features/$featureId` presence and that
  `sort=7` is invalid, so nobody adds one.
- **T-21.intent** — mount list three -> **four** trend panels; third VERBATIM case label
  `merged PR panel mounts the Shape B weekly line`, asserted like the other two (`getByTestId`
  `chart-shape-b` plus DOM-level `querySelector`/`querySelectorAll` inside that element's own
  subtree — at least two `svg path` descendants over a fixture with two runs separated by an empty
  week, which is also what proves the empty week broke the line). The paragraph that invited an
  optional third case is **reconciled**: the three labelled cases are gated and not optional; the
  S-1 negative is the one that stays optional and ungreped.
- **T-21.verify** — one label added to the watched list. Mechanism unchanged: same
  `--reporter=json`, same `raw_decode`, same `status == "passed"` requirement, same
  `not passed: …` failure message.

**T-15.intent was NOT amended** and needed no change: Shape B already renders one line per
pre-segmented run over a temporal scale, so a single weekly series is the shape it already builds.
Amending it would have been the capability-adding signal the dispatch warned about. T-14.verify also
untouched — no new gap-state component name.

## Verification run

- `harness_yaml.load_plan` loads the file: **22 tasks, 22 decisions**. Every `depends_on` id exists,
  graph acyclic, and all twelve pinned edges (T-06/07/08/09/10/11/19/14/15/21/16/17) compare equal to
  the dispatch's list — zero deviations.
- `approval:` and `panel:` blocks extracted and compared byte-for-byte against `git show HEAD:` —
  identical (62 and 8445 bytes). BRIEF `## Approval` appears in `git diff` as context only.
- **T-21.verify proved discriminating** by extracting its `python3 -c` body from the loaded plan and
  feeding it fabricated reporter JSON: all-three-passed -> exit 0; merged-PR case `skipped` -> exit 1
  naming that label; `failed` -> exit 1; trend case `skipped` -> exit 1. The new label is
  load-bearing, not decorative.
- `check-plan-routes.py <plan>`: every task OK. Its single reported violation is the pre-existing
  worktree-vs-owner `team-config.yaml` manifest DEVIATION, unrelated to this step (no lane, file
  list or routing field was touched).
- **Coverage balance, how it was checked:** the table was parsed into left pairs (REQ -> SC) and
  right pairs (SC -> REQ) and the two sets differenced both ways. Result: 15 REQ rows, 20 SC rows, no
  empty cell, no unknown id, and **set difference empty in both directions**. Fixing that surfaced
  two *pre-existing* asymmetries — SC-16 traced REQ-02 and SC-15 traced REQ-12 with neither named on
  the REQ side — now added, so the table balances rather than nearly balancing.
- Grep confirms no accuracy / handoff-eval KPI in either artifact: `accuracy`, `handoff-eval`,
  `FEAT-54`, `required-facts` all absent from BRIEF.md and plan.yaml. The single `eval` occurrence in
  BRIEF is the pre-existing `test_kinds` runner-gap sentence.

## Open questions as raised — BOTH now closed by the send-back section below

1. **T-22 still gates only two of the three labels.** Its intent says "EACH of the two labels" and
   names them, and it is the adapter that makes the render gate a suite gate and a CI gate. Left as
   is, the merged-PR mount is gated only by T-21's hand-typed verify and never by
   `run-unit-tests.sh` or CI — the weaker half of the very gate SC-18 rests on. T-22.intent is
   outside the field list this step was granted.
2. **No task `traces:` REQ-15.** T-10, T-14 and T-21 carry the work but their `traces:` lists were
   not writable here, so the goal-check will find REQ-15 untraceable to shipped code. One-line fix on
   any of the three (`traces:` + `REQ-15`), needing a dispatch that grants the field.

## Send-back — both open questions CLOSED — 2026-09-02

**Q1.** `T-22.intent` now requires **three** labels: "FAILS unless all FOUR hold" (exit 0 plus each
of three labels), the three quoted one per line so no wrap can split one, and a new sentence saying
they are matched literally on both sides and must stay byte-identical to T-21's strings. "either
case" -> "ANY of the three cases" in the skip paragraph, and the DIGEST line asks for three case
statuses. Every other rule survives verbatim, checked by assertion on the whitespace-normalised
value: assert-status-never-presence, `json.JSONDecoder().raw_decode` from the first `{`, NO SOFT
SKIP, the absent-from-the-JSON-is-a-failure-named-as-absent clause, and the `INTEGRATION_SCRIPTS`
registration. Diff of the field is exactly three paragraphs.

**Label comparison, programmatic, not by eye.** The third label was extracted from `T-21.intent`
and from `T-21.verify` by regex and asserted equal before being written into T-22 — never retyped.
Re-extracted from the amended plan: T-22.intent's three labels compare **equal, ordered and
byte-for-byte, to T-21.verify's watched list** (`True`), and the merged-PR label is identical across
all three fields, occurring exactly once in each — `merged PR panel mounts the Shape B weekly line`,
len 46, sha256 `c2a8c3a0…`.

**Q2.** `REQ-15` appended (order preserved, nothing lost) to `T-10.traces` -> `[REQ-10, REQ-11,
REQ-15]`, `T-14.traces` -> `[…, REQ-11, REQ-15]`, `T-21.traces` -> `[…, REQ-12, REQ-15]`. **T-22
deliberately NOT traced to REQ-15:** it delivers no part of the series, tile or mount — it makes
T-21's assertion reachable from `run-unit-tests.sh` and CI, which is verification, not delivery. The
plan's own convention agrees: T-22 already gates the trend-panel case while tracing `[REQ-07,
REQ-12]` and not REQ-10. Tracing it would let a goal-check score REQ-15 covered by a script that
renders nothing.

**Re-verified after the four amends.** Plan loads at 22 tasks / 22 decisions; every `depends_on` id
exists, graph acyclic, and the edge set is **identical to HEAD** (no edge changed); `change_type`
present on every task; `approval:` (62 B) and `panel:` (8445 B) byte-identical to `git show HEAD:`;
`check-plan-routes.py <plan>` 0 violations. A field-by-field diff against HEAD shows this step's
four fields plus the previous step's four; the other eight differing fields (`D-14.choice`,
`D-21.choice`, `D-22.choice/because`, `T-06.files/intent`, `T-11.intent`, `T-19.intent`) are the
concurrent V-1..V-5 sibling edits, untouched by this step's per-field splices.
