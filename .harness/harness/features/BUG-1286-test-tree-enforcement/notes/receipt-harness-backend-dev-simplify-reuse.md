# REUSE angle — BUG-1286-test-tree-enforcement plan draft

**BLUF:** 2 findings. T-03's `--against` clause instructs reusing `baseline()` verbatim, but
`baseline()`'s row regex cannot match a tree-audit row at all — only its fence-extraction half is
reusable. T-01 adds a fourth spelling of test-shape vocabulary into a file that already carries
three, without deriving the two pre-existing ones from it. No finding on checks 2, 4, 5.
IDs to change: T-03 (intent, `--against` paragraph), T-01 (intent, constants paragraph).

## Check 1 — T-03 `tree-audit` vs `tests/manual/suite-census.py`'s existing subcommands: **finding**

Read all four existing subcommands and `baseline()` (`tests/manual/suite-census.py:20-30,32-45,
47-59,61-84,143-167`). `tree-audit` itself does not duplicate `verdict-lines`/`migration`/
`residue`/`children` — none of those enumerate test-shaped files by NAME_PATTERNS or classify by
disposition; `tree-audit` is genuinely new capability.

But T-03's own instruction (plan.yaml:258-261) says `--against` must "parse the fenced text block
out of the given note the same way the existing `baseline()` helper does." `baseline()`
(suite-census.py:23-30) does two things in sequence: (a) extract fenced ```/```text blocks via
`re.findall(r"```(?:text)?\n(.*?)\n```", text, re.S)`, and (b) per line, match
`re.fullmatch(r"(test-.*\.py)\s+(\d+)", line.strip())` — a path followed by a **numeric** count.
A tree-audit row is `path\tdisposition` (e.g. `foo.md\tout-of-vocabulary`) — the second column is
never a digit string, so `baseline()`'s row regex matches zero tree-audit rows, always. Applying
`baseline()` "the same way" to a tree-audit note silently returns an empty `rows` dict for every
input, which contradicts T-03's own required behaviour (print MISSING for every measured row,
exit 1). Only fragment (a), the fence-extraction, is reusable; fragment (b) is not and needs a new
regex over `path\tdisposition`.

**Cost:** the implementer either notices this at build time and writes a diverging parser anyway
(the plan's "the same way" then describes work that didn't happen), or takes the instruction
literally and ships an `--against` that reports zero MISSING/EXTRA rows for any note, defeating
the comparison T-04's verify depends on.

**Alternative — replace plan.yaml:258-261 T-03 intent with:**
> With `--against`, extract the fenced text block from the given note using the same
> `` ```(?:text)?\n(.*?)\n``` `` pattern `baseline()` uses at suite-census.py:24, but parse each
> line as `path` then a tab then `disposition` (never a numeric count — tree-audit rows have no
> `baseline()`-compatible shape), compare the row set to the measured rows, print each row present
> in one side only prefixed MISSING or EXTRA, and exit 1 on any difference.

## Check 2 — T-01 registry self-policing vs existing exact-path-registry validators: **no finding**

Searched `check-domain.sh`, `check-plan-routes.py`, `check-state.sh`, `check-expertise.sh`, and
`tests/unit/test-suite-layout.py`'s own `sole_implementations()` sweep (lines 17-20, 38, 110-134).
`SOLE_IMPLEMENTATION_EXEMPTIONS` (test-suite-layout.py:17-20) is the closest analog — a literal
exact-path tuple — but its policing is a single set-difference (`unexpected = sorted(set(
implementations) - set(SOLE_IMPLEMENTATION_EXEMPTIONS))`, line 112): no glob-character check, no
duplicate check, no "unnecessary" (never-would-be-flagged) check. `suite-census.py`'s `residue()`
(lines 61-84) checks `RESIDUE_EXEMPTIONS` for staleness (an unmatched exemption is flagged, line
82-83) but its tuples are `(path, text-fragment)`, not `(path, reason)`, and it never checks for a
glob character or a duplicate entry either. `check-plan-routes.py`'s glob/literal split
(lines 235-236) polices the plan's `files:` lists, an unrelated registry. No existing script
performs T-01's specific four-way self-policing (glob / duplicate / untracked / unnecessary) over
an exact-path exception registry; T-01 is new capability, not a restatement.

## Check 3 — T-01's `NAME_PATTERNS`/`SOURCE_EXTENSIONS` vs existing vocabulary: **finding**

Three spellings of "what counts as a test-shaped file" already exist in the tree before T-01 adds
a fourth, all inside files T-01 itself touches or that sit one hop away:
- `suite_layout.py:20`, `test_shapes = ("test-*.py", "test_*.py", "*_test.py")` — used for the
  `tests/` misplacement rglob.
- `suite_layout.py:30`, the inline tuple `("test-*.py", "*.test.*", "probe-*")` — used for the bin
  planted-file glob.
- `.harness/harness.json` `test_kinds.unit.detect`:
  `"tests/unit/**|**/*.test.*|**/*_test.*|**/test_*.py"` (harness.json:269) — a pipe-glob DSL for
  qa's own detection, a different consumer/format, not in scope for T-01 to touch.

T-01's `NAME_PATTERNS = ("test-*", "test_*", "*_test.*", "*.test.*", "probe-*")` paired with
`SOURCE_EXTENSIONS` is a superset of the first two tuples' vocabulary (adds `probe-*` and
generalizes the extension), but T-01's intent (plan.yaml:112, "Keep every existing clause, message
string and ordering in the predicate exactly as it is") explicitly leaves `test_shapes` (line 20)
and the bin tuple (line 30) as their own hand-typed literals rather than deriving them from the new
constants. That leaves three independently-editable spellings of the same vocabulary inside one
file. **Concrete cost:** whichever pattern set is touched next (e.g. adding `*_spec.*`), the other
two tuples are not mechanically implicated by that edit and nobody is prompted to update them —
`test_shapes` at line 20 is the one least likely to be remembered, since it is a local variable
three functions away from the new module-level constants, not exported or referenced by anything
that would fail loudly if it went stale.

**Alternative — append to plan.yaml:112-124 T-01 intent, after the constants paragraph:**
> Do not hand-type a fourth spelling: define `test_shapes` (currently a local tuple at
> `suite_layout.py:20`) and the bin planted-file tuple (currently inline at `suite_layout.py:30`)
> as derivations of `NAME_PATTERNS`/`SOURCE_EXTENSIONS` (e.g.
> `tuple(p + ext for p in NAME_PATTERNS for ext in (".py",) if ...)` scoped to each clause's own
> narrower needs), so the three clauses cannot drift out of sync. Message strings and ordering are
> unaffected by this — only the pattern *source* changes.

## Check 4 — task `verify:` hand-rolling an existing bin script: **no finding**

T-01's verify runs the real test file plus `run-unit-tests.sh --check-layout`; T-02's runs the
integration test file; T-03's runs the new subcommand directly; T-04's runs `tree-audit --against`
against the note it just wrote; T-05's runs `gen-decisions-index.py --stdout | diff` plus
`check-decision-anchors.py`. Each verify invokes the real instrument rather than reimplementing a
check any `.claude/skills/harness/bin/` script already performs.

## Check 5 — task intent restating a procedure another task owns: **no finding**

T-03's intent states the expected pinned-SHA measurement (9 rows outside `tests/`, 1 exception, 8
out-of-vocabulary, 0 violations, plan.yaml:263-265) as a self-check for the subcommand's author;
T-04 owns *producing* the audit record and its per-row prose, a distinct deliverable (a note file,
with reasons "in your own words," plan.yaml:288-291) rather than the same procedure restated. T-05's
DEC-213 amendment paragraph necessarily restates T-01's shipped invariants in decision-record prose
— that is T-05's actual job (documenting what T-01 built), not a duplicate procedure.
