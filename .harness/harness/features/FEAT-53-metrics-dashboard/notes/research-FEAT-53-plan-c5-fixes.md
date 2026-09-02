# Research — FEAT-53 plan c5 record fixes (B-19, B-20, B-21, B-22, B-24)

**All five advisory fixes are applied to `plan.yaml` and `BRIEF.md`, the seven cycle-4 panel
findings carry their dispositions, and both approval blocks are byte-identical to their pre-run
state (sha256 proof below).** Nothing about the build changed: no `verify:`, no `files:`, no
`depends_on:`, no new library, no new mechanism. The one item this file first left uncited — the
DESIGN.md half of B-21 — was cited later in the same run once the sibling's edit landed
(*Follow-up*, DESIGN.md:249-252).

## Approval blocks — proof of byte identity

Captured before the first write, re-read after every write. Same sha256 both times.

`plan.yaml approval:` — `96666915d78504ef0538dc3c3a15bf67dde5100450173cb7403bddb26440cce3`

```
approval:
  status: pending
  approved_by: none
  date: none

```

`BRIEF.md ## Approval` — `76b3b76dabd0883aa03ade3ae653ba5f352719b59856f7532e94224e0f121d3f`

```
## Approval

status: pending
approved-by:
date:
```

## What changed, field by field

Diff of the parsed documents, pre vs post: **task fields changed = `T-07.intent`, `T-10.intent`,
`T-19.intent`; decision changes = `D-08.choice`, `D-08.because`, `D-20.because`, `D-23` (new);
panel = the 7 cycle-4 findings only.** Nothing else in either file.

**B-19 → `T-19.intent` (plan.yaml:1279-1291).** Excerpt: *"BOTH COMMIT BRANCHES MUST BE COVERED,
and the case that covers the SUCCEEDING one makes the copy a git repository first: run git init in
the copytree temp copy of fixture project-a and set a LOCAL user.name and user.email … asserts …
the copy's working tree is CLEAN (git -C &lt;copy&gt; status --porcelain prints nothing) and that
.harness/metrics/trend.jsonl is TRACKED in that copy … present on disk is NOT the assertion … KEEP
the existing non-git case as well, explicitly labelled as the FAILURE-BRANCH case"*.

**B-20 → `T-10.intent` (definition at plan.yaml:741-753, fixtures at :774-781).** Excerpt:
*"weeks are UTC ISO-8601 weeks — each bucket starts Monday 00:00:00Z and ends the next Monday
00:00:00Z, EXCLUSIVE … Each bucket's LABEL … is that bucket's own Monday date. For 30d and 90d the
FIRST bucket is the ISO week CONTAINING the start resolve_window returns … that is DERIVED from
resolve_window and is not a restatement of a window boundary, so the one-authority rule stated in
this task and in T-06 still holds … For all, which is unfiltered and returns NO start, the series
is anchored at the ISO week containing the EARLIEST record's shipped_at … If there are NO records
at all the weekly series is EMPTY and carries its own reason in the unavailable map"*. Fixtures
added: the `all` anchor, and two records one minute either side of the same Monday 00:00:00Z each
asserted into its own bucket.

**B-21 → `D-08.choice` (:72), `D-08.because` (:73), `D-20.because` (:121), BRIEF `## Constraints`
(:77-82, :88-90).** `D-08.choice` now: *"the alpha is ACCEPTED, ruled by the operator on 2026-09-01
(notes/answers-2026-09-01-plan-signature.md, DEC-3), with the rollback named in this decision's
because clause; the capability trigger is unchanged — any of CAP-01, CAP-05, CAP-07 or CAP-11 unmet
at T-18's probe."* The struck clause (*"NO FALLBACK LIBRARY IS NAMED - what to do when the trigger
fires is an operator decision outstanding at signature"*) is gone.

The rollback in `D-08.because`, composed only from DESIGN C-2 (read at DESIGN.md:258-281, both
columns) and D-04/T-04: **(a)** exact version pin in the client `package.json` (T-04) plus the
committed bundle (D-04), so no upstream alpha change reaches a user without a task's explicit
version bump; **(b)** where the `If absent` cell names a workaround it *is* the rollback, applied
in place with no library change — **CAP-02** five single-bar series, **CAP-03** datum-derived hatch
computed server-side, **CAP-04/CAP-10** hand over to S-1 before mount, **CAP-06** own bin labels,
**CAP-09** server-side segmentation into contiguous runs (already unconditional in T-10),
**CAP-12** ours to supply, **CAP-13** resize observer; CAP-08 is not a fallback (C-2
pre-authorised three stacked single-series plots); **(c)** the four rows whose cell reads *hard
requirement* — **CAP-01, CAP-05, CAP-07, CAP-11**, exactly the trigger set, CAP-11 additionally
offering an overlaid-marker series for its dash/shape half — give `T-18` VERDICT STOP, chart tasks
do not start, and the replacement library becomes an operator decision taken *then*. No fallback
library is named in advance because none survives the React 19 substrate check today
(react-charts: last published 2023-11-02, React 16 peer — sentence kept verbatim).

`D-20.because` tail now: *"RULED by the operator on 2026-09-01 … the client build is KEPT and this
decision stands as drafted. The server-rendered alternative was weighed and REJECTED … so the
disclosure above stands as a recorded consideration of what was weighed, not as a question open at
signature."* BRIEF's two bullets carry the same two rulings; the react-charts-is-dead sentence and
the disclosure itself are both kept.

**B-22 → new `D-23` (plan.yaml:163-199), `dec: none`.** Names all fourteen accepted rows — B-1,
B-2, B-3, B-4, B-5, B-7, B-8, B-9, B-10, B-12, B-13, B-14, B-23, B-25 — with a one-line subject for
the six that have no panel disposition (B-7..B-10 from the cycle-1 briefing table lines 126-129,
B-23/B-25 from the cycle-4 table lines 116-118). `because` records that **B-6 was struck** and
**B-11, B-15..B-22, B-24 were fixed**, so the list is the complete accepted set. Mechanism
unchanged and not invented: one issue per row, label `Dashboard`, at ship.

**B-24 → `T-07.intent` (:578-585) and BRIEF `## Verification gaps` (:157-166).** Removed:
`1024` and `ES2022` from both clauses (BRIEF now contains neither token at all; plan.yaml's
remaining `1024` at :1054/:1085 and `ES2022` at :340 are the real breakpoint and tsconfig target,
untouched, and :2040/:2048 are the immutable C4-06 summary plus my note quoting it). Carriers
written, each verified at source:

|Token|Carrier|Verified at|
|---|---|---|
|`12`|`127.0.0.1`|D-05 (plan.yaml:60); T-12 ships `app.run(host="127.0.0.1"…)` (:869, binding stated :866); T-17's own verify requires `127.0.0.1` in METRICS.md (:1139) and documents the bind (:1144)|
|`12`|`122`|SC-06 greps it in its own right (BRIEF.md:183); T-07 asserts the literal absent (:538 pre-edit); T-14 verify forbids `['107','122']` (:986 pre-edit)|
|`3`|`3x3` tile grid|T-05 *"fixed 3x3 grid of seven tiles"* (:331); T-14 *"a fixed 3x3 tile grid"* (:990)|
|`3`|`python3` start command|T-17 verify requires `python3 -m pip install flask` in METRICS.md (:1139) and the documented `python3 …/serve.py` command (:1144)|

The conclusion is unchanged in both artifacts: `12` and `3` cannot be grepped bare and stay carried
by SC-15's ui-reviewer inspection at `review_sha`.

## Panel

`C4-01, C4-02, C4-03, C4-04, C4-06 → resolved` (with `resolved_by` T-19 / T-10 / D-08 + D-20 /
D-23 / T-07) and `C4-05, C4-07 → backlog`, each note in the existing V-1..V-5 / B-12..B-14 style.
`last_run: 2026-09-02-05-validator` and `cycle: 4` untouched; both readers still recorded as `ran`.
**The 18 earlier findings are byte-identical** — verified by chunking the pre-run and post-run
`panel:` regions per finding id and comparing raw text: 18 identical, 0 differing.

## Commands run — `plan-merge.py` was the only writer of plan.yaml

All from `/Users/molchairuangutai/GitHub/harness` using the **main checkout** binary
`.agents/skills/harness/bin/plan-merge.py`, with
`--file <worktree>/.harness/harness/features/FEAT-53-metrics-dashboard/plan.yaml`:

1. `apply --proposal /tmp/feat53c5/d23.yaml` → `ADDED D-23`
2. `amend --key tasks --id T-19 --field intent --expect-sha256 ff73e892…a71bb --value-file /tmp/feat53c5/t19-intent.txt`
3. `amend --key tasks --id T-10 --field intent --expect-sha256 e8b4c3fa…65277 --value-file /tmp/feat53c5/t10-intent.txt`
4. `amend --key tasks --id T-07 --field intent --expect-sha256 abd3d768…6b8c6 --value-file /tmp/feat53c5/t07-intent.txt`
5. `amend --key decisions --id D-08 --field choice --expect-sha256 6ceba622…ad69c --value-file /tmp/feat53c5/d08-choice.txt`
6. `amend --key decisions --id D-08 --field because --expect-sha256 6e86bc26…4cf841 --value-file /tmp/feat53c5/d08-because.txt`
7. `amend --key decisions --id D-20 --field because --expect-sha256 309a8404…f7080 --value-file /tmp/feat53c5/d20-because.txt`
8. `set-panel --value-file /tmp/feat53c5/panel.yaml` → `PANEL cycle 4`

Value files were composed by anchored substring surgery over the parsed field (`/tmp/feat53c5/mkvals.py`,
`/tmp/feat53c5/mkpanel.py`), each anchor asserted to occur exactly once; the `|` literal blocks keep
their original wrap width and only the region from the anchor's own line to the end of the value is
reflowed. BRIEF.md was edited with the Edit tool (pm's own domain; two hunks). No Write, no shell
redirect, no hand edit of plan.yaml.

**Scoped check:** `check-plan-routes.py <this plan>` → `0 violation(s) across 1 plan(s)`, exit 0.
No project-wide validation, formatter or unit suite was run.

## Open

- ~~DESIGN anchor missing from C4-03's note~~ **CLOSED — see *Follow-up* below.** The sibling's
  DESIGN.md edit landed later in the same run and C4-03's note now cites it at
  `DESIGN.md:249-252`, verified by direct read.
- B-23 and B-25 remain accepted backlog with no plan task, by the operator's pass-4 Q2 ruling;
  D-23 is now their carrier.

## Follow-up (same run) — the landed DESIGN anchor is now cited in C4-03

**One field changed: `panel.findings[C4-03].note`. Nothing else in the file.**

Re-read at source before citing (not taken on trust): `DESIGN.md:249-252` carries the C-2 preamble
clause *"Where a capability's `If absent` cell names a server-side workaround, that workaround is the
fallback; no replacement charting library is named in advance, and naming one would be an operator
decision taken on T-18's probe evidence, needing its own plan Decision."* A grep of DESIGN.md for
`[Rr]eact.?[Cc]harts` returns **no matches** — zero survive. Sibling artifact:
`notes/mockups/design-c5-fallback-fix.md`.

C4-03's note now ends: *"… BRIEF `## Constraints` (BRIEF.md:77-82 and BRIEF.md:88-90) carries both
rulings. The DESIGN C-2 half is applied too: the C-2 preamble now states that where a capability's
If absent cell names a server-side workaround THAT workaround is the fallback, names no replacement
charting library in advance, and records that naming one would be an operator decision taken on
T-18's probe evidence and needing its own plan Decision — DESIGN.md:249-252; the sibling
visual-designer's sweep (notes/mockups/design-c5-fallback-fix.md) found and removed the single React
Charts occurrence and zero survive in DESIGN.md."* Everything before `carries both rulings.` is
byte-identical to the pre-write note.

**Stale-claim sweep over the whole `panel:` region** (tokens `DESIGN.md:250`, `not yet visible`,
`NOT yet visible`, `React Charts`, `react-charts`, `second fallback`):

|Token|in any `note:`|in a `summary:`|
|---|---|---|
|`DESIGN.md:250`|none|**C4-03 — left alone (immutable record of what the panel found)**|
|`not yet visible` / `NOT yet visible`|none|none|
|`second fallback`|none|**C4-03 — left alone**|
|`React Charts`|C4-03, in the new *"found and removed the single React Charts occurrence"* clause — not a stale claim|**C4-03 — left alone**|
|`react-charts`|none|none|

Outside the panel region the token survives only where it belongs and was not touched: `D-08.because`
(:73, the react-charts-is-dead sentence) and `T-04.intent` (:316, the *never* `@tanstack/react-charts`
instruction).

**Per-finding raw-text comparison, pre vs post** (`panel:` region chunked by finding id, same method
as the first pass): **24 identical, 1 differing — `C4-03` only**, and within C4-03 the changed field
set is exactly `['note']` with its key order unchanged. All **18 pre-cycle-4 findings identical**.
`panel:` header identical (`cycle: 4`, `last_run: 2026-09-02-05-validator`, both readers still
`ran`), finding count 25 → 25, id order unchanged.

**`approval:` re-read after the write, verbatim:**

```
approval:
  status: pending
  approved_by: none
  date: none
```

BRIEF.md received **no write this pass** (its modified state in `git status` is the earlier c5 pass).

**Writer:** one call —
`plan-merge.py set-panel --file <FD>/plan.yaml --value-file /tmp/feat53c5b/panel.yaml` →
`PANEL cycle 4` / `APPLIED`. The value file was composed by anchored surgery over the parsed panel
(`/tmp/feat53c5b/mkpanel.py`, anchor asserted to occur exactly once, head asserted to end at
`carries both rulings.`). No Edit, no Write, no redirect against plan.yaml. No project-wide
validation, formatter or unit suite was run.
