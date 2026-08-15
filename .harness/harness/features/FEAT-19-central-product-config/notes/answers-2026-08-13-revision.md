# Operator answers — FEAT-19 plan revision — 2026-08-13

**STATUS: SUPERSEDED — NEVER DISPATCHED. This file is now an INPUT TO A GRILLING, not a revision
instruction.** The ten answers below are settled and carry forward, but the effort they describe is
no longer the effort that was grilled: `notes/../../../notes/grilling-central-product-config-2026-08-12.md`
records a destination — "nothing else about onboarding moves in this effort" — that five of these
answers falsify. The operator ruled a fresh grilling rather than letting pm plan against seven
guesses. **Read this file for what is SETTLED; read the new grilling artifact for the destination
and the open questions.**

## A-01 — The Goal is too narrow. It must cover the board and the issue mirror, not only tests.

The operator's own words for the destination: **the factory can work on a repository that sits
outside harness, under `workspace_root`; it can update the board related to that repo, run the
tests related to that repo, and operate whatever else that repo needs — while the entire control
plane stays in harness.**

D-06 flips from option A to **option B — rewire both consumers.** The Goal, REQ-02 and every
criterion narrowed to "the test matrix only" widen to match. The sentence "Issue mirroring and
board writes for a product keep resolving against harness's `harness.json` until a later effort"
is struck: there is no later effort, and nothing tracked one.

## A-02 — Take advantage of the board that `fleet.yaml` already holds.

Do not invent a second source for a product's board. `fleet.yaml` has carried the board
per-repository since FEAT-16, and kaya's entry already holds `owner: mruangutai`, `number: 2`,
`station_field: Status` and its three station names. `factory_config` already exposes
`board_for(fleet, repo_name)` and `board_station(fleet, repo_name, key)`.

**Re-price option B with that in mind.** The BRIEF priced it as "a code change with its own review
surface" without recording that the resolution layer is already written and already used by three
tools. The remaining work is `gh-sync.py` asking `factory_config` instead of joining
`.harness/harness.json`.

## A-03 — Harness itself keeps reading `harness.json`, and that is not an inconsistency.

`mruangutai/harness` is deliberately absent from `fleet.yaml` under DEC-174 am.1 — the absence is
what makes `check-domain.sh --resolve` exit 2 instead of returning `NOBODY`. So the resolver serves
two cases by design: a product resolves through `fleet.yaml`, harness resolves through its own
file. This agrees with D-01 and does not reopen it.

## A-04 — Proving it end to end stays OUT of this feature.

The BRIEF's exclusion of cloning, running or testing kaya's code stands. A first real factory run
is its own effort; folding it in would hide config defects behind checkout defects.

## Facts the main session verified at `63b83c7`, so pm does not re-derive them

1. **The factory lane already resolves the per-repository board.** `factory_land.py:85` calls
   `factory_config.board_for(fleet, args.repo)`; `factory_claim.py` and `factory_decompose.py`
   validate each served repository's own board. That half of the goal already works and needs no
   task.
2. **`gh-sync.py` imports `factory_config` zero times** (`grep -c` = 0). It is the one tool in the
   family that does not.
3. **Why a product's feature resolves harness, traced rather than assumed.** `gh-sync.py:729` sets
   `root = abspath(feat_dir/../../..)` — the repository holding the feature directory. Features
   live in harness because harness is the control plane, so `root` is always harness and
   `github.repo` is always `mruangutai/harness`. The BRIEF's claim is correct and this is the
   mechanism behind it.
4. **The qa gate's source, verbatim** — `.claude/skills/harness-qa-gate/SKILL.md:45`: "Read
   `test_matrix` and `test_kinds` from `.harness/harness.json`."
5. **`workspace_root` not existing on disk is NOT a defect and must not become a task.**
   `factory_workspace.py:124` does `os.makedirs(parent, exist_ok=True)` before cloning, so
   `/Users/molchairuangutai/GitHub/harness-factories` is created on the first claim. It is a
   working directory the agents make, per repository. The main session raised its absence as a
   risk and the operator corrected that; the correction is recorded here so it is not re-raised.
6. **`FLEET_PATH` binds at import time** (`factory_config.py:52`). This is the defect engineering
   review already caught in T-01 — any fixture test that does not pass an explicit path reads the
   live repo's `fleet.yaml` and passes for the wrong reason. It applies to every new caller too,
   including anything added to `gh-sync.py`.

## A-05 — Notes and observations stay in harness. Expertise must resolve per product.

The operator asked where the notes and observation structure belongs — harness, or the product's
own checkout.

**Ruled: harness.** Three reasons, none new: FEAT-12 ended copy distribution, so the harness is not
copied into a product; the 2026-08-09 ruling makes harness the control plane; and a workspace
checkout is disposable — `factory_workspace.py` clones fresh, so anything written there dies with
the clone, while `.harness/` is committed. `features/<FEAT>/notes/` and `.../observations/` already
carry the feature id in the path (DEC-130), so a kaya feature and a harness feature never share a
directory. **That structure needs no change and no task.**

**But the question exposed a third instance of this feature's own defect class, and it is now IN
SCOPE.** `expertise/<agent>.md` is per **agent**, never per product. Once `harness-backend-dev`
works on kaya, kaya-specific knowledge lands in the same file the `SubagentStart` hook injects when
that role next works on harness. It is the same silent wrong answer as the test matrix and the
board, reached through the third door. **Nothing in the BRIEF, the plan or the grilling artifact
addresses it — the main session checked.**

**Operator ruling: add it to this feature.** Expertise resolves per product, so a role carries one
file per repository it works on. pm owns the shape and the criteria. Two things pm must weigh and
state rather than assume: the `SubagentStart` hook is what injects the file, so the resolution has
to happen where that hook reads; and a role working on harness must keep getting exactly what it
gets today.

**The codebase map stays out**, as the BRIEF already has it at `:231`. It has the same defect and
the operator has not reopened it. Its exclusion line must now say so explicitly rather than listing
it among re-homing chores, because the map is injected at spawn and is therefore the same class as
expertise, not the same class as the interview.

## A-06 — T-04 fixes the layout record's four false rows, not just its own.

`.harness/README.md` is the document a reader consults to answer exactly the question in A-05, and
at `63b83c7` it is wrong in four places. T-04 already opens that file to add the product config
location. Correct all four in the same task:

1. It lists `codebase/` — **the directory does not exist** (`ls .harness/codebase` fails).
2. It lists `features/<FEAT>/feature.yaml` — the file is `feature.json`, renamed two features ago.
3. It lists a top-level `BRIEF.md` and `PLAN.md` — those live per-feature now.
4. It **omits `members/`**, which exists on disk.

Re-derive all four at HEAD before editing; do not trust this list. This is the `#247` defect class
in the layout record itself, which is why it is not being left for later.

## A-07 — The per-repository layout migration is FOLDED INTO this feature.

The operator ruled that `.harness/` gains a repository level and that FEAT-19 does it, after the
main session recommended a separate effort and was overruled. **This is the operator's decision,
taken with the cost in front of them, and it is not to be re-litigated by pm or by any reviewer.**

**The shape, in the operator's words:** `.harness/<repo>/features/<FEAT>/` reads better than
`.harness/features/<product>/<FEAT>/`. The main session agreed and gave the reason: four things
already need per-repository resolution — the config, expertise, the codebase map, and features —
and one segment at the top covers all four and every future one, where a segment under `features/`
covers only features.

**The forced constraint that makes this a path question rather than a field question.** Write
permissions are granted by GLOB in `team-config.yaml` (`.harness/features/*/BRIEF.md`,
`.harness/features/**`, and six more). A glob cannot read a JSON field, so `feature.json`'s existing
`factory.repo` block — which INV-24 already reads — can RECORD the repository but can never GATE a
write. Per-product write isolation is only reachable through the path.

**Measured at `63b83c7`, replacing the FEAT-10 figure the grilling artifact carries:** 1499
references to `.harness/features` across 284 files; **206 of them in code and config**, which is the
migration surface. The rest is prose. `check-domain.sh`'s anchored regexes use `[^/]+`, which cannot
cross a path segment, so they are REWRITTEN rather than adjusted. No layout-migration machinery
exists in the tree.

**BLOCKING SUB-QUESTION, answered below in A-08: what is harness's own segment?** Harness is
deliberately absent from `fleet.yaml` under DEC-174 am.1, and the absence is load-bearing — it makes
`check-domain.sh --resolve` exit 2 rather than quietly return `NOBODY`. Any segment name for harness
risks re-creating the entry that absence was protecting; leaving harness flat makes it an exception,
and an exception in a layout rule is where drift starts.

## A-08 — Harness gets a real `fleet.yaml` entry, and the stale-checkout diagnostic gets its own signal.

**DEC-174 am.1 is amended by this feature, not ignored and not struck.** Its measurement is correct
and the main session re-took it at `63b83c7` rather than citing it. Probe applied and reverted
byte-identical, `git diff` empty:

| `fleet.yaml` | `check-domain.sh --resolve` on `<workspace_root>/harness/.claude/skills/harness/bin/check-domain.sh` |
|---|---|
| harness **absent** | `BLOCKED — under the factory workspace but belongs to no repository declared in <fleet path>. A checkout there for an unlisted repository is stale or a mistake. Add the repository to `repos` in that file, or remove the directory.` |
| harness **present** | `NOBODY` |

**What is lost is DIAGNOSIS, not permission — and the earlier framing of "quieter" was imprecise.**
Both outcomes refuse the write. The loss is that `NOBODY` is also the answer for any ordinary
ungranted path, so **a stale or mistaken checkout stops being distinguishable from a routine
permission miss.**

**The operator's ruling: add the entry AND restore the detection on its own footing.** The absence
of a fleet entry was carrying two jobs — declaring what the factory serves, and detecting a checkout
that should not exist. Adding the entry silently drops the second. A task in this plan gives that
detection its own signal, so the layout gains its uniform rule without the tree losing the sentence
that tells an operator a directory is stale.

pm owns the mechanism. Two constraints it must respect: the new signal must fire on the same case
the absence fired on, and it must be provably able to redden — a diagnostic that cannot fail is the
`#148` defect. DEC-174 am.1's entry is **amended with this measurement and this ruling**, in its own
voice, not marked and not struck: it was accurate about what it measured.

## A-09 — Budget: raise it as far as the scope needs.

Operator's words: "Increase the budget as needed. This is the right direction, and we wanna solve it
once and for all."

At the time of this revision FEAT-19 stood at **5 cycles of 10 and 4 runs of 20, with no build
started**, and the scope grew five times in one sitting: the board and issue mirror (A-01), expertise
resolution (A-05), the layout-record corrections (A-06), the per-repository layout migration
(A-07), and the fleet entry with its replacement diagnostic (A-08).

**The orchestrator raises `max_total_cycles` and `max_total_runs` in `feature.json` to fit the
re-scoped plan and states its reasoning.** The cap guards against thrash, never against work the
operator deliberately added. The five cycles already spent are NOT reset — they are real signal that
this plan has been round-tripped, and erasing them would hide it.

## A-10 — Expertise moves to `.harness/<repo>/expertise/<agent>.md`, in two layers.

**This SUPERSEDES A-05's "expertise resolves per product" by giving it a path and a rule.** A-05
established that it was in scope; this establishes the shape.

**The path is `.harness/<repo>/expertise/<agent>.md`, not `.harness/expertise/<product>/`.** The
operator named both shapes and chose the first. It is the same reasoning A-07 used for features and
it is recorded here so the two rulings cannot drift apart: four things need per-repository scoping —
features, expertise, the codebase map and config — and ONE segment at the top covers all four with
one glob rule. Namespacing expertise under its own directory would need a second convention for the
codebase map and a third for whatever comes next.

**Two layers, and craft carries while repository facts do not.**

- **Craft layer** — how the role works, true wherever it works: re-derive an anchor at HEAD before
  citing it; never quote a figure with no artifact behind it; prove a new check can redden. A role
  arriving on kaya keeps all of it.
- **Repository layer** — what is true of one repository: which test runner exists, which board
  number, which paths are granted. A role arriving on kaya must NOT carry harness's answers, which
  is the same silent-wrong-answer defect as the test matrix and the board.

pm owns the mechanism and must state the rule that decides which layer an observation belongs to —
without it, every writer guesses and the layers blend back into one. `inject-expertise.sh`
(a `SubagentStart` hook, registered in `.claude/settings.json`) is what injects the file today and is
therefore where resolution happens. `check-expertise.sh` takes a file or a directory and will need
to walk the new shape.

**A migration constraint, not an implementation detail:** ten expertise files exist today under
`.harness/expertise/`. They hold both layers mixed together, written before the distinction existed.
Moving them wholesale into harness's repository layer would silently discard the craft half for
every future repository. pm must plan the split rather than the move, and must not assume the split
can be done mechanically.

## Still open — the operator is reading

Further changes will be appended here before this file is dispatched.
