> **RETIRED, NEVER SIGNED — 2026-08-14. Read this for its RESEARCH, never for its scope.**
>
> This brief was planned, reviewed through three engineering passes, and never approved. Its scope
> was superseded before signature by wayfinding map **#336**, which took the same effort from "one
> repository can be configured centrally" to "the harness becomes multi-repository". Its 17 success
> criteria were written for the narrower scope and do not describe anything that will be built.
>
> **Four of its six decisions are dead:** D-01 (superseded — A-08 gives harness a fleet entry and
> #346 gives it a segment), D-02 (**falsified** — #351 measured `cwd` as the harness root for every
> agent, so position-derivation answers the wrong question and `agent_id` is the real channel),
> D-04 (**reversed** by #350 — a product's board moves into `harness.json`), D-06 (flipped to
> option B).
>
> **Two survive and were carried onto map #336:** D-03 (kaya's test kinds ship `unresolved` and
> DEC-187 closure is enforced at the first factory run) and D-07 (the resolver's flag is
> `--which-config`, because a second `--resolve` answering a different question in a different shape
> is a homonym).
>
> **What the five spent cycles actually bought was research, not a plan** — anchors re-derived at
> HEAD, and an engineering review that caught `load_fleet()` being called with no argument while
> `FLEET_PATH` binds at import, which would have made every fixture test pass for the wrong reason.
> **That finding applies to any new caller and must not be lost.**

# BRIEF — FEAT-19 Central product config

**Anchored at `63b83c7`, branch `main`** — every fact, count and routing verdict below was
re-derived at that commit. The grilling artifact's anchors were re-derived at `862d270` and had
already moved; one clause of its own refresh is false at HEAD (see
`notes/research-FEAT-19-anchors-and-mechanism.md`). Nothing in this brief inherits a line number.

**Revision 2**, after an architecture review returned FAIL on the plan's specification of D-02 (the
choice itself was confirmed sound) and a design review returned PASS with contract corrections.
**Three** rulings are new — D-06, D-07 and D-08, the last recorded here as D-02's sub-choice;
D-04's `station_field` justification and the `## Constraints` NOBODY clause were **false about the
code at `63b83c7`** and are corrected in place, with what was false named rather than quietly
replaced.

Implements issue #206 and the grilling decision record
`.harness/notes/grilling-central-product-config-2026-08-12.md`.

## Problem

The factory can be pointed at another repository but cannot be told anything about it. A worker
session standing in `harness-factories/kaya-ai` has no `.harness/` beneath it, so every config
question — which tests this change owes, which repo to sync issues to, which board to move cards
on — resolves against the harness repository's own `harness.json`. The answers it gets are
harness's answers. `mruangutai/kaya-ai` has been registered in `fleet.yaml` since FEAT-16 and is
still, at `63b83c7`, a repository the factory can check out and cannot describe.

The cost is not an error message. It is a **silent wrong answer**: harness's `test_matrix`
applied to kaya's code would demand `unit` and `integration` from runners that do not exist in
kaya's tree, and harness's `github.repo` would send kaya's issue mirror to `mruangutai/harness`.
Nothing today makes either loud.

The operator's rule, ruled 2026-08-13 during FEAT-18's signature and recorded in the grilling
artifact: **`harness.json` holds harness RUNTIME metadata; project, repo and GitHub data belongs
with the product, and the redundancy between `harness.json` and `fleet.yaml` today is the defect.**

## Goal

A repository registered in `.harness/factory/fleet.yaml` can also be **configured** centrally, by
a file in the harness repository, and a session working on that repository resolves its config
from there rather than from harness's own. Reaching the end looks like: point the factory at
`mruangutai/kaya-ai`, and **the test matrix the qa gate applies is kaya's, not harness's**.

**The Goal is scoped to one consumer on purpose, and this is D-06's ruling.** Two things in the
tree read config by joining `.harness/harness.json` by hand at `63b83c7`: the qa gate
(`.claude/skills/harness-qa-gate/SKILL.md:45`, prose telling qa where to read `test_matrix` and
`test_kinds`) and `gh-sync.py` (`.claude/skills/harness/bin/gh-sync.py:122`, which joins the same
path for `github.repo` and the board). This effort rewires **the qa gate only**. Issue mirroring
and board writes for a product keep resolving against harness's `harness.json` until a later
effort; that is stated here rather than implied, because a Goal no task reaches is the defect that
sent the first draft back. Nothing else about onboarding moves in this effort.

## Requirements

- REQ-01: A registered repository can carry a central config in the harness repository, addressed
  by a path derived from its fleet entry.
- REQ-02: A session working inside a registered repository's checkout resolves its config from
  that repository's central config, not from the harness repository's own. **Scope of "its
  config" under D-06: the `test_matrix` and `test_kinds` a qa gate applies. The `github` block a
  session syncs issues with is explicitly NOT in this requirement** — `gh-sync.py` keeps joining
  `.harness/harness.json` and the rewiring of it is a named follow-on, not an omission.
- REQ-03: A session working in the harness repository itself resolves the harness repository's own
  config, exactly as it does today.
- REQ-04: A resolution that cannot be completed refuses loudly and never falls back to another
  repository's config.
- REQ-05: `mruangutai/kaya-ai` has a real central config in this repository — not a fixture, not a
  template example.
- REQ-06: The onboarding skill describes what the factory actually does: registration is its first
  step, and it no longer instructs a reader to install prerequisites into a product, scaffold a
  product `.harness/`, or restart a product session.
- REQ-07: The layout record for `.harness/` names the new product location and who writes it.
- REQ-08: The qa gate takes the `test_matrix` and `test_kinds` it applies from the config that
  resolves for the session under test, rather than from a path it joins by hand.
- REQ-09: No file in the harness repository asserts a placement this feature's ruling
  contradicts. (`.harness/harness.json` asserts at `63b83c7` that `github`, `test_matrix` and
  `test_kinds` are moving to the product; D-01 option A rules they stay.)

## Decisions for the operator, priced — rule these at signature

These are named here rather than resolved, on the grilling artifact's instruction. Each is priced
in tasks so the cost of a branch is visible before you sign. **The plan as written implements the
default named in each; choosing otherwise re-plans the listed tasks and resets approval.**

### D-01 — The fleet-entry paradox: where does harness's OWN project data live?

The rule says project/repo/GitHub data belongs with the product, which would move harness's
`github` block (and `test_matrix`, `test_kinds`) out of `harness.json`. But the only "with the
product" location for harness is a `fleet.yaml` entry, and `mruangutai/harness` is **deliberately
absent** from `repos:` — the absence is the mechanism. Measured both ways and recorded in
`fleet.yaml` itself: with the entry present, `--resolve` on a harness checkout under the factory
workspace returned NOBODY; with it absent, it exits 2. **Louder, not quieter.** So satisfying the
rule for harness requires making a guard quieter.

One nuance narrows it: that measurement was on a checkout **inside** `workspace_root`. The live
checkout at `~/GitHub/harness` is unaffected either way. The entry would only change what happens
when the factory builds harness itself.

| Option | Cost | Effect on the guard |
|---|---|---|
| **A — harness is the one repo whose project data legitimately stays local** (DEFAULT, planned) | 0 extra tasks. `harness.json` keeps `github`, `test_matrix`, `test_kinds`; the asymmetry is written down as the rule rather than an exception | unchanged; the absence keeps exiting 2 |
| B — give harness a `fleet.yaml` entry and move its project data there | reverses DEC-174 am.1; adds a migration task, a fleet-schema task, and a re-measurement of `--resolve` on a workspace checkout | **weakened** — exit 2 becomes NOBODY for a harness checkout under the workspace |
| C — a third config location, neither `harness.json` nor `fleet.yaml` | adds a location, a reader and a precedence rule to every consumer | unchanged, but the number of places config can live goes from two to three |

**Why A is the default:** it is the only option that adds zero tasks and keeps the guard loud, and
the asymmetry it records is the same one `fleet.yaml` already carries for `stations:` — a product
board is foreign and may name anything, harness's board is prescribed. Its cost, stated plainly:
the operator's rule then has a permanent named exception, and `harness.json` keeps holding data
the rule calls project data.

### D-02 — How a worker session finds its product's config

The load-bearing design choice, and the one an eng-lead architecture review runs on after this
plan. Stated as a proposal with alternatives rather than silently fixed.

**Proposed (planned): position-derived.** The session's root is matched against
`workspace_root/<segment>` using the fleet map that `harness_boundary.resolve_fleet` and
`factory_config.workspace_path` already compute; the matched entry's repo segment addresses
`<harness root>/.harness/products/<segment>/harness.json`.

Its merit is that the derivation already exists and is already trusted: the same map decides which
domain base a write resolves against. Adding a second key would mean two things could disagree
about which product a path belongs to, and the guard's answer and the config's answer diverging is
the worst failure mode available here. Its cost: a session outside both the harness root and
`workspace_root` cannot resolve — which is a refusal, and by REQ-04 a loud one.

| Alternative | Price |
|---|---|
| An explicit `config:` pointer on each fleet entry | visible in the file you edit; a second thing to keep in sync with the directory, and nothing would check it |
| An env var (`HARNESS_PRODUCT`) | works from anywhere; an override that can silently point a session at the wrong product's matrix |
| A marker file in the product checkout | contradicts the principle that repos carry almost nothing of the harness |

**D-02 sub-choice — recorded as `D-08` in the plan — and this one is genuinely open: is the
containment rule SHARED or COPIED?**
The architecture review found that the guard's containment rule is not just "a prefix" — it is
`commonpath` with **longest match wins**, so a product checked out beneath another's path
resolves against its own base rather than its parent's (`harness_boundary.select_base`, the
`max(..., key=len)` over matching bases, re-derived at `63b83c7`). The first draft said only "a
prefix of session_root", which would have made the guard and the config disagree about a nested
checkout — defeating the merit D-02 is chosen for.

| Option | Cost |
|---|---|
| **A — COPY the rule: the resolver states longest-match-wins explicitly, and the divergence is recorded as accepted** (DEFAULT, planned) | 0 extra tasks. Two implementations of one rule; a future change to the guard's containment must still be mirrored by hand. The mirror is no longer unchecked: T-01's test file imports `select_base` read-only and asserts both implementations pick the same base on the nested-checkout fixture, so a divergence on that shape reddens the unit suite. One fixture, not general agreement. Recorded as an accepted divergence in the decision entry, DEC-193 am.1 style |
| B — SHARE the rule: lift `select_base`'s `inside` closure to module scope in `harness_boundary.py` and import it from the resolver | one implementation, permanently. But it **changes `harness_boundary.py`**, which both write guards import and which DEC-193 names as the one shared rule, and the review's own open question asks whether that file is inside DEC-174's carve-out *in substance* even though it is not on the literal list of four. That question is unresolved |

**Why A is the default, stated so you can overrule it:** acquiring an unresolved carve-out
question mid-feature is a worse trade than one recorded divergence. A divergence is written down
and findable; a carve-out question stops the build. If you disagree, taking B at signature costs
T-01's `intent:` an import instead of a restatement, one edit to `harness_boundary.py`, and a
ruling from you on whether that edit is `main-session-direct` under DEC-174.

### D-03 — What test-matrix closure means for a config authored on a product nobody has run

DEC-187 sets a closure invariant: every kind the matrix names must be `active` — a `cmd` someone
has **run and seen pass** — or `excluded` with a `signed` value naming a decision that resolves in
**the project's decisions file**. `unresolved` blocks.

Neither is available for kaya. Nobody has run kaya's commands from here and this effort does not
clone kaya, so `active` would be an unverified claim of exactly the shape DEC-187 exists to stop;
and kaya has no decisions file, so `excluded` has nowhere to sign. The existing reference
`.claude/skills/harness/templates/examples/harness.kaya-ai.json` carries the defect DEC-187 names
by name — `bugfix.always` is `["__bug_class__"]`, a predicate placeholder in no `test_kinds`, so
kaya's bugfix type can never resolve — so it cannot be copied forward unchanged.

| Option | Cost |
|---|---|
| **A — kaya's kinds ship `unresolved`, and closure is enforced at first factory run** (DEFAULT, planned) | honest, and REQ-05 is still met — a real config exists and resolves. A qa gate on kaya blocks until someone runs the commands, which is DEC-187 working as designed rather than a defect |
| B — the operator signs statuses at approval | a config that claims verified runners nobody ran; the exact claim DEC-187 forbids |
| C — coin a per-product decisions location so `excluded` can sign | closes the invariant properly, and is a second feature: a decisions file, an index, and a resolver for `signed` |

**Regardless of the option chosen, `bugfix.always` is corrected** — the placeholder is moved to a
`when` clause or dropped, and `unit` is restored, because a matrix whose type can never resolve is
broken under every option.

### D-04 — The three board keys, ruled PER KEY

The grilling artifact is explicit that a single ruling on all three will be wrong about at least
one. Each carries its own recommendation.

| Key | Recommendation | Why |
|---|---|---|
| `number` | **KEEP, and it is required.** | Nothing else in the tree identifies a board. Not derivable from anything |
| `owner` | **KEEP, and this reverses the artifact's lean.** | The artifact calls it redundant because `github.repo`'s first segment gives it. That derivation is true of harness today and **false in general** — `fleet.yaml`'s kaya entry already carries `board.owner` explicitly, and a config that derives owner for one repo and reads it for another has two rules for one field. Deriving it also means a board owned by a different account than its repo fails by silently querying the wrong owner, rather than by being unstated. The cost of keeping it — one line restating data two lines above — is smaller than the cost of two rules |
| `station_field` | **KEEP and REQUIRED — but the ruling CONFIRMS the code rather than changing it.** | The first draft said this made something required that was optional. That was **false at `63b83c7`**, and it is corrected here rather than left standing. `factory_config._validate_board` **already** raises `FleetError` on a missing or empty `station_field`, and kaya's `fleet.yaml` entry already carries `station_field: Status`. So for a **product** board, nothing is added — the ruling records why the existing enforcement is right, so a future reader does not relax it: DEC-192 prescribes the six station *values* byte for byte and nothing prescribes the *field name* holding them, `Status` is GitHub's renameable default, and a pinned field name is a string that goes stale silently. **The silence the first draft described is real but lives elsewhere:** on *harness's own* board, `gh_board.load_board` returns `None` when `station_field` is missing or empty — not configured, not an error — so station writes are silently skipped. **No task in this plan changes that**, and that is a named residual of this feature, not a claim it fixes. |

**Where each board block lives, so these rulings do not create the redundancy they are meant to
end.** A **product's** board stays in its `fleet.yaml` entry, where FEAT-16 put it and where
`factory_config._validate_board` already enforces it — a product config file carries no board at
all, because one board declared in two files with nothing checking their agreement is exactly the
defect this feature removes. **Harness's own** board stays in `harness.json` under D-01 option A.
The three rulings above describe the required shape in both places.

### D-06 — Does anything CALL the resolver in this effort?

**The first draft's most serious defect, and the reason it came back.** The plan built the
resolver and rewired nothing. At `63b83c7` two places read config by joining
`.harness/harness.json` by hand: `.claude/skills/harness-qa-gate/SKILL.md:45` ("Read `test_matrix`
and `test_kinds` from `.harness/harness.json`") and `.claude/skills/harness/bin/gh-sync.py:122`
(`os.path.join(root, ".harness", "harness.json")` for `github.repo` and the board). With neither
rewired, the mechanism has no consumer, the Goal's own sentence is not reached by any task, and
the resolver could be deleted at ship with only its own tests noticing.

| Option | Cost | Does the Goal's sentence come true? |
|---|---|---|
| **A — rewire the qa gate only** (DEFAULT, planned) | 1 task, prose. The file is granted to NOBODY, so it is a declared main-session step | **Yes, for the test matrix.** Not for issue sync — stated in the Goal and in REQ-02 rather than left implied |
| B — rewire both | A's task plus a code task on `gh-sync.py` and its tests. `gh-sync.py` takes `root` from each caller and joins config from it; making it resolve instead changes what `root` means at every call site, which has to be re-derived per site. That is a code change with its own review surface | Yes, fully |
| C — rewire nothing; narrow the Goal and REQ-02 to "the mechanism exists and is observable" | 0 tasks. The feature ships a resolver nobody calls, and the next effort inherits both the wiring and the argument about whether it was in scope | **No.** The Goal is narrowed to match |

**Why A is the default:** the qa gate is the consumer the Goal actually names — "the test matrix
that applies is kaya's" is a sentence about the qa gate and nothing else — and it is prose, so the
change costs one task and carries no code-review surface. B is right eventually and is priced
above so you can take it now; C is honest but ships a mechanism with no caller, which is the state
the review flagged.

### D-07 — The resolver's flag is `--which-config`, not `--resolve`

`check-domain.sh --resolve <path>` already exists and answers a **different** question in a
**different** shape: which agent owns a path, as plain text including the literal `NOBODY`,
re-derived by running it at `63b83c7`. A second `--resolve` answering "which config file applies",
as JSON, on an adjacent tool is a homonym — and it is not hypothetical: D-01's own prose above
argues about a harness checkout returning `NOBODY` versus exiting 2 inside a paragraph about
config resolution, which is the two questions already blurring in this document.

**Ruled: the new flag is `--which-config`.** This is a `D-NN` rather than a digest note because it
is hard to reverse once documentation and a UAT step name it, and because the alternative — keep
`--resolve` and rely on always naming the tool with the flag — is a real trade-off with a
convention on its side. Everything that names it is still `pending`, which makes now the only
cheap moment. Every place that names it also names the tool with it: never a bare flag.

## Explicitly out of scope

- Re-homing the interview, `dev-ops` detection, domain seeding, the BRIEF and the codebase map.
  In scope for the central model as a whole; out by this effort's destination.
- **Whether `harness-init --upgrade` applies to a product config.** Nothing else about onboarding
  moves; `upgrade-config.py` is untouched and keeps merging this repository's own `harness.json`.
  Named cost: a product config has no upgrade path and will drift from the template.
- **Whether a product's domain globs are part of "configured".** `team-config.yaml` lives solely
  in harness (operator ruling, 2026-08-09) and this effort does not describe a product's paths.
- Deleting `templates/`. #203 closed without removing it and nothing here depends on its fate.
- Cloning, running or testing kaya's own code.

## Success Criteria

- SC-01: A session rooted in a registered repository's checkout resolves that repository's
  central config, and the `test_matrix` it gets is the one in `.harness/products/<segment>/`, not
  the one in `.harness/harness.json`.
  verify: automated      evidence: unit
- SC-02: A session rooted in the harness repository resolves `.harness/harness.json`, byte for
  byte the same result as before this feature.
  verify: automated      evidence: unit
- SC-03: A checkout under `workspace_root` that is **registered in `fleet.yaml` but has no
  product config** refuses loudly and never returns harness's config.
  verify: automated      evidence: unit
- SC-04: A product config directory with **no matching `fleet.yaml` entry** is never reachable —
  resolution is keyed on registration, so an orphaned directory cannot be resolved into.
  verify: automated      evidence: unit
- SC-05: A checkout under `workspace_root` belonging to no registered repository still exits 2,
  unchanged by this feature.
  verify: automated      evidence: unit
- SC-06: `mruangutai/kaya-ai` has a config at the derived path that loads, and every change type
  in its `test_matrix` names only kinds that exist in its own `test_kinds` — in particular
  `bugfix` no longer names `__bug_class__` in `always`.
  verify: automated      evidence: unit
  (The evidence is a case in `test-factory-product-config.py` reading the **live** config file, not the
  one-shot command on the task that writes it: a task command dies with the task and leaves
  nothing to cite at goal-check.)
- SC-07: `harness-init`'s skill no longer instructs a reader to install prerequisites into a
  product, scaffold a product `.harness/`, or restart after init, and its first step is fleet
  registration.
  verify: inspection
- SC-08: The six surviving steps of `harness-init` are unchanged in wording — the hybrid is the
  signed outcome, so a partial rewrite of those steps would be scope creep, not tidying.
  verify: inspection
  (Deliberately **not** `automated`: no `unit` glob matches a `SKILL.md`, and the task's
  `change_type: docs` obligates no tests, so an `automated` mark here would rest on a runner that
  never sees the file. The evidence is T-03's `verify` output, read by the reviewer.)
- SC-09: `.harness/README.md` names `products/` with its writer, so the layout record does not
  omit a directory the factory depends on.
  verify: inspection
- SC-10: No invariant fires on the presence of `.harness/products/`, and `check-state.sh` passes
  on this repository after the change.
  verify: automated      evidence: integration
  (The `integration` evidence is `test-check-state.py`, which runs against fixture trees. A pass
  on **this** repository is the pre-commit `check-state.sh` run and is cited separately.)
- SC-11: The new resolver is registered in `run-unit-tests.sh`'s script arrays, so its tests
  actually run rather than existing unread.
  verify: automated      evidence: unit
- SC-12: The operator can point the factory at kaya and see, in one command's output, which
  config file answered — the resolution is observable, not inferred from behaviour. **On both
  branches**: on success the config path is a key of the one JSON line, and on a refusal — where
  stdout is empty by `factory_cli.run`'s contract — the config path or repository name the
  operator can act on is carried in the stderr line's `value` slot. `--which-config .` from
  inside the checkout is the gesture; an absolute path is not required.
  verify: uat
- SC-13: A session rooted in neither the harness checkout nor the factory workspace refuses, and
  does not silently answer with the harness repository's config. **Including the case where
  `fleet.yaml` is absent**, which the first draft's algorithm answered `harness` for.
  verify: automated      evidence: unit
- SC-14: A fixture-rooted test's answer does not depend on this repository's own
  `.harness/factory/fleet.yaml` — proven by a fixture whose fleet declares a repository name
  present in no live fleet entry, whose expected resolution is reachable only from the fixture.
  (Guards the import-time `FLEET_PATH` trap: `factory_config.FLEET_PATH` is computed at import
  from that module's own root probe, so a default-argument `load_fleet()` reads the live
  repository while the test believes it read the fixture, and every case passes for the wrong
  reason.)
  verify: automated      evidence: unit
- SC-15: The qa gate takes its `test_matrix` and `test_kinds` from the resolver rather than from a
  path it joins by hand, and says what happens when resolution refuses.
  verify: inspection
- SC-16: No file in this repository asserts that `github`, `test_matrix` and `test_kinds` are
  moving to the product, and `.harness/harness.json`'s board note still explains why the board's
  three keys are resolved by name.
  verify: inspection
  (Deliberately not `automated`: no test kind's runner reads `.harness/harness.json`'s prose. The
  evidence is T-06's `verify` output — which asserts the absence AND a positive control that the
  note survives — read by the reviewer.)
- SC-17: A harness-rooted session whose `.harness/harness.json` is **missing, unparseable, or not
  a mapping** refuses loudly and names that config path — never an empty, partial or defaulted
  config. This is the control plane's own copy of the rule SC-03 applies to a product's: an
  unreadable config closes rather than degrades (the same clause `CLAUDE.md` states for a missing
  PyYAML — a loud error, never a quieter mode).
  verify: automated      evidence: unit

## Verification gaps

Read from `test_kinds` in `.harness/harness.json` at `63b83c7`. Four kinds have `cmd: null` and
therefore no runner: `functional`, `component`, `ui`, `eval`. Of these only `functional` touches a
surface this feature could plausibly want.

- `functional` has no runner and is `excluded` here under DEC-187. This feature crosses a process
  boundary in exactly one place — nothing. The resolver reads files and computes paths; no `gh`,
  no `git`, no subprocess. So the exclusion costs this feature nothing, and that is a measured
  statement about this feature, not a general one.
- **The gap that does cost something:** no runner anywhere executes against a real checkout under
  `workspace_root`. Every criterion above is proven on fixture directories. **What is therefore
  NOT proven: that resolution works on the actual `harness-factories/kaya-ai` checkout** — which
  does not exist at `63b83c7`; `ls /Users/molchairuangutai/GitHub/harness-factories` fails. SC-12
  carries that, as UAT, by the operator's own hand. It stays `not_met` until the operator runs it.

## Constraints

- **DEC-174** — `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py` and
  `check-state.sh` are never changed through a team run. Any task touching them is
  `main-session-direct`.
- **DEC-179** — routing is resolved at plan time by `check-domain.sh --resolve`. **Three** of this
  feature's surfaces resolve to NOBODY and are declared main-session steps for that reason, which
  is distinct from the DEC-174 reason: `.harness/products/kaya-ai/harness.json` (T-02),
  `.claude/skills/harness-init/SKILL.md` (T-03) and `.claude/skills/harness-qa-gate/SKILL.md`
  (T-07). Each was re-resolved by running the guard at `63b83c7`.
  **Correcting the first draft**, which named four surfaces including `.harness/factory/fleet.yaml`
  and `.claude/skills/harness/templates/harness.json`: those two do resolve to NOBODY, but neither
  is a surface of this feature. Kaya is already registered in `fleet.yaml`, so no task edits it,
  and `templates/harness.json` is harness's own template, untouched under D-01 option A. The false
  half was "of this feature's surfaces", not the NOBODY verdict. **No task was added to make the
  sentence true; the sentence was wrong.**
  `.harness/harness.json` (T-06) resolves to `harness-dev-ops` — a real grant, not NOBODY — so it
  routes as a team task.
- **DEC-187** — the closure invariant on any `test_matrix`, including a product's. See D-03.
- **DEC-192** — the six station values are prescribed byte for byte and case sensitive. A product
  board's `stations:` mapping exists because a foreign board may name its columns anything; that
  asymmetry survives this effort.
- **DEC-193** — code is written in exactly two locations. This feature adds a config location, not
  a code location, and nothing here creates a third checkout.
- **DEC-171 / DEC-190** — PyYAML and `jsonschema` are required; a missing import is a loud error.
  The resolver uses `safe_load`, never a line scan.
- **DEC-133** — the feature id is immutable.
- **The operator-facing command grammar is contracted in `DESIGN.md`**, and that contract is an
  input to the resolver's task, not a suggestion: one JSON stdout line on success with exactly
  `source`, `config_path` and `product` (`null`, never omitted, when harness answered) and no
  config body; every refusal exits 2 with empty stdout, so the actionable path or repository name
  rides in the stderr `value` slot; and `factory_cli.body`'s third slot is the operator's next
  **action**, never the cause.
- **The resolver's module name is `factory_product_config.py`.** Not a style choice: the SC-18
  invariant in `test-factory-config.py` enumerates only `factory_*.py` when it asserts that
  exactly one scope in the tree opens the fleet file. A module named `product_config.py` would sit
  outside that enumeration permanently, so a future bypass of `load_fleet` inside it would never
  be seen. The name buys the coverage for free.
- The per-product path uses the repo segment after the slash, matching
  `factory_config.workspace_path`. Two owners with the same repo name collide; that collision
  already exists in `workspace_root` and is inherited, not introduced.

## Approval

status: pending
