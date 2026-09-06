# Research — BUG-1308 Expertise replace and drop — 2026-09-05

BLUF: the issue's premise is confirmed at c369fb1 and the default branch (build the operation) is the
right one, not the Alternative (weaken the contract). The contract at
`.claude/skills/harness-distill/SKILL.md:112-123` already names `add | replace | merge | drop` with a
`target:` and declares a nonexistent target "rejected, not guessed at"; DEC-66 signed that vocabulary.
`expertise-merge.py` exposes one subcommand and `compute_union` (`:113-139`) appends new ids only.
Weakening the contract would require unwinding a signed decision to match a tool gap.

## What the mechanism already gives us

- `harness_merge.locked_update` (`harness_merge.py:121-153`) reads under an exclusive lock, calls a
  transform, and `os.replace`s the result. A `MergeRefusal` raised inside the transform writes nothing
  — fail-closed and byte-identity are properties of the primitive, not of new code.
- `require_expertise_destination` (`expertise-merge.py:153-192`) already gates the `--file` class at
  exit 9. A second subcommand reuses it unchanged.
- Exit codes in use: 0, 6 lock, 7 CONFLICT, 8 CAP EXCEEDED, 9 destination, 2 argparse. 10, 11, 12 free.
- `CAPS` is spelled once (`:37`) and cross-checked against `check-expertise.sh` as text by case 8 of
  `tests/integration/test-expertise-merge.py`. Nothing may add a third copy.
- `check-expertise.sh` enforces the four section names and the per-section counts only — no id
  contiguity — so a drop leaving a numbering gap is legal to the checker (`check-expertise.sh:42,161`).

## Why a second subcommand, not a directive inside the entries stream

The `--entries` stream is Expertise markdown parsed by `ENTRY_RE = ^- ([A-Za-z]{1,3}-\d+): (.*)$`,
which is the same shape `check-expertise.sh` parses. Putting a verb inside a line of that stream
changes a format two tools read and one of them is the format checker. The distill contract's ops are
already structured data in the DIGEST, so JSON ops are the same vocabulary in the medium it already
has. `apply` is then provably untouched, which is what REQ-07 asks for.

## Resolution against one base snapshot

Every op resolves against the ORIGINAL file, and nothing is applied until all ops have resolved. This
is what makes the three ambiguity conditions decidable and the whole proposal atomic; resolving op N
against the result of op N-1 would make "the file already carries a duplicate id" undetectable for a
later op and would make refusal order dependent on op order.

## `merge` is not a mechanism op

The contract's fourth verb synthesises new text from two entries — only the authoring agent can do it.
It is expressed as a replace on the surviving id plus a drop of the absorbed id. The tool refuses
`op: merge` at exit 12 naming that rewrite, and the contract text must say the same thing, or the
contract still promises a verb nothing applies (REQ-08).

## Lane resolution, re-run at c369fb1

`check-domain.sh --resolve` on every surface this plan names:

- `.claude/skills/harness/bin/expertise-merge.py` -> backend-dev, dev-ops (team)
- `tests/unit`, `tests/integration/test-expertise-merge.py` -> backend-dev, dev-ops, qa (team)
- `.claude/skills/harness-distill/SKILL.md` -> NOBODY (main-session-direct, DEC-174)
- `.harness/harness/docs/SPEC.md`, `DECISIONS.md`, `DECISIONS-INDEX.md` -> harness-documentor (team)

The dispatch's fact table named `docs/SPEC.md`; no such path exists — SPEC.md lives at
`.harness/harness/docs/SPEC.md` and resolves to documentor, not NOBODY. Corrected in the plan.

## Open question carried to the panel

Q1 — the entry-id reuse ban (DEC-66's accepted tradeoff) is unenforceable by the tool, which sees only
the current file and cannot know an id was dropped last month. Recommendation, recorded as D-12: the
tool refuses only what it can see — a drop and an add of the same target inside ONE proposal, at
exit 11 — and the ban across time stays a contract rule the author obeys.
