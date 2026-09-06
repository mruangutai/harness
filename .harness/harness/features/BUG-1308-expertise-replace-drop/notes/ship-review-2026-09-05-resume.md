# BUG-1308 — ship review

**Recommendation: SHIP.** Validation is green, all fourteen success criteria are met, and the six
defects found along the way are all closed and independently re-verified. Nothing gates.

**Ship candidate:** `433df52092834f4358de234449c736ae554738e9`, on
`feat/BUG-1308-expertise-replace-drop`, merged onto latest `origin/main` (`0f885a0a`) with no
conflicts. Branch clean. Cycles **8 of 8 — budget exhausted**, so any further gating finding stops
the feature rather than buying a fix.

**No report round was spawned** (DEC-69). This briefing was assembled by reading these digests and
notes directly:

- `runs/2026-09-05-01-eng/digest.md`, `runs/2026-09-05-02-validator/digest.md` (build, T-01/T-02)
- `runs/2026-09-05-t04-docs-product/digest.md`, `runs/2026-09-05-renumber-dec219-product/digest.md`
- `runs/2026-09-05-qa-gate-validator/digest.md`, `runs/2026-09-05-simplify-eng/digest.md`
- `runs/2026-09-05-2-eng/`, `runs/2026-09-05-3-eng/`, `runs/2026-09-05-e1b-product/digest.md`
- `runs/2026-09-05-c4-validator/digest.md` (final panel), and pm's goal-check note
  `notes/research-BUG-1308-expertise-replace-drop-goalcheck-sc-c4.md`
- The plan-phase digests under `runs/2026-09-05-plan-panel-c1/c2-validator/` and
  `runs/2026-09-05-goalcheck-c1..c3-product/`, inherited rather than run by this session.

## What shipped

`expertise-merge.py` could only ever ADD to an Expertise file. A distillation could append an entry
but never correct or retire one, so the reconciliation DEC-66 specified had no applier at all.

BUG-1308 adds a second subcommand, `ops`, taking the distill contract's own op objects as JSON from a
file path — `add`, `replace`, `drop`. A target is keyed on section plus entry id, both required.
Every op resolves against one base snapshot under the lock `apply` already holds, and each affected
section is rebuilt in base order: one proposal is one order-independent rebuild, a replace rewrites
its entry without moving it, and caps are checked once on the final state. `merge` stays an authoring
concept, written as a replace plus a drop. Recorded in SPEC §5.3 and as **DEC-219**.

## The honest part: three panels, three highs the tests never saw

This is the finding worth your attention, more than the feature itself.

| Cycle | What the panel found | Status |
|---|---|---|
| 1 | **VL-01** — a newline inside an op entry injected a section header past the cap check. REQ-03 false as shipped. Plus VL-02/03/04. | closed `3488ca38` |
| 2 | **VL-05** — VL-01's *root cause survived its own fix*. The validator rejected 2 characters; the parser's `str.splitlines()` breaks on 10. A `U+2028` left 16 entries in a section capped at 15; a vertical tab silently moved entries between sections. | closed `8a0121b0` |
| 3 | **VL-06** — `target` was never matched against the id grammar. `add target="PPPP-1"` reported success and persisted data the tool's own parser could not see, which a later op then deleted. `add target="P-01: fake prefix"` planted a duplicate id that **locked that entry against every future replace and drop** until hand repair. | closed `a737eb9d` |
| 4 | Nothing gating. All six closed under fresh execution by two independent reviewers each. | **PASS**, severity_max `med` |

**Every one of those landed on a surface no success criterion named.** That is why twelve green
criteria coexisted with a falsified requirement through two consecutive goal-checks. The suites were
never wrong; they were never asked. Both later fixes were therefore made *derivational* rather than
enumerated — the line check now asks the parser what a line is, and the grammar check round-trips
through `ENTRY_RE` itself — so neither can drift from its source again.

## Verification

Measured by the orchestrator on the merged tree, not relayed:

- unit exit 0, zero `FAIL`, 29 files · integration exit 0, zero `FAIL`, 46 files
- T-04's own `verify:` block passes verbatim; `test-gen-decisions-index.py` exit 0
- Exploit probes run directly against the tool: newline, `U+2028`, `\x0b`, `\x85`, `PPPP-1` and
  `P-01: fake prefix` **all refuse at exit 12 with the file's sha256 byte-unchanged**; positive
  controls `add P-09`, `replace P-01`, `drop G-01` each exit 0 — so the refusals are not passing by
  rejecting everything.
- **REQ-07 holds mechanically:** the diff of `expertise-merge.py` against `origin/main` removes
  **zero** lines across every cycle. The pre-existing `apply` path was never touched.
- qa's gate PASSED; the panel's PASS was discriminated by mutation — neutering the new validator
  reddens `u21` across all three verbs while the positive control stays green.

## Operator decisions

1. **SC-13 and SC-14 adopted.** The operator's delegated Advisor adopted both as an approved BRIEF
   amendment. SC-13 grades cap preservation under every boundary derived from `str.splitlines()`;
   SC-14 grades target identity by round-trip through `ENTRY_RE`. Both are already MET by the
   existing unit and integration evidence named in the final goal-check note, so this changes no
   implementation or validation verdict.
2. **REQ-falsifying findings must propose a criterion.** This process improvement is preserved as a
   follow-up because VL-01, VL-05 and VL-06 each falsified a requirement on a surface no criterion
   named.

## Proposed backlog

Unstruck rows become issues on ship acceptance. **Anything not listed here dies silently.**

| ID | Nature | Item |
|---|---|---|
| B-1 | bug | **VLD-01** No character-length cap on `target`/`entry`; `check-expertise.sh`'s `WORD_CAP=50` counts words, so a 10 KB single-token line passes clean. The file is injected whole into every spawn, so it taxes every later context. |
| B-2 | enhancement | **VLD-02** Python's unicode-aware `\d` lets `P-١`/`P-０１` pass as ids distinct from `P-01`. Round-trips consistently, so it is human confusability only. Remedy narrows `ENTRY_RE`, which REQ-07 pinned — hence post-ship. Do this before B-3 and B-6. |
| B-3 | chore | **VLD-03** The exit-12 grammar refusal echoes the offending value but never states the shape that would pass. |
| B-4 | bug | **VLD-04** `cmd_ops` catches only `JSONDecodeError`; a deeply nested `--ops` payload raises an uncaught `RecursionError` at exit 1 instead of a documented refusal code. Fails closed, no data loss. |
| B-5 | bug | **VLD-05** Non-line-breaking control characters (ESC/ANSI, NUL, ZWSP) persist verbatim into the rendered file on a successful add. |
| B-6 | chore | **VLD-06** CLI-level grammar coverage is add-only; `replace`/`drop` are proven at the resolver. Buys a demonstration, not protection. |
| B-7 | bug | **No shipped gate enforces Expertise id uniqueness.** The panel showed the tool is internally consistent, not that the invariant is held. This is the load-bearing assumption behind the whole feature. |
| B-8 | chore | SPEC §5.3's **apply-side** citations are stale and predate this feature (`compute_union`, `cmd_apply`, `CAPS`, and an `acquire_lock` naming no live symbol). Deliberately left out of this diff. |
| B-9 | enhancement | §5.3 pins behaviour to raw line ranges in a file that keeps moving — **three realignments in one feature**. Durable fix: cite stable symbol names, plus a generated check resolving every `file:line` cite in `docs/**` to the symbol the prose names. |
| B-10 | bug | **`handoff-*.md` cannot be written for a worktree-only feature.** `handoff_done_when.py` resolves `feature_dir` against the project root, so `brief-sc:`/`plan-task:` never resolve; `FINDING_RE` wants `F-\d+` while this repo mints hex ids. Confirmed live at this HEAD. |
| B-11 | bug | `runs/<dir>/state.yaml` is unguarded where `digest.md` is guarded, and nothing stops a write into an occupied run dir. One checkpoint was destroyed twice here. |
| B-12 | bug | The unit runner's discovery count is caller-dependent (28/29/74 files from one command) and it false-fails `test-plan-merge.py` unless invoked `env -u HARNESS_AGENT_TYPE`. A zero FAIL count does not bound what ran. |
| B-13 | bug | The run-digest append-only guard refuses a replacing write, so a digest cannot be corrected in place; and `bash-write-guard.sh` misreports a `mktemp -d` redirect target as `"xx"`. |

## Budget note

`runs[]` stands at **33 against an informational budget of 20** (INV-22 notes, never blocks). The
overrun is three adversarial panel cycles that each caught a high the suites could not, plus their
fixes and two docs realignments. Each run returned a verdict and advanced the feature; none was
churn. I would not have wanted to stop at 20.
