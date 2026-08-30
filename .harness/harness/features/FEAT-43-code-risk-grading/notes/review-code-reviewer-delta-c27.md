# Delta code review — cycle 27 — CI hermeticity fix

**BLUF: PASS.** SC-20's four clauses all resolve to live, correctly-wired implementations at pin
`4adb2219`. Both fixture files are byte-identical to the `df63193` blobs they vendor (SHA-256
confirmed, not diffed-by-eye). The eng lead's scope extension to two further call sites is
**RATIFIED** — same file, same root cause, disclosed in the commit message, no production or
workflow surface touched. One `med` finding: `check_prior_validator` fails open (silent pass, not
a crash) if a fixture were ever reduced to a syntactically-valid no-op — advisory, not blocking, and
does not describe the fixtures as shipped (verified non-corrupt by hash).

## A. SC-20 — four clauses, pin `4adb2219`

`BRIEF.md:210-218` (re-read at this pin): (1) policy is imported from config, not hardcoded — the
must_fix+PASS/`advisory_unless_high` pair rejects; (2) the same digest is accepted under `advisory`;
(3) a `gates`-less fixture makes the validator exit non-zero naming `gates`; (4) the previous
revision of the validator is run against the first return and shown to accept it.

| Clause | Implementation | Verified content |
|---|---|---|
| 1 | `check_review_policy` — `test-validate-digest.py:1946-1953` | `guarded = reviewer_digest("pass", must_fix=...)`; asserts `"review policy"` appears in errors under the `advisory_unless_high` config `write_review_config` sets at `:2604` before the call. |
| 2 | `check_config_errors` — `:2558-2561` | Same `guarded` object (passed in as a parameter, not re-derived) accepted under `write_review_config(config, "advisory")`. |
| 3 | `check_config_errors` — `:2562-2569` | Empty `{}` config; asserts `ValueError` naming `"gates"`. |
| 4 | `check_prior_validator` — `:1961-1990` | See below. |

Q11's citations (`check_review_policy:1946`, `check_config_errors:2503-2505,2523`) were written
against an earlier pin; at `4adb2219` `check_config_errors` has shifted to `:2558` (net +55 lines
from two additions ahead of it: `FIXTURE_DIR`/comment, `make_review_sha_repo`). Content, not just
line numbers, was independently re-read at the current pin — the shift does not affect the finding.

**Fixture byte-identity** (`shasum -a 256`, both exit 0):
- `validate-digest.py`: `git show df63193...:...` → `4933c60c...edb1646`; fixture file →
  `4933c60c...edb1646` — **match**.
- `harness_yaml.py`: `git show df63193...:...` → `ca261f64...fcd112f`; fixture file →
  `ca261f64...fcd112f` — **match**.

**Clause 4, executed path** (`:1961-1990`): fixture bytes are written into `td/prior/` under their
real module names, then `subprocess.run([sys.executable, ".../prior/validate-digest.py",
"harness-code-reviewer"], input=guarded, ...)` — a genuine subprocess invocation of the PRIOR code
against the SAME `guarded` object `check_review_policy` returned and `check_config_errors` already
exercised (not a fresh or paraphrased digest). `prior.returncode != 0` is what fails the test, i.e.
a prior-validator *rejection* is what fails it — matching the clause's requirement that the control
prove itself able to fail. Confirmed by inspecting the fixture's own `__main__` (line ~2170 of the
fixture): it calls `validate(sys.argv[1], text)` with **no config argument at all** — the pre-feature
validator has no review-policy gate to consult, which is *why* it accepts a must_fix+PASS digest the
current validator rejects. That is the discrimination clause 4 requires, not a duplicate of clause 1.

**No `git` in the function** (`sed -n '1961,1998p' | grep -n 'git '` → one hit, inside the docstring
reading *"no `git show`"* — a negation, not an invocation; exit 0 for the grep itself since it matched
that line, no runtime call).

`PRE_FEATURE_REVISION` is **not** runtime-inert file-wide: it is still read at `:2052`
(`check_reviewed_range`) and `:2361` (`check_review_sha_binding`) — but both are inside
`run_code_grade_cases`'s new `with ..., _hermetic_review_sha_cwd(td) as _cwd_marker:` block
(`:2602`), which reassigns the module globals `PRE_FEATURE_REVISION, REVIEW_SHA` to fabricated OIDs
from a purpose-built `/tmp` repo (`:2583-2586`) before either check runs, and restores the real
constants on exit. `check_prior_validator` itself never reads the name. This is not a violation of
the "documentation constant" instruction in spirit — the real `df63193` SHA is never resolved
against ambient history at runtime anywhere in the file after this commit — but it is a second,
larger use of the identifier the instruction's phrasing didn't anticipate; noted, not blocking, since
it is precisely the subject of item B below.

## B. Scope-call ruling: **RATIFIED**

`git diff --stat cd8dae47..4adb2219`: only `test-validate-digest.py` (+71/-8) and the two new
`fixtures/*` files changed. `grep` for `.github/workflows` and `production` in that diff: no hits.
No production module, no CI workflow file, changed.

The three call sites, before → after:
1. `check_prior_validator` (`git show df63193:<file>`, `check=True`) → reads vendored `.fixture`
   files. *(Named explicitly by Q11.)*
2. `check_reviewed_range` (`:2052`) — `f"{PRE_FEATURE_REVISION}..HEAD"` against the ambient
   checkout → now runs inside `_hermetic_review_sha_cwd`, against a fabricated repo.
3. `check_review_sha_binding` (`:2361`) — `f"{PRE_FEATURE_REVISION}..{REVIEW_SHA}"` against the
   ambient checkout → same wrapper.

Both `df63193...` and `94383e6...` (`REVIEW_SHA`) are confirmed real commits in this repo's full
history (`git cat-file -t` → `commit`, both). Before this commit, `run_code_grade_cases` opened only
a bare `tempfile.TemporaryDirectory()` — no repo substitution existed — so sites 2 and 3 resolved
these two SHAs against the **real, ambient** checkout, exactly as site 1 did via `git show`. A
depth-1 shallow clone (the CI environment Q11 names) contains exactly one commit object; it cannot
resolve `df63193` or `94383e6` under *any* subcommand, not only `git show`. `check_review_sha_binding`'s
own first assertion (`:2361-2363`) requires `validator.validate(...)` to *accept* a digest carrying
`reviewed: df63193..94383e6` — if the range does not resolve, the validator can only return an error
or raise, and either way the "must accept" assertion fails. This is not a hypothetical: it is the
same missing-object condition, in the same file, against the same two ambient SHAs.

Q11's text: *"Scope is the CI failure and nothing else."* The blocker section names
`check_prior_validator` because that was the operator's own report of what turned CI red on run
`33294260861` — not a statement that repository-history dependency was confined to that one
function. The ruling's own prescription is general: *"Remove the dependency on repository history;
keep the discrimination"* — a principle, not a function-scoped patch — and it directly quotes the
operator's invitation to *"assess the smallest correct hermetic fix (revise mine if needed)."* Fixing
sites 2 and 3 with the identical vendoring/fabrication pattern, in the same file, same commit, same
justification, transparently stated in the commit message ("the shallow clone that exposed this also
exposed two further history dependencies in the same file, fixed the same way. No assertion was
weakened.") is the smallest-correct-fix reading of that mandate, not an expansion into new territory:
no new production coupling, no new test surface, no weakened assertion — confirmed by re-reading
`check_reviewed_range`/`check_review_sha_binding`'s bodies unchanged apart from the ambient-repo
swap. **RATIFIED.**

## C. Fail-open: fixture missing vs. empty

- **Missing** (`FIXTURE_DIR/<name>` absent): `open(...)` at `:1976` raises `FileNotFoundError`,
  unhandled — the whole suite crashes with a traceback. **Fails loudly.**
- **Empty** (0-byte but present `.fixture` file): `f.read()` returns `""`; a 0-byte Python file
  executes as a no-op and exits `0`. `check_prior_validator` only inspects `prior.returncode`
  (`:1990`) — `!= 0` is the sole failure condition. An empty (or any syntactically-valid no-op)
  fixture therefore makes the subprocess exit `0`, and the function records **no failure at all** —
  a silent pass, not the loud rejection SC-20 clause 4 exists to prove. There is no check that
  `prior.stdout` actually contains validator output (e.g. `"digest ok"`), nor any length/hash guard
  on the fixture content. **`med`, advisory** — the shipped fixtures are hash-verified non-empty and
  byte-identical to `df63193`, so this does not affect the current pin's correctness; it is a
  robustness gap against future silent corruption (bad merge, truncation, encoding mangling) of a
  vendored control that is exactly the kind of thing this cycle was created to guard against.

## Tree state

`git -C <worktree> status --porcelain`:
```
 M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q11-ci-hermeticity-cycle-27.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-2026-08-29-01-validate-ci-hermetic-c27-eng.md
```
Not caused by this review — no `write`/`edit` tool was used this run, only `read`/`grep`/read-only
`bash` (`git show`, `git diff`, `shasum`, `git cat-file`, `git status`). `feature.json`'s diff is the
pin/cycle bookkeeping (`review_sha` → `4adb2219`, `cycles_used`/`max_total_cycles` → 27, one new run
record) from the concurrent `Feat43CiHermeticC27` eng-lead track; the two untracked files are its
Q11 answer and dev-ops receipt. None of the three files under my review scope are touched.
