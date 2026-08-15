# Review — harness-ui-reviewer — FEAT-20 follow-up, PR #385 (a714bd0 vs 3c75aa6)

## Scope census (measured)

`git diff --name-status 3c75aa6..a714bd0` — 8 files, all `.sh` / `.py` / `.yaml` / `.md`:

```
M .claude/skills/harness/bin/check-state.sh
A .claude/skills/harness/bin/layout_fixtures.py
M .claude/skills/harness/bin/layout_migration.py
M .claude/skills/harness/bin/test-check-state.py
M .claude/skills/harness/bin/test-layout-migration.py
M .harness/features/FEAT-20-migration-detector/plan.yaml
M .harness/logs/2026-08-14.md
M docs/harness/DECISIONS.md
```

No `.html/.css/.scss/.tsx/.jsx/.vue/.svelte`, no `DESIGN.md`-governed rendered surface anywhere in
this diff. Ordinary Mode A/B UI review is out of scope — **except** the one surface the dispatch
explicitly handed me: the reworded INV-27 diagnostic text in `check-state.sh`, which a human reads
at session entry. Treated as in-remit per this role's own P-06 (a dispatch that names an adjacent
non-rendered surface puts it in-remit).

## Finding — diagnosis clause and blame list can now disagree (real, PASS-level, non-gating)

`check-state.sh:1290-1310` composes two `CANNOT_VERIFY` messages from `layout_migration.blame()`:

- cause `"unreadable"` → `"a coupled reader could not be read — {blame(rep)}"`
- cause `"neither"` → `"a coupled reader matches neither form — {blame(rep)}"`

Before this PR, each clause filtered `rep.readers` to only the matching form (`_tagged(_form)`), so
the list always agreed with the clause — at the cost of silently dropping other co-occurring defects
on the same surface (a real prior bug: an unreadable reader *and* a `[neither]` reader on one surface
would report only the first, costing the operator a second round trip).

After this PR, both clauses render `layout_migration.blame(rep)` **unfiltered by cause** — the same
list `render()` uses for `MIXED`. `blame()`'s own selection (`layout_migration.py:262-273`) names any
reader tagged `both`, `neither`, or `unreadable`, plus any reader disagreeing with a single evidence
shape — regardless of which cause put the surface into `CANNOT_VERIFY` in the first place. `scan()`
picks cause by priority (`unreadable` first, then `neither`, `no-evidence`, then `MIXED`) and
`continue`s immediately, so a surface with cause `"unreadable"` can still hold co-occurring `[neither]`,
`[both]`, or (via the evidence-disagreement clause) `[migrated]`/`[legacy]` readers, all pulled into the
list.

Measured (constructed the module's own `blame()` against synthetic `SurfaceReport`s — output below):

```
cause="unreadable", readers=[a:unreadable, b:neither, c:migrated, d:legacy], evidence={legacy}
  → blame = [(a,unreadable), (b,neither), (c,migrated)]
  → renders: "a coupled reader could not be read — a [unreadable], b [neither], c [migrated]"

cause="neither", readers=[x:neither, y:both, z:legacy], evidence={legacy}
  → blame = [(x,neither), (y,both)]
  → renders: "a coupled reader matches neither form — x [neither], y [both]"
```

Both are reachable in practice, not just synthetic: `features` has 4 coupled-reader rows and `docs`
has 3 (`layout_migration.py` `READER_TABLE`), and FEAT-20's own migration sequence edits these rows
independently unit by unit — exactly the condition that produces mixed forms across rows on one
surface while the migration is mid-flight.

**Effect on legibility:** the diagnosis clause is singular and specific ("could not be read" /
"matches neither form"), but the list behind the em-dash can now contain readers tagged with a
*different, sometimes contradictory* form (`[both]` under a "matches neither form" headline;
`[migrated]`/`[neither]` under a "could not be read" headline). A human reading the finding at
session entry sees a tag that doesn't match the sentence naming it. The remedy sentence
(`_lrem`, appended after the list) stays intact and generic, so remedy-vs-diagnosis separation is not
affected — only the diagnosis-clause-vs-list-content pairing is.

**This is an incomplete refactor, not a regression in coverage.** The stated purpose of unifying on
one `blame()` (`# ONE blame policy, owned by the module (issue #379)`) is real and correct — the old
per-form filter silently dropped co-occurring defects, which is worse. The list is now complete; only
the two CANNOT_VERIFY clause sentences weren't reworded to be cause-agnostic to match. The fix is
wording (e.g. "a coupled reader disagrees with this surface's expected form" or similar), not
re-filtering — re-filtering would reintroduce the exact drift #379 exists to kill.

**No test exercises this.** `test-layout-migration.py` has zero references to `blame` at all; the one
`test-check-state.py` case for cause `"neither"` (`:2796-2802`, "x.2 a tree it CANNOT JUDGE: one
reader carries neither form") uses a single-defect fixture, not a mixed-form one. The edge case is
unguarded by the suite that would otherwise catch a future wording drift here.

**MIXED branch — unaffected, checked and closed.** `blame()`'s `both`/`neither`/`unreadable`
membership check can never surface `neither` or `unreadable` tags inside the `MIXED` branch, because
`scan()` routes any surface holding such a reader into `CANNOT_VERIFY` (cause `unreadable`/`neither`)
before the `MIXED` check runs — `continue` short-circuits it. So for `MIXED`, `blame()` is
behaviourally identical to the pre-PR `_blame` computation; the "readers {list}" sentence there is not
newly ambiguous.

## Not filed (out of scope / already handled)

- `test-check-state.py` duplicate `def case_x` at :1585/:2719 — already flagged by the dispatcher.
- #365/#367/#368-375/#377/#378/#380/#381/#384/#279 — pre-briefed, not re-derived.
- No accessibility or theme-parity dimension applies: this is batch/CLI stdout text, no markup, no
  colour-only state encoding, no rendered surface — both are explicitly n/a, not silently omitted.

## Verdict rationale

Not a `DESIGN.md` contract violation (none exists in this diff — census above). Not an accessibility
exclusion (no rendering, no colour). It is a real, measured communication-clarity defect in a
CI/session-entry diagnostic that the dispatch asked me to judge directly, worth `severity: med` and a
non-gating note — the finding is legitimate but the current text remains actionable (form tags are
still correct per-reader; only the clause-vs-list pairing is loose), so it does not meet this role's
`must_fix`/`high` gate bar.
