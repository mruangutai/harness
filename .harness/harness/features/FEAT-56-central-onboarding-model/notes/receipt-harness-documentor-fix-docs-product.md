# Receipt — harness-documentor — FEAT-56 fix-docs — 2026-09-08

## BLUF

**All four documentation findings closed (V-1, V-3, V-4, V-5-doc-half).** Four written files, not
three: `DECISIONS-INDEX.md` was regenerated because the DEC-220 body edit recomputed that row's
tag set (expected and permitted by the dispatch; named below). All three gate scripts exit 0 —
including `check-instruction-paths.py`, so the pre-existing failure reported earlier in this
feature does **not** reproduce at this tree state. Two sibling-owned files are dirty in
`git status` and were left untouched.

## V-1 — `.harness/harness/docs/SPEC.md:145` (§2.2 routing table, row 1)

BEFORE (`SPEC.md:145`), Condition cell:

> not registered in `.harness/factory/fleet.yaml`, or its own `harness.json` not readable at its `default_branch`

AFTER (`SPEC.md:145`), Condition cell:

> not registered in `.harness/factory/fleet.yaml`, or its own `harness.json` not readable at its `default_branch`, or no central tree at `<control-plane>/.harness/<segment>/`

One row, one cell; Action cell, all other rows and §2.2's surrounding prose untouched (diff is a
single one-line hunk at `@@ -145 +145 @@`). The third element is worded with the same
`<control-plane>/.harness/<segment>/` spelling the other three sites use, so a fifth site cannot
drift onto a synonym.

**Dispatch's quote of SPEC.md:442-452 confirmed against the file** — it matches, verbatim, including
"then create its central per-segment tree at `<control-plane>/.harness/<segment>/`". No convergence
needed.

### Four sites, checked individually (four separate reads/greps, not one sweep)

1. `SPEC.md:145` — grepped for the literal `central tree at \`<control-plane>` in `SPEC.md`; the
   hit is line 145 (quoted above). Third condition present.
2. `SPEC.md:441-445` (canonical statement, read as its own range) — "…**three things, in order
   (DEC-220):** land that repository's own `.harness/harness.json` on its `default_branch`; add a
   `- name: <owner>/<repo>` entry under `repos:` in `.harness/factory/fleet.yaml` … then create its
   central per-segment tree at `<control-plane>/.harness/<segment>/`." Three conditions.
3. `.harness/README.md:83-85` (read as its own range) — "absent from `.harness/factory/fleet.yaml`,
   when its own `harness.json` is not readable at its default branch, or when it has no central tree
   at `<control-plane>/.harness/<segment>/`". Three conditions.
4. `.claude/commands/harness.md:12-14` (read as its own range) — "the repository is not in
   `.harness/factory/fleet.yaml`, its `harness.json` is not readable at its default branch, or its
   central tree `<control-plane>/.harness/<segment>/` is absent". Three conditions.

All four now state the same three, with the same third-element path spelling. Sites 2–4 were not
edited.

## V-3 — `README.md:192` ("## Factory repositories", closing sentence)

BEFORE:

> `/harness-init` registers the repository in `.harness/factory/fleet.yaml`, creates its central tree under `<control-plane>/.harness/<segment>/`, and lands its `harness.json` on its own default branch, which is the only file the harness puts in a product repository (DEC-220).

AFTER:

> `/harness-init` lands its `harness.json` on its own default branch — the only file the harness puts in a product repository — then registers the repository in `.harness/factory/fleet.yaml`, then creates its central tree under `<control-plane>/.harness/<segment>/`, in that order (DEC-220).

Order now lands-config → registers-in-fleet → creates-central-tree, matching DEC-220 and
`SPEC.md:441-447`. Both carried claims preserved: the only-file-in-a-product-repository claim (now
an em-dash aside on the config it qualifies, where it belongs) and the DEC-220 citation. One
sentence in, one out; section length unchanged; the two preceding sentences untouched.

## V-4 — DEC-220, `**Chose:**` paragraph (`DECISIONS.md:6990-6997`)

BEFORE (tail of the paragraph, `:6990-6992`):

> `.harness/products/` is created nowhere. The three are ordered: registration comes **after** the config lands, because the failure of the reverse order has no symptom but an unattributed `FleetError`, and `factory_config.py --check-product-configs` is what names it.

AFTER (`:6990-6997`) — same text, then:

> … is what names it — a check that is OPERATOR-RUN, with no standing invariant behind it. `check-state.sh` never reads a member's config from its remote, and its only network calls record nothing when the network is unavailable, because an offline environment must never become a red gate (`check-state.sh:2270-2273`). So nothing grades a fleet member's remote config on every run, and a member whose `harness.json` is deleted after onboarding stays invisible until the next build against it.

**The dispatch's claim was verified and deliberately narrowed.** The dispatch asked me to state that
`check-state.sh` "deliberately makes no network call". **That is false as written** and I did not
assert it: `check-state.sh` makes `gh` calls in INV-26 and INV-30 (`check-state.sh:2062-2080`,
`:2291-2327`). What is true, and what the entry now says, is the narrower pair of facts that
actually carry the finding:

- **No remote-config read at all.** Grepped `check-state.sh` for
  `product_config|check-product-configs|fleet` — every hit is INV-24/INV-29 reading the local
  `fleet.yaml` file (`:1622-1651`, `:1884-1945`). Nothing anywhere in the script reads a member's
  `harness.json` from a remote.
- **No network result can ever raise a violation.** `check-state.sh:2270-2273`: "Everything else —
  `gh` absent, unauthenticated, the network unreachable, a milestone that 404s — records NOTHING.
  `check-state.sh` runs before every commit, and an offline environment must never become a red
  gate." Same posture at `:2076-2077` and `:2451-2453`.

So the conclusion the finding needs — no every-run invariant can grade a fleet member's remote
config — holds on stronger ground than the handed-down premise.

## V-5 (doc half only) — DEC-220, `**Because:**` paragraph (`DECISIONS.md:7011-7015`)

BEFORE (tail, `:7005-7006`):

> … and the operator struck the central placement on 2026-08-18.

AFTER (`:7011-7015`) — same text, then:

> Reading from that branch also delegates trust: whoever can push a member's `default_branch` controls everything the factory reads for that member, including every `test_kinds.*.cmd`, which is a command the factory executes. A config that will not load fails closed, blocking writes rather than widening them, but a well-formed hostile one is screened by nothing — push access to a member's default branch is factory-level trust.

Disclosure only; no mechanism proposed or changed. `test_kinds.*.cmd` verified as a real, executed
field at `templates/harness.json:96-140` ("dev-ops fills every `test_kinds.cmd` by RUNNING it",
`:2`). The fail-closed half is stated **without** a line citation on purpose: `SPEC.md:450`'s
existing pointer for it, `harness_boundary.py:158`, is **stale** — that line is inside
`linked_worktrees`' docstring about git subprocesses, not a fail-closed write refusal. See stale
note below. I did not repeat a citation I could not confirm.

DEC-220 was not restructured: two paragraph-tail additions, three sentences and two sentences.
No heading, no bold run, no `**Over:**`/`**Record:**` change. Diff is exactly two hunks
(`@@ -6992 +6992,6 @@`, `@@ -7006 +7011,5 @@`).

## Gate scripts — all three, exit 0

```
$ env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md
EXIT_DIFF=0
(no output)
```

**First run of this diff FAILED (exit 1), by my edit, and I regenerated.** The DEC-220 body edit
recomputed that row's tag set:

```
220c220
< - DEC-220 @6985 [plan,state,deploy,domain] refs: DEC-113 DEC-129 DEC-174 DEC-182 :: The central onboarding model: …
---
> - DEC-220 @6985 [plan,deploy,domain,expertise] refs: DEC-113 DEC-129 DEC-174 DEC-182 :: The central onboarding model: …
```

`state` entered and `expertise` left because the new sentences name `check-state.sh` and no longer
tip the expertise tag. Fixed the sanctioned way — `gen-decisions-index.py` with no flags (exit 0),
never by hand. **This is the fourth written file: `.harness/harness/docs/DECISIONS-INDEX.md`.** The
`@6985` anchor and the hand-written ruling right of ` :: ` are byte-identical; the one-line diff is
the generated tag list alone. No ruling text was authored or edited, so the index's ruling-length
budget is unaffected.

```
$ env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/check-decision-anchors.py
examined 34 anchor(s), 0 failed
EXIT_ANCHORS=0

$ env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/check-instruction-paths.py
scanned 62 file(s), 0 violation(s)
EXIT_PATHS=0
```

**On the pre-existing `check-instruction-paths.py` failure** reported in run
`2026-09-08-t07-product`: it does not reproduce here. The script exits 0 with zero violations at
this tree state, so there is no failure to attribute — neither mine nor the earlier one. I report
what I measured rather than confirming a red I never saw.

## `git status --porcelain`

```
 M .claude/skills/harness/bin/factory_config.py
 M .harness/harness/docs/DECISIONS-INDEX.md
 M .harness/harness/docs/DECISIONS.md
 M .harness/harness/docs/SPEC.md
 M README.md
 M tests/unit/test-fleet-product-config.py
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/review-harness-code-reviewer-c0.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/review-harness-qa-c0.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/review-harness-security-reviewer-c0.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/review-harness-ui-reviewer-c0.md
```

- **Mine (4):** `DECISIONS.md`, `DECISIONS-INDEX.md`, `SPEC.md`, `README.md`. This receipt is a
  fifth, written after the snapshot above.
- **NOT mine, LEFT ALONE:** `.claude/skills/harness/bin/factory_config.py` and
  `tests/unit/test-fleet-product-config.py` are the concurrent sibling engineering segment's work
  (V-2, V-7, V-8). I never opened either for editing.
- `.claude/skills/harness-init/SKILL.md` does **not** appear — the MAIN SESSION's edit was unsaved
  at snapshot time. Either way it is not mine; I did not open it, and V-5's matching
  `harness-init` clause remains the main session's to write.
- The four `??` reviewer notes are the review panel's, pre-existing at my spawn.
- Confirmed my own footprint independently: `git diff -U0` over my four files shows exactly four
  hunks (`DECISIONS-INDEX.md@220`, `DECISIONS.md@6992` + `@7006`, `SPEC.md@145`, `README.md@192`).

**Nothing committed.** No test suite, formatter or project-wide gate sweep was run.

## Stale found — not fixed, out of scope

`.harness/harness/docs/SPEC.md:448-450` cites `.claude/skills/harness/bin/harness_boundary.py:158`
as the site where `check-domain.sh` "fails CLOSED" on a bad fleet entry. **That anchor is wrong.**
`harness_boundary.py:151-169` is `linked_worktrees`, and `:158` is its docstring's
"NO GIT SUBPROCESS: DEC-193 forbids one…" line. Grepping the module and `check-domain.sh` for
`fails closed`/`FleetError` returns nothing; the deny path is `classify`'s
`{"outcome": "deny", …}` at `harness_boundary.py:711`. The claim is true; only the pointer rotted.
Not fixed here: the dispatch scoped me to row 145 of §2.2 and told me not to restructure other
SPEC prose, and re-anchoring a §-later paragraph is a separate one-line change. Flagged, per
"fix it or flag it".

## Not done, by instruction

- `.claude/skills/harness-init/SKILL.md` — V-5's operator-facing half and V-6 entirely.
  MAIN-SESSION-owned; read-only for me and not read at all.
- V-2, V-7, V-8 — sibling engineering segment.

---

# Addendum — fix-anchor pass — 2026-09-08

**The stale citation flagged above is now fixed.** One line changed in
`.harness/harness/docs/SPEC.md`; nothing else. The four findings closed in the first pass are
untouched — the sections above are the record of those and remain accurate as written.

## The change — one line

The citation sits on **`.harness/harness/docs/SPEC.md:450`**, not `:451` as the dispatch stated;
`:451` is the following line (`clones it under \`workspace_root\`; …`). I edited the line the text is
actually on.

BEFORE — `.harness/harness/docs/SPEC.md:450`:

```
(`.claude/skills/harness/bin/harness_boundary.py:158`). The first factory run against it
```

AFTER — `.harness/harness/docs/SPEC.md:450`:

```
(`.claude/skills/harness/bin/harness_boundary.py:711`). The first factory run against it
```

The prose it supports — "because `check-domain.sh` then fails CLOSED the symptom is not a failed
onboarding but every agent write in this repository BLOCKED" — is TRUE and is unchanged. This is a
pointer repair, not a prose edit.

## The anchor, measured at this tree state

Grep of `"outcome": "deny"` over `.claude/skills/harness/bin/harness_boundary.py`, one hit:

```
 710:
*711:    return {"outcome": "deny", "rel": rel, "base": base,
 712:            "advertise": _advertise, "shared_advertise": _shared_advertise}
```

`711` still holds. `harness_boundary.py` is not in `git status` (unmodified in this worktree), so
this is committed state and no sibling has shifted it.

## Gates — all three exit 0

Run from the worktree root with `env -u HARNESS_AGENT_TYPE`:

```
=== gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md ===
exit=0
=== check-decision-anchors.py ===
examined 34 anchor(s), 0 failed
exit=0
=== check-instruction-paths.py ===
scanned 62 file(s), 0 violation(s)
exit=0
```

The index diff **emitted zero bytes** — emptiness is the pass condition here, and it confirms this
SPEC edit did not move `DECISIONS-INDEX.md`. Nothing was regenerated.

## `git status --porcelain`

```
 M .claude/skills/harness/bin/factory_config.py
 M .harness/harness/docs/DECISIONS-INDEX.md
 M .harness/harness/docs/DECISIONS.md
 M .harness/harness/docs/SPEC.md
 M .harness/harness/features/FEAT-56-central-onboarding-model/observations/harness-documentor.md
 M README.md
 M tests/unit/test-fleet-product-config.py
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-documentor-fix-docs-product.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/review-harness-code-reviewer-c0.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/review-harness-qa-c0.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/review-harness-security-reviewer-c0.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/review-harness-ui-reviewer-c0.md
```

- **Mine, five across both passes:** `SPEC.md`, `DECISIONS.md`, `DECISIONS-INDEX.md`, `README.md`,
  and this receipt (`??`, created in the first pass, appended to here).
- **Also mine, incidental:** my own `observations/harness-documentor.md`.
- **Not mine — sibling engineering segment:** `factory_config.py`,
  `tests/unit/test-fleet-product-config.py`. Not opened.
- **Not mine — review panel, pre-existing at my spawn:** the four `??` `review-*.md` notes.
- `.claude/skills/harness-init/SKILL.md` still does not appear; it is MAIN-SESSION-owned and I did
  not open it in either pass.

## Footprint — `git diff -U0 -- .harness/harness/docs/SPEC.md`

Exactly two hunks, as expected:

```
@@ -145 +145 @@ Run at every `/harness` entry. The real state is a matrix, not a binary:
-| not registered in `.harness/factory/fleet.yaml`, or its own `harness.json` not readable at its `default_branch` | the repository is not onboarded — have the user run `/harness-init` |
+| not registered in `.harness/factory/fleet.yaml`, or its own `harness.json` not readable at its `default_branch`, or no central tree at `<control-plane>/.harness/<segment>/` | the repository is not onboarded — have the user run `/harness-init` |
@@ -450 +450 @@ the symptom is not a failed onboarding but every agent write in this repository
-(`.claude/skills/harness/bin/harness_boundary.py:158`). The first factory run against it
+(`.claude/skills/harness/bin/harness_boundary.py:711`). The first factory run against it
```

`@145` is the V-1 row from the first pass; `@450` is this pass. No third hunk.

**Nothing committed.** No test suite, formatter or project-wide gate sweep was run.
