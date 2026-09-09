# Receipt — harness-dev-ops — T-14 — command-adapter generator + Claude-only door gate

## Task
FEAT-56-central-onboarding-model, T-14. Files: `.claude/skills/harness/bin/sync-command-adapters.py` (new),
`.claude/skills/harness/bin/check-omp-port.py`, `tests/integration/test-sync-command-adapters.py` (new),
`tests/integration/test-check-omp-port.py`.

Intent cross-checked verbatim against `plan.yaml:1739-1803` — matches the relay in the dispatch exactly.

## Plan
1. Inspected `sync-agent-adapters.py` (interface: `--root` default `Path(__file__).resolve().parents[4]`,
   `--check`/`--apply`, drift list naming files, exit 1 on drift under `--check`).
2. Measured the real banner already authored by T-13 on all four `.claude/commands/harness*.md` files:
   `<!-- Generated from .omp/commands/{name}; do not edit. Run bin/sync-command-adapters.py --apply. -->`
   followed by `\n` then the canonical file's bytes verbatim (confirmed byte-exact via python diff for
   all four files: harness.md, harness-grilling.md, harness-plan.md, harness-ship.md). Generator's
   expected-adapter format is designed to reproduce this exactly, so --check should pass on the real
   tree without reconciliation.
3. TEST FIRST: wrote `tests/integration/test-sync-command-adapters.py` before the generator existed;
   ran it and confirmed RED for the right reason (module not found), then built the generator, then
   confirmed GREEN.
4. Added command-door block to `check-omp-port.py::check()`.
5. Added the one new redness case to `tests/integration/test-check-omp-port.py`.

(Appending sections below as work proceeds.)

## Banner design (measured, not guessed)
All four `.claude/commands/harness*.md` adapters authored by T-13 already carry, byte-for-byte:
`<!-- Generated from .omp/commands/{name}; do not edit. Run bin/sync-command-adapters.py --apply. -->\n`
followed immediately by the canonical file's bytes verbatim (confirmed via `python3` diff for all four
doors). The generator's `BANNER` template reproduces this exactly, so `--check` on the real tree
passes with no reconciliation write needed — no main-session hand-edit was required.

## RED-CAPABILITY proofs (verbatim)

### (a) sync-command-adapters.py --check on a Claude-only orphan (temp tree)
```
ok    orphan Claude-only door fails --check
ok    orphan failure names the file
```
Full test run output (12/12), including this case, is pasted in the "Full verify" section below.
The orphan case constructs `.claude/commands/harness-orphan.md` with no `.omp/commands` counterpart
— reproducing the pre-T-13 all-Claude-only-doors state — and asserts `--check` returns non-zero and
names `harness-orphan.md`.

### (b) check-omp-port.py new block: missing single door, and canonical root absent (temp tree)
```
ok    missing command door fails
ok    missing door is named
ok    absent canonical command root fails
ok    absent canonical root names all four doors
```
The second case deletes `.omp/commands` entirely and asserts all four
`.omp/commands/{door}.md is missing` messages appear in stderr (counted, not just non-zero exit).

## Full verify (verbatim, run from worktree root)
```
$ env -u HARNESS_AGENT_TYPE bash -c '
python3 .claude/skills/harness/bin/sync-command-adapters.py --check &&
grep -q "omp/commands" .claude/skills/harness/bin/check-omp-port.py &&
python3 .claude/skills/harness/bin/check-omp-port.py &&
python3 tests/integration/test-sync-command-adapters.py &&
python3 tests/integration/test-check-omp-port.py
'
OMP port surface: ok
ok    well-formed tree passes --check
ok    edited adapter body fails --check
ok    edited-body failure names the file
ok    missing banner line fails --check
ok    missing-banner failure names the file
ok    orphan Claude-only door fails --check
ok    orphan failure names the file
ok    missing adapter fails --check
ok    apply exits 0
ok    apply creates the missing adapter
ok    created adapter matches banner + canonical bytes
ok    check now passes after apply

12/12 cases passed
ok    Claude skills remain a real directory
ok    Agent Skills path links to Claude skills
ok    live provider-neutral tree passes
ok    missing AGENTS.md fails
ok    missing guidance is named
ok    concrete model in canonical agent fails
ok    provider coupling is named
ok    stale Claude adapter fails
ok    adapter drift is named
ok    missing explicit async enablement fails
ok    async liveness contract is named
ok    task wall clock limit fails
ok    wall-clock contract is named
ok    missing OMP child lifecycle wiring fails
ok    lifecycle wiring gap is named
ok    missing plan-sign-gate.sh wiring fails
ok    sign-gate wiring gap is named
ok    nonblocking nested Harness agent fails
ok    nested supervision contract is named
ok    missing command door fails
ok    missing door is named
ok    absent canonical command root fails
ok    absent canonical root names all four doors

23/23 cases passed
VERIFY_EXIT:0
```

## Syntax check (acceptance 4)
```
$ env -u HARNESS_AGENT_TYPE python3 -c 'import ast,sys;[ast.parse(open(p).read(),p) for p in sys.argv[1:]]' \
    .claude/skills/harness/bin/sync-command-adapters.py .claude/skills/harness/bin/check-omp-port.py
AST_OK
```

## git status --porcelain (acceptance 5)
```
 M .claude/skills/harness/bin/check-omp-port.py
 M .harness/harness/docs/BUILD.md
 M .harness/harness/features/FEAT-56-central-onboarding-model/plan.yaml
 M tests/integration/test-check-omp-port.py
?? .claude/skills/harness/bin/sync-command-adapters.py
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-dev-ops-t14-eng.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-documentor-fixpin-product.md
?? tests/integration/test-sync-command-adapters.py
```
`.harness/harness/docs/BUILD.md`, `plan.yaml`, and `receipt-harness-documentor-fixpin-product.md`
are sibling (documentor / orchestrator bookkeeping) changes — seen, untouched, not mine.
My four files: `check-omp-port.py` (edited), `test-check-omp-port.py` (edited),
`sync-command-adapters.py` (new), `test-sync-command-adapters.py` (new) — exactly the T-14 file list.

## Verdict
PASS. All five verify clauses ran verbatim and green. No banner reconciliation was needed —
the generator's byte-exact expected banner already matches T-13's hand-authored bytes on the real
tree. No writes outside the four T-14 files plus this receipt.
