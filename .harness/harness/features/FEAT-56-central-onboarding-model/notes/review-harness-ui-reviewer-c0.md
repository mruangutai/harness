# UI review — FEAT-56 central onboarding model — cycle 0

Pin: `6f34e289` (= `6f34e2899b6b165585e6ceb95d78e0d836b43c36`, resolves cleanly).

## Job 1 — rendered/operator surfaces: no regression, two advisory findings

### `org.html` — scoped-out with measured evidence, no regression

`git diff 4b5dbb23..6f34e289 -- .harness/harness/docs/org.html` is exactly **one line**
(`org.html:286`): the `team-config.yaml` owner cell changes from `/harness-init` to
`/harness-init · control plane only`.

What I opened to conclude "no regression":
- `git show 6f34e289:.harness/harness/docs/org.html` full file (348 lines) — markup around the
  edited `<tr>` is well-formed, same `class="owner o-you"`, no new class/tag/attribute.
- Grep for `products/|deploy\.sh|per-product|scaffold|team-config\.yaml` across the whole file:
  the only other `team-config.yaml` mentions (lines 307, 345) are unrelated prose, not scaffold
  references. No orphaned reference to the deleted per-product install anywhere in the page.
- CSS variable trace: `.o-you{color:var(--ink)}` (`org.html:125`), `--ink` is defined in the
  unprefixed `:root`, the `@media (prefers-color-scheme:dark)` block, and both
  `:root[data-theme="dark"]`/`:root[data-theme="light"]` blocks (`org.html:2-27`) — the edited
  cell inherits an existing, already-theme-safe token; no new color, no new contrast surface.
- `·` (middle dot) as a plain-text separator is an established convention already in the same
  table (`each view's author · skeleton documentor`, unlabelled `<span>`) — the edit matches it,
  no inconsistent styling introduced.

**Conclusion: no UI regression.** The edit is correctness-improving (it removes the false
impression that `/harness-init` writes `team-config.yaml` into every onboarded product) and
touches nothing else. Note for completeness: `org.html`'s *entire* onboarding-relevant content is
this one cell — it is an ownership map, not a procedure description, so it cannot state "fleet
registration" or "central tree" the way `README.md` does; that is the page's job, not a gap.

### CLI operator output — `factory_config.py --check-product-configs` — one advisory finding

**FIND — duplicated identifier/phrase in the stderr failure line.**
File: `.claude/skills/harness/bin/factory_config.py`. Task: **T-04**. Lane: **squad-writable**
(`.claude/skills/harness/bin/**` → team, harness-backend-dev | harness-dev-ops). Severity: **low**.

`_check_product_configs` (`factory_config.py:470-473`) calls
`factory_cli.fail("config", "product config unreachable", f'{m["repo"]}@{m["ref"]}:{m["path"]}', m["detail"])`
where `m["detail"]` is `str(FleetError)`, and `FleetError.__str__` is already
`factory_cli.body(what, value, next_step)` (`factory_config.py:62-69`) — i.e. the detail string
already contains the full `{repo}@{ref}:{path}` triple once, wrapped in its own
`"product config unreadable: ... — ..."` prefix. `fail()` wraps that same triple and a
near-duplicate phrase a second time. Reproduced by direct execution against a temp fleet with an
unresolvable repo (`python3 factory_config.py --fleet <tmp> --check-product-configs`), actual
stderr byte-for-byte:

```
factory: config: product config unreachable: nonexistent-owner-zzz/nonexistent-repo-zzz@main:.harness/harness.json — product config unreadable: nonexistent-owner-zzz/nonexistent-repo-zzz@main:.harness/harness.json — could not read nonexistent-owner-zzz/nonexistent-repo-zzz's .harness/harness.json at main: gh api contents failed: ...
```

Concrete scenario: an operator running `--check-product-configs` against a fleet with several
unreachable members gets one stderr line per member, each restating the same `repo@ref:path`
identifier twice back-to-back with two near-synonymous phrases ("unreachable" / "unreadable"),
making a log with multiple failures noticeably harder to scan. Not blocking — the information is
correct, just redundant — so this does not gate. `stdout`'s JSON payload (`members[].detail`) has
the same redundancy but is machine-read, not scanned, so it is lower-impact there.

## Job 2 — SC-04, my seven files, one citation each

| # | File | `file:line` (at `6f34e289`) | Grade |
|---|---|---|---|
| 1 | `.harness/harness/docs/org.html` | `:286` — `/harness-init · control plane only` | **met** |
| 2 | `README.md` | `:192` — "`/harness-init` registers the repository in `.harness/factory/fleet.yaml`, creates its central tree under `<control-plane>/.harness/<segment>/`, and lands its `harness.json` on its own default branch, which is the only file the harness puts in a product repository" | **met** |
| 3 | `.harness/README.md` | `:83` — "A repository is not onboarded when it is absent from `.harness/factory/fleet.yaml`, when its own `harness.json` is not readable at its default branch, or when it has no central tree" | **met** |
| 4 | `.claude/skills/harness/templates/README.md` | `:4` — "Exactly one instantiated file lands in a product repository — that repository's own harness.json, on its default branch — and everything else is instantiated in the control plane" | **met** |
| 5 | `.claude/commands/harness.md` | `:12` — "anything spawns — except when this clone has no `.harness/` at all, the repository is not in [`.harness/factory/fleet.yaml`...]" | **met** |
| 6 | `.claude/commands/harness-plan.md` | `:19` — "Gate check in step 0 above, including registration in `.harness/factory/fleet.yaml`" | **met** |
| 7 | `.claude/commands/harness-grilling.md` | `:5` — "the repository's own `harness.json` — which must land on its default branch —" | **met** |

Routing-specific check for the three `.claude/commands/**` files (a model following them routes to
the central model, not the retired scaffold):
- `harness.md` Gate (`:11-17`): the four disjunctive onboarding-needed conditions are all
  central-model conditions (no `.harness/` at all / not in fleet.yaml / `harness.json` unreadable
  at default branch / central tree absent), and it explicitly carves out the non-onboarding case
  ("a registered fleet member with an empty features/ ... routes to `/harness-plan`, not
  onboarding") — a model cannot mis-route an already-onboarded-but-featureless member into
  `/harness-init`.
- `harness-plan.md` (`:18-19`): no longer re-derives its own condition list (which is exactly the
  drift the simplify pass already fixed here, see below) — it defers to `harness.md`'s Gate and
  adds only the fleet.yaml example. A model following it lands on the same routing decision as
  `harness.md`, by construction.
- `harness-grilling.md` (`:4-6`): not itself a routing predicate (it fires only once already
  inside onboarding), but its destination claim is now scaffold-free: the repository's own
  `harness.json` on its own default branch, and (for the control plane only) `team-config.yaml`
  and `.harness/glossary.md` — no product-side `team-config.yaml` copy is implied.

**My quarter of SC-04: 7/7 met.**

## Job 3 — the "second drift instance" lead: confirmed, one real second instance found

The lead's premise checks out. The *first* instance — `harness.md`'s Gate testing two conditions
while `harness-plan.md`'s Target-state bullet independently re-derived three, already out of sync
— is recorded in `notes/receipt-harness-ai-dev-simplify-altitude.md:22-38` and is **fixed** at this
pin: `harness-plan.md:18-19` now defers to `harness.md`'s Gate instead of restating the list
(confirmed above).

**A second, different-shaped instance exists, within my seven files, not yet flagged by anyone:**
`README.md` states the three-part model in the *wrong order* relative to the decision it cites in
the same sentence.

- `README.md:192` (as an action sequence, i.e. what `/harness-init` *does*, in order): **registers
  in `fleet.yaml`, THEN creates the central tree, THEN lands `harness.json`** — cites `(DEC-220)`.
- `.harness/harness/docs/DECISIONS.md:6987-6992` (DEC-220 itself, the cited authority): **"its own
  `.harness/harness.json` landed on its default branch, its entry in
  `.harness/factory/fleet.yaml`, and its central per-segment tree"** — i.e. config lands FIRST,
  registration SECOND — and states explicitly why: *"The three are ordered: registration comes
  **after** the config lands, because the failure of the reverse order has no symptom but an
  unattributed `FleetError`."*

`README.md`'s stated order is the exact reverse of the order its own cited decision mandates, for
the exact reason the decision calls out. Concrete scenario: an operator whose only reference is the
README (rather than the full `harness-init` procedure) registers the repository in `fleet.yaml`
first, as the sentence's first clause tells them to, before that repository's `harness.json` has
landed — reproducing precisely the race `DEC-220` exists to close, whose only symptom is an
unattributed `FleetError` the next time `factory_config.product_config` is called for that member.

File: `README.md`. Task: **T-07**. Lane: **squad-writable** (`README.md` → team,
harness-documentor). Severity: **low** — not gating. Reasons it stays low rather than med: (1) this
is background/overview prose, not the executable procedure — `harness-init/SKILL.md`, the file
that is actually followed step-by-step, has the correct order and is verified by SC-01's own
`grep -n` line-number ordering check (`DB < FL < SG`); (2) the safety net the decision itself
names, `factory_config --check-product-configs`, still catches any member that slipped through in
the wrong order before a build reaches it. It is a real documentation-consistency defect, not a
functional regression, and is reported as such rather than upgraded to force a gate.

Checked and found NOT to be a second instance of the *same* (independent-restatement,
count-drifted) shape: `.harness/README.md:83-84` and `harness.md:12-14` also each restate the
three-part model independently, but both phrase it as a **disjunction of failure conditions**
("not onboarded when A, or B, or C"), where element order carries no operational meaning (all
three are checked, none is a step to perform in sequence) — so their differing internal orderings
are not the same defect as `README.md`'s ordered-action-sequence contradiction. Recorded here as
assessed-and-dismissed with reason, not silently dropped.

## Findings summary

| Severity | File | Task | Lane | Gates? |
|---|---|---|---|---|
| low | `.claude/skills/harness/bin/factory_config.py` | T-04 | squad-writable | no |
| low | `README.md` (vs `DECISIONS.md`) | T-07 | squad-writable | no |

No `high`/`critical` findings. `severity_max: low`. Nothing in `must_fix`.
