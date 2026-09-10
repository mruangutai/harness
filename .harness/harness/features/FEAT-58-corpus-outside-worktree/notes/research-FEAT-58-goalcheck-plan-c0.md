# Goal-check — the cycle-0 plan against the operator's stated intent — FEAT-58

Graded 2026-09-10 against `.harness/notes/dod-worktree-corpus-2026-09-10.md` (read end to end) plus
the same day's shape correction. Read-only; `plan.yaml` and `BRIEF.md` untouched. Siblings
`-c1.md`/`-c2.md` graded the superseded plan and are not cited here.

## Answer: NOT DELIVERED — one reason, and it is in a decision, not in a task

**The plan is a faithful encoding of the note in every respect but one: `D-08`'s derived include set
strips six tracked `.harness` subtrees the feature never meant to hide, and no criterion can see
it.** Everything else — all five things done means, all seven binding items, the three
weight-bearing proofs, the exclusions, the consolidation — holds. Coverage audit of the assertion
ledger: **36 rows checked, 36 landed, zero dropped.**

D-08 (`plan.yaml:240-243`) derives the cone as `git ls-tree -d --name-only HEAD` **minus
`.harness`**, plus `.harness/harness/features/<active>`. Measured just now on git 2.50.1, synthetic
`git init`, that exact cone:

    S .harness/factory/fleet.yaml        S .harness/harness/docs/DECISIONS.md
    S .harness/notes/note.md             H .harness/team-config.yaml
    H .harness/harness/features/FEAT-X/BRIEF.md   S .../FEAT-Y/BRIEF.md

Files directly in `.harness/` survive by cone's parent rule; **every `.harness` subdirectory other
than the active feature does not.** At the owner root that set is `factory/`, `logs/`, `notes/`,
`expertise/`, `harness/docs/`, `harness/expertise/` (`git ls-tree -d HEAD:.harness`). Grounded
consequences, all resolving root from the script's own location — i.e. the worktree:

- `factory_config.py:57-58` builds `FLEET_PATH` from `resolve_root(_BIN_DIR)`; `feature-worktree.py:79-83`
  exits 2 on `FleetError`. **Creating a worktree from inside a sparse worktree breaks.**
- `harness_boundary.py:470-472` returns `None, [], path` when `<root>/.harness/factory/fleet.yaml`
  is absent — silently emptying the workspace base list `classify()`'s cross-checkout tier uses.
  That is the tier `D-02` cites as REQ-08/SC-03's whole enforcement.
- `gen-decisions-index.py:2-5` and `check-decision-anchors.py:2` resolve
  `.harness/harness/docs/DECISIONS.md` through the same resolver — absent.
- `post-merge-sweep.sh:113-116` `load_fleet()` fails into a caught `None`: the sweep degrades mute.
- `BRIEF.md:6` names its own goal of record at `.harness/notes/dod-…md`, a path this cone deletes.

The plan mentions none of these subtrees anywhere (grepped `plan.yaml` + `BRIEF.md` for
`factory|harness/docs|\.harness/(notes|expertise|logs)`: no hit outside a `harness.json` test-kind
citation). This is the `.agents/skills` omission class the note made the positive control mandatory
for (note:227-230) — reproduced one level down, in `.harness`.

## Findings

| id | sev | lands on | finding | concrete change |
|---|---|---|---|---|
| GC-01 | **critical** | D-08, N-02 check 1 (`plan.yaml:462-466`), SC-01 | derivation excludes all of `.harness` when only the features corpus must be excluded; a worktree loses fleet, decisions, expertise and notes | rewrite D-08's derivation as: top-level dirs, **plus every tracked `.harness` subtree except `.harness/<repo>/features`**, plus `.harness/<repo>/features/<active>`; N-02 check 1 compares against that set |
| GC-02 | **high** | N-01 (`:336-339`), N-05 group 2 (`:784-801`), SC-01 | the fixture tracks only `.agents`, `.claude/skills`, `docs`, `tests` and `features/<id>`, so `REQUIRED_PATHS` has no non-features `.harness` subtree to assert — the mandatory positive control is structurally blind to GC-01 | fixture tracks `.harness/factory/fleet.yaml`, `.harness/harness/docs/` and `.harness/expertise/` analogues; `REQUIRED_PATHS` names each; N-05 asserts them per path |
| GC-03 | med | N-01 exclusions (`:367-379`), N-09 part 4 (`:1211-1213`) | X-1/X-2 resolve their targets from a literal list, and at N-01 no listed file exists yet — a missing path skips silently, so the exclusion greens over files never written | self-check asserts every listed path EXISTS before greping it, and that the list equals the plan's own test-file set; N-09 runs it in that mode |
| GC-04 | med | REQ-06, SC-09/SC-10, N-06/N-07 | note:117 rules "`--verify` is what gates call"; the plan wires only `--repair` (three hooks) and no gate invokes `--verify`, so it ships with no caller and is graded only in isolation | name the calling gate in N-06 or N-07, or record a decision that `--verify`'s caller is a human/CI step and which one |
| GC-05 | low | N-01 (`:360-363`) vs ledger A-01 | ledger promises "asserts no path under the real `.claude/worktrees` is read"; plan substitutes a <100 tracked-file bound, which caps cost but does not assert non-copying | add: the fixture's git toplevel is under the temp dir and no source outside it is copied |
| GC-06 | low | N-09 `change_type: docs` (`:1101`) | `docs` and `scaffolding` both resolve to `always: []` (`harness.json:233-238`), so the qa matrix requires nothing of the task carrying SC-12 | relabel N-09 `cross_module`, or state in-task why `docs` is right |
| GC-07 | low | all nine `traces:` | SC ids are carried in `traces:` (e.g. `:301`, `:1100`), which `harness-spec-driven` defines as the REQ list; N-01 additionally traces four REQs it discharges none of | keep SC traceability if deliberate but say so; narrow N-01's REQ traces |

## Axis verdicts

**1 — the five things done means: FAIL.** Each of the five is **delivered by a production change**,
not merely tested: cone (N-02+N-04), symlink created by `--repair` (`:476-479`), audit narrowed at
the choke point (`:847-864`), index + gate + live correction (N-07/N-08), scope guard for a
non-worktree checkout (`:445-457`). Point 2's "readable with ordinary tools" is right: N-03 clause
(a) forbids `git show` and requires `open()`/`cmp` (`:569-571`). Corroborating D-09's empty-reader
claim: grepping `.claude/skills` found **no** live cross-feature disk read — `suite_layout.py:18-26`'s
`FEAT-44` entry is compared against `git ls-files` output, never opened. The axis fails only on
GC-01: point 1's mechanism also un-materialises state points 3 and 5 depend on.

**2 — the seven binding items: PASS, clean.** Verified in the files, not in the table.
`BRIEF.md:50-68` carries REQ-01…REQ-07 one-to-one with D-1…D-5, M-1, M-2, each labelled with its
item; SCs at `:123-179` — D-1→SC-01, D-2→SC-02, D-3→SC-04/05/06, D-4→SC-07, D-5→SC-12, M-1→SC-09/10,
M-2→SC-11. None folded, none deferred, **all twelve `verify: automated`** — nothing graded by
inspection. **Explicitly: M-1 and M-2 are first-class.** They hold their own REQs (REQ-06, REQ-07),
their own criteria (SC-09/SC-10, SC-11) and their own tasks (N-02, N-04); REQ-07 states the
whoever-creates-it claim in the note's own terms (`BRIEF.md:65-68`). No drift back into detail.

**3 — the three that carry the weight: PASS, clean. Each can report RED, and each proof is
demonstrated, not asserted.**
- *Merge regression* (N-04 part 2, `:667-696`): own file, must fail today; step 1 asserts the S count
  non-zero first so a never-sparse fixture cannot green vacuously; step 4 keeps the pre-change
  reproduction and asserts the two runs DIFFER; if the fixture cannot reproduce the shape the task
  returns **BLOCKED** and the assertion is never weakened (`:691-692`). Red-capable: today
  `post-merge` has no `--repair`, so step 3 fails. The 3337/3807 figures are cited as the operator's
  host measurement and explicitly forbidden in any assertion (`:672-676`), with the host residual
  routed to a receipt heading — which is what note:220-221 asks for.
- *Equivalence* (N-06, `:901-921`): exit status EXCLUDED and named as such twice (`:903-905`, `:921`);
  normalisation limited to the absolute root, with a stated ban on widening; X must carry at least
  one real finding, asserted explicitly, killing the two-empty-sets tautology; discrimination
  perturbs X and requires inequality. Red-capable: yes, by the discrimination clause.
- *`--verify` does not repair* (N-02, `:524-542`): own file; manifest is path→sha256 **plus** the
  `git ls-files -t` skip-bit set, includes `.git/info/sparse-checkout` explicitly, records a symlink
  as its readlink target; asserts structures, never counts. Red proof: route one break through the
  repair path, record that this file reddens for that case only, revert.

**4 — the mandatory positive controls: FAIL (literal asks met, purpose defeated).** Per-path named
assertions from `REQUIRED_PATHS`, exit status explicitly never asserted, `.agents` **and** `.claude`
spellings with `realpath` equality, plus a non-active-feature-absent clause (`:784-801`) — yes.
Derivation proven by adding a top-level directory, with step 4 pinning `git status` and
`worktree-state.py`'s sha256 unchanged and a grep proving the name is not hardcoded (`:807-821`) —
yes. It fails because `REQUIRED_PATHS` cannot name what the fixture does not track: GC-02.

**5 — the exclusions: PASS.** X-1/X-2 are assertions in `--self-check`, not prose (`:365-379`), and
both must be shown to fire. Synthetic-fixture rule in D-11 and restated in N-01 with the #1526
precedent and an explicit no-`copytree` instruction. No SC is gated on a byte figure, a `du` value or
a size; the three sanctioned modes are the only ones used. Caveats GC-03, GC-05 are about enforcement
strength, not compliance.

**6 — the shape correction: PASS.** (a) Nine tasks, each a surface: fixture+baseline, mechanism,
corpus read path, hook tier, creation surface, audit, uniqueness, live correction, non-regression.
Two (N-05, N-09) carry no production file and legitimately grade surfaces N-02/N-04/N-06 deliver;
N-06's second part (`check-domain.sh:2150`) is on the audit's own report surface and D-02 argues it
(`:93-113`). No staple found. (b) **Coverage was not dropped.** Audited `runs/consolidate-eng/digest.md`
second block row by row: **25 matrix rows (A-01…A-23, X-1, X-2) + 11 finding-derived rows = 36
checked, 36 landed.** Spot anchors: A-15 split record/compare across N-01 `:381-411` and N-09
`:1149-1181`; A-17 N-02 `:524-538`; A-19 N-04 `:667-696`; F-06's remedy tail in both N-02 `:499-501`
and N-06 `:862`; VL-01's dirty-tree asymmetry N-02 `:483-488`, `:522`; C-01's owner-root refusal
N-07 `:973-984` and case (c); ALT-F3's single-implementation assertion N-07 `:1000-1001`.
**No dropped assertion, by name or otherwise.** One substitution, not a drop: A-01's promised
"no real `.claude/worktrees` read" became a <100-file bound (GC-05).

**7 — what the DoD kills: PASS, clean.** Grepped for all six. Migration/convergence: absent as a
task; `BRIEF.md:219-221` non-goal; the only hits are the `panel.note`'s record of the deleted T-10
(`:293`) and a `lanes:` row (settled unwritable). Corpus-root anchor and the fifteen-reader ledger:
present only as D-09's recorded rejections (`:32`, `:41-42`). Reflink/clonefile: `BRIEF.md:213-216`
non-goal, and inside X-1 as the reason a byte bound is banned. Byte-count criteria: none of SC-01…SC-12
is gated on one. Incremental-sweep cache: no occurrence. Nothing crept back.

## Open questions

- **Q1** SC-12 bundles two distinct failure modes (D-5 non-regression, REQ-10 nothing-altered). The
  shape correction says distinct failure modes each earn one, but splitting makes 13 — outside the
  stated ten-to-twelve. Operator's call; already raised as consolidate-eng Q1. Non-blocking.
- **Q2** GC-04: does the operator want `--verify` wired into a named gate in this feature, or is a
  human/CI caller acceptable? Non-blocking.
