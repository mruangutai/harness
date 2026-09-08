# Security review — BUG-151-check-domain-fail-aggregation — c1 (re-pinned)

review_sha: 9b7b27d074924af2be46194536d6baca4ad4dd18
Diff command used (exactly as specified, not `main`/`merge-base`):
`git diff 6d969ed3..9b7b27d074924af2be46194536d6baca4ad4dd18 -- tests/integration/test-check-domain.py`
139 insertions / 46 deletions, one file. Read the full pre-image and post-image of the file plus
the unified diff (both hunks: the `import` line, and the ~200-line block replacing
`run_bug1305_cases`/`main`).

## VERDICT: PASS — no must-fix. severity_max = low.

## What I checked (identity-level, not read-and-conclude)

**1. Fail-open via exception inside a discovered block.** Reproduced independently (not copied
from the lead's method): defined a block that prints then raises inside
`contextlib.redirect_stdout(tee)`, called it the way `_run_block_captured` does. Result: the
exception propagates past the `with` block (stdout is correctly restored — `sys.stdout is
sys.__stdout__ == True` — because `redirect_stdout.__exit__` runs on the exception path), and is
never caught anywhere in `_run_block_captured` or `main()`'s discovery loop. An uncaught exception
in any discovered `run_*` gives the process a nonzero exit via Python's default traceback handler,
before `sys.exit(1 if main() else 0)` is ever reached. **Fails CLOSED.** No regression from the old
code, which had the identical no-try/except shape.

**2. Discovery-loop escape/spoofing (D-02).** Grepped every module-level `run_\w+` binding
(`def` or `name =`) in the post-image: all 24 are `def`s, none are aliases, lambdas, or imported
names — so today there is no non-runner callable that discovery would accidentally invoke, and no
`run_*` runner is missing from discovery (matches the lead's 405-line/24-block count: the same 23
functions the old explicit call-list ran, plus the one new self-check). Discovery genuinely
subsumes the old explicit list; nothing was silently dropped by the refactor. The general risk
that some *future* contributor could name an unrelated helper `run_foo` and have it auto-invoked
is inherent to D-02 and was accepted at plan time, not introduced or worsened by this diff.

**3. Aggregation-predicate soundness (D-01), pushed with a constructed adversarial block —
identity-level, executed, not argued.** `_aggregation_verdict` only checks *agreement of
zeroness* between printed column-0 `FAIL` lines and the returned total, by design (R-1/D-01). I
built two counter-scenarios and ran them through the real `_run_block_captured`:
  - a block returning a negative total with a *disagreeing* printed count → the diagnostic DOES
    fire (`bool(0) != bool(-1)`), so `main()` still returns nonzero overall. This is not a hole.
  - a block that prints one `FAIL`-prefixed line **and** returns `-1` (zeroness agrees, since
    both sides are truthy) run alongside a second, genuinely-failing block that returns `+1`:
    the diagnostic does NOT fire for the malicious block, and `fails` sums to `1 + (-1) = 0`,
    with `problems == []` → `main()` returns `0`, i.e. **exit 0 despite a real, printed
    regression.** Verified by direct execution (not inference) — see the two python
    reproductions in this run's tool trace.

    This IS a genuine hole in the safeguard's guarantee. But it is **not introduced by this
    diff**: the accumulation `fails += block_fn()` (`+=` over a plain int) is the exact pattern
    the pre-image already used (`fails += run_t12()`, …, `return fails + run_bug1305_cases()`),
    which had *zero* aggregation safeguard at all — a negative-returning helper would have masked
    other failures identically before BUG-151, with no diagnostic whatsoever. Every one of the 24
    real `run_*` helpers in this file computes its total as `fails = 0; fails += 1` (or
    equivalent non-negative counting) — none returns a negative value on any live path, so this
    is a latent property of the accumulator shape, not a reachable defect of this change. Rated
    **low**, not a finding requiring this cycle's fix: hardening it (e.g. `max(0, total)` or
    `abs`) would be a one-line, low-risk improvement worth a backlog note, not a gate.

**4. Data exposure in the new capture path.** The tee (`_AggTee`) still writes through to the real
stream by default, so nothing a human previously saw on screen is now swallowed — confirmed by
reading `_run_block_captured`'s `stream=stream if stream is not None else sys.stdout` default and
`write()` calling `self.real.write(s)` unconditionally. The new self-check's only in-memory-only
(non-passthrough) capture is `run_bug151_selfcheck_cases`'s own `wiring-seam-…` case, which
deliberately uses `io.StringIO()` to test the seam itself, not to hide anything — the strings fed
through it are hardcoded literals (`"FAIL  fake-block-prints-fail-returns-zero"`), never fixture
content, PII, or secrets. The `[:120]` truncation in the self-check's own failure message
(`detail = str(verdict)[:120]`) truncates a synthetic `f"{label}: {printed} … vs total={total}"`
string built from hardcoded case names and ints — no fixture or repo path data reaches it.

**5. Conventional surface.** No new subprocess/shell calls (the only `subprocess.run([HOOK], …)`
call is pre-existing, now just wrapped by `cases_tee`, same argv, same env). No new imports beyond
stdlib `contextlib`/`io`. Grepped the full diff for credential-shaped strings: none. No new file
I/O, no new network calls, no new deserialization of untrusted data — the block being executed is
always a module-level Python function the test file itself defines, never a value from payload,
fixture, or environment.

## Threat model

| boundary | STRIDE | mitigated | note |
|---|---|---|---|
| discovered `run_*` global set (D-02) | Tampering | true | no non-`def` binding exists today; grepped and confirmed |
| printed-vs-returned zeroness (D-01) | Tampering | true | BUG-151's exact shape (print FAIL, return 0) is caught; reproduced live |
| block returning a total with disagreeing sign/zeroness | Tampering | true | diagnostic fires on any zeroness mismatch, confirmed by execution |
| block returning a negative total that *agrees* on zeroness with its own printed line | Tampering | false | reproduced live (exit 0 despite a real concurrent failure); precondition-absent — no current `run_*` helper returns negative, so unreachable today; low-severity, not gating |
| exception inside a discovered block | Denial of Service / fail-open | true | propagates uncaught, exits nonzero; verified stdout is correctly restored on the exception path |
| in-memory tee holding block stdout | Information disclosure | true | passthrough is unconditional; nothing swallowed; no fixture/secret data enters the new self-check's synthetic strings |

## Corroboration with R-1/R-2/R-3

- R-1, R-2: not contested — this file's diff carries no code touching those areas.
- R-3 (CASES loop's inlined tee is non-gating): agree, independently confirmed by reading
  `main()`'s CASES loop — `fails += 1` / `print(...)` are co-located statements inside the same
  `for` body under one `with contextlib.redirect_stdout(cases_tee):` block, so there is no
  daylight between what increments `fails` and what the tee captures; no drift scenario exists
  for me to name either.

## Corroboration with the lead's measurements

Did not re-run the full 405-case suite (would duplicate the lead's and QA's own runs); instead
verified the SAME conclusion by a different, more adversarial method (constructed counter-blocks
run directly against the real `_run_block_captured`/`_aggregation_verdict`, per my Expertise
P-16/O-01 — identity-level, not read-and-conclude). No disagreement with the lead's numbers to
report.

## Non-goals honored

Did not audit `test-validate-digest.py` / `test-bash-write-guard.py` (R-2, out of scope). Did not
edit the reviewed file. Did not run project-wide suites.
