# EFFICIENCY angle — BUG-1286 plan draft (T-01..T-05, D-01..D-06)

**BLUF: no findings.** Measured the hot-path subprocess pair at ~46ms combined per
`run-unit-tests.sh` invocation in this checkout (2670 tracked files) — negligible against the
~15s integration suite it gates and against the two CI call sites that actually exist. The
conjunct order spends one of the two subprocesses on roots that will turn out inert, but the
saving is single-digit milliseconds in a rare edge case, not worth reordering at the cost of the
fail-closed guarantee. The 13 new test cases add real subprocess work but stay an order of
magnitude under each task's 60s budget. T-03's re-enumeration is not redundant with T-01's — they
read different git objects for different reasons.

## 1. Hot path: the two subprocesses inside `violations(root)`

Measured directly in this checkout (`git ls-files | wc -l` = **2670** tracked files):

- `git ls-files -z` (read-only): `real 0m0.025s`
- `git rev-parse --show-toplevel` (read-only): `real 0m0.021s`
- Combined: **~46ms** per `violations(root)` call, sequential (`tracked_paths()` per T-01's spec
  runs both inside one function).

(a) Call sites, found by grep, not guessed:
- `.github/workflows/tests.yml:86,92` — CI runs `run-unit-tests.sh --kind unit` then
  `--kind integration`, **2 invocations per CI run**, each paying the layout check once before
  kind dispatch (`run-unit-tests.sh:33`, ahead of the `run_pool.py` exec at line 47).
- `.claude/skills/harness/bin/validate-digest.py:1613-1665` (`_reverify_suite`/
  `check_qa_matrix_claim`) — re-runs the whole `run-unit-tests.sh` (30-minute timeout) once per
  digest that claims an unconditional `VERDICT: PASS` + `suite: pass` + `matrix_ok: true`; each
  such re-run pays the same 46ms once.
- No other scripted invocation exists; every other grep hit (`CODEOWNERS`, `harness-spec-driven/
  SKILL.md`, `DECISIONS.md`, per-feature `notes/*.md`) is prose or a human-typed manual run, not a
  call site.

(b) Cost is justified. `.github/workflows/tests.yml:88`'s own comment measures the integration
kind at "~15s"; 46ms against that is ~0.3%, and against the 1800s `_reverify_suite` timeout it is
noise. The two subprocesses are not per-file or per-test-case — they fire once per
`run-unit-tests.sh` invocation, not once per script in `SCRIPTS`.

(c) No cheaper shape to propose. Dropping `git rev-parse --show-toplevel` would remove the exact
protection T-01's own intent names ("a fixture root nested inside another checkout can never be
scanned against the outer index") — that is a correctness loss, not an efficiency win, so it is
not flagged.

**No finding.**

## 2. Order of the D-03 conjuncts

- `.git` entry exists — free, `os.path.exists` (filesystem stat).
- index carries `suite_layout.py` — free once `tracked_paths()` has already returned (membership
  check against the set already in memory); it is a fully free operation only in the "clean" case.
- git toplevel realpath-equals root — **costs a subprocess** (`git rev-parse --show-toplevel`,
  ~21ms measured above).
- `tracked_paths()` — **costs a subprocess** (`git ls-files -z`, ~25ms measured above).

T-01's stated order runs `git ls-files -z` first and folds the toplevel comparison into the same
function's failure branch ("`git rev-parse --show-toplevel` not resolving... to the same
directory as root" is one of `tracked_paths()`'s own `LookupError` conditions). So on a root
nested inside another checkout, the ~25ms `ls-files` enumeration runs and is then thrown away when
the toplevel check fails it. Swapping the two subprocess checks (toplevel first, then ls-files)
would save one subprocess spawn — but only in the nested/foreign-root case, which is the rare
edge case exercised by fixtures, not the common "clean real checkout" path where both subprocesses
run regardless of order. The saving is bounded by ~25ms and only in that rare case.

I checked explicitly whether such a reorder changes behaviour: it does not, if done correctly —
`tracked_paths()` would still raise `LookupError` with the same "cannot enumerate tracked files
under {root}: {reason}" message, still surfacing as a violation (fail-closed, per SC-04), not a
silent inert pass. So a toplevel-first reorder is behaviour-preserving.

Given the saving (single-digit-to-tens of milliseconds, only on an already-rare path) is smaller
than the noise band already established in check 1, this does not clear the "hot-path
milliseconds" bar this angle is scoped to.

**No finding** — the potential reorder is real but not worth a plan change at this magnitude;
recorded here so a future reader does not re-derive it.

## 3. Per-case cost of the new coverage vs. the 60s `verify:` budget

Measured current runtimes in this checkout:
- `tests/unit/test-suite-layout.py` (5 existing cases, no subprocesses): `real 0m0.097s`.
- `tests/integration/test-run-unit-tests-layout.py` (5 existing cases, 9 `run()` subprocess
  calls): `real 0m1.360s` (~150ms/call average, each call itself execs `run-unit-tests.sh` →
  `run_pool.py`).

T-01 adds 8 unit cases, most requiring a real git fixture (`git init -b main`, `git add -A`,
commit — each tens of ms per the measurements above, comparable to the ~46ms hot-path pair since
they are the same class of git subprocess). Even generously budgeting ~150ms per new case (fixture
build + one or two `violations()` calls), 8 cases add on the order of ~1.2s, landing the unit
suite well under 10s — T-01's `verify:` also runs `run-unit-tests.sh --check-layout` once more
(~50-100ms), nowhere near the 60s the file's own `run()` helper already budgets per subprocess
call.

T-02 adds 5 integration cases, each building a `git_tree()` (git init + commit, tens of ms) plus
1-3 `run()` calls (~150-300ms each per the existing average, higher for `--kind all` since it
executes both fake sentinel scripts through `run_pool.py`). Budgeting generously, 5 cases add
~2.5-3s, landing the integration file around ~4s total — still nowhere near 60s.

No pair of new cases is redundant at equal binding strength. T-01's unit cases exercise
`suite_layout.violations()` directly (predicate level); T-02's integration cases exercise the same
scenarios (single rogue file, three rogue files, `.git`-replaced-by-empty-dir) through the real
`run-unit-tests.sh` subprocess (wiring level: exit code, `MISCONFIGURED:` stderr formatting, and
the ordering guarantee that no sentinel runs first). These are different binding strengths by
design — the pyramid's two layers, not a duplicate — so none is named as redundant.

**No finding.**

## 4. Repeated I/O across T-01 and T-03

T-01's `tracked_paths()` reads `git ls-files` (the **index**: staged working-tree state, so a
staged-but-uncommitted addition is scanned and a staged deletion is not — D-03's own wording).
T-03's audit reads `git ls-tree -r --name-only <ref>` (a **committed tree** at an arbitrary,
caller-supplied `--ref`, defaulting `HEAD`) so the audit is reproducible byte-for-byte against a
named revision, including `review_sha`, independent of whatever is staged in the working tree at
audit time.

This difference is load-bearing, not incidental: T-01's guard must fire on the developer's current
staged state before a commit exists to point `--ref` at, and T-03's audit must be re-runnable
against a fixed historical commit (SC-09 explicitly re-derives it against `review_sha` later, when
the working tree may have moved on). A single enumeration pass cannot serve both — one is
inherently "now, staged" and the other is inherently "then, committed" — so merging T-01's and
T-03's enumeration into one pass would either make the guard blind to staged-but-uncommitted rogue
files (breaking D-03) or make the audit unreproducible against an arbitrary past ref (breaking
T-03's own `--ref`/`--against` contract and SC-09).

**No finding** — the two `git` reads are answering different questions and neither can substitute
for the other.
</content>
<parameter name="i">Writing efficiency-angle receipt