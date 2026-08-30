# Security review — FEAT-43-code-risk-grading — validate-final-panel (re-dispatch)

Pin: `94383e671e51f95d142f3220f97c8e453721d516`. Range:
`7ccfae8dd7644bc3aaea612dabf4317c0d804f99..94383e671e51f95d142f3220f97c8e453721d516`.

## 1. Finding — `code_grade: n_a` is a self-attested claim never bound to `review_sha`

**Severity: high.**

**Who / what / gain.** Any agent (or a compromised/careless one) filling the
`harness-code-reviewer` DIGEST controls the `reviewed:` field itself. `validate-digest.py`
never cross-checks that field against `feature.json`'s `review_sha` — the value the rest of the
system (`check-state.sh` INV-6) treats as the actual pin. A reviewer that reports a same-commit,
zero-diff `reviewed:` range gets `code_grade: n_a` accepted unconditionally, regardless of how
much real Python changed in the feature. The gain: bypass the project's only code-risk gate on
a merge that would otherwise fail it (this feature's own diff currently fails it — see the
dispatch's own reproduction: 21/98 below bar).

**Code path (pin):**
- `validate-digest.py:549-567` `reviewed_python_change(reviewed)` computes "did Python
  change" **exclusively** from the digest's self-reported `reviewed:` string — `git diff
  --name-only` between whatever two revisions that string names (line 566).
- `validate-digest.py:541-546` `resolve_reviewed_commit` and the `reviewed_python_change`
  call at `:764-771` are the *entire* mechanism gating `n_a`. Nowhere in this file, in
  `check-state.sh` (verified: `grep reviewed\b` → no matches), or in `check-domain.sh`
  (same, no matches) is `reviewed:` ever compared to `feature.json`'s `review_sha`. They are
  two disconnected fields; `review_sha`'s own INV-6 (`check-state.sh:245-252`) only asserts
  it is *non-placeholder*, never that it equals what a reviewer actually diffed.
- Consequence at `validate-digest.py:766-771`: `code_grade == "n_a"` is accepted whenever
  `reviewed_python_change` returns `False` for *whatever range the digest names* — there is no
  requirement that the range be the feature's real range.

**Live reproduction, at this pin, in this worktree** (forged digest, all other required
fields present and legal):

```yaml
VERDICT: PASS
DIGEST:
  headline: forged clean review
  code_grade: n_a
  reviewed: "94383e671e51f95d142f3220f97c8e453721d516..94383e671e51f95d142f3220f97c8e453721d516"
  grade_2_reasons: []
  findings: 0
  must_fix: []
  severity_max: none
  files_touched: []
  open_questions: []
  expertise_update: []
artifact: none
```

```
$ python3 .claude/skills/harness/bin/validate-digest.py harness-code-reviewer /tmp/forged_digest.md
digest ok
$ echo $?
0
```

Same pinned commit used as both base and head — a "resolvable no-op range" per the dispatch's
own framing — produces an empty diff, no `.py` path, `n_a` accepted, exit 0. This is the exact
review_sha of this run; a real reviewer facing the six grade-3 production FAILs (`gate_policy.py`,
`code_grade.py`, etc.) that the panel already confirmed fail this feature's own bar can ship an
`n_a` claim and clear validation instead.

**Impact.** The gate this entire feature exists to add — "the tool must pass its own bar"
(T-01's stated intent) — is enforced only if the reviewer *chooses* to name an honest range.
Nothing downstream verifies the claim against the system of record. What ships as a result: a
feature (this one, concretely) whose own `code_grade.py`/`code-grade.py` contain two grade-3
production functions below the panel's already-confirmed bar can be waved through as
`code_grade: n_a`/`pass` with no mechanical contradiction raised anywhere in the pipeline.

## 2. This is the shipped happy path, not an edge case

`test-validate-digest.py:1709-1711` — the shared `reviewer_digest()` fixture used by every
reviewer-schema test in the suite defaults `reviewed` to
`f"{PRE_FEATURE_REVISION}..{PRE_FEATURE_REVISION}"` (`PRE_FEATURE_REVISION` defined at
`test-validate-digest.py:20`) — a same-commit, zero-diff range, structurally identical to the
forged digest above.

`test-validate-digest.py:1786` asserts exactly this default-shape call must be **accepted**:
```
if validator.validate("harness-code-reviewer", reviewer_digest("n_a"), config):
    failures.append("n_a with no reviewed Python diff must accept")
```
The test suite's own affirmative contract is "a same-commit range yielding `n_a` passes
validation" — it never asserts that range equals the feature's `review_sha`. The adjacent case
at `:1783-1784` (`reviewer_digest("n_a", reviewed=python_diff)`) only proves the negative
direction (a range that *does* touch Python is rejected); it does not close this gap because an
attacker/careless-reviewer is free to pick a range that touches nothing, which is the entire
bypass. The option-injection cases at `:1789-1793` are a different, already-mitigated concern
(see §5) and do not touch this one either.

## 3. Recommended remediation (concrete, not implemented)

Bind the diffed range to the system of record before an `n_a`/`code_grade` claim is trusted, not
to the digest's self-report:
- In `validate()`'s `harness-code-reviewer` branch (`validate-digest.py:764`), read the
  feature's `review_sha` from `feature.json` (the same value INV-6 already enforces is pinned)
  and require `reviewed`'s `head` to resolve (via the existing `commit_oid`/
  `resolve_reviewed_commit`) to the **same commit OID** as `review_sha`. Reject the digest
  (append to `err`) if they diverge, with the same "range could not be resolved" style message
  already used for the other range failures at `:769-771`.
  - `base` has no independent system-of-record value today; at minimum pin `head`, since that
    is what actually varies between a real review and a forged no-op one.
- Do this validation unconditionally (before branching on `code_grade`'s value), not only when
  `code_grade == "n_a"` — a forged `reviewed:` also lets a `pass`/`fail`/`grade_2` claim describe
  a diff that was never actually reviewed.
- Update `test-validate-digest.py:1709-1793` (and the shared fixture default) so the fixture's
  default `reviewed` is derived from a real `review_sha` fixture value rather than a
  self-consistent no-op pair, so the suite cannot keep asserting the bypass shape as the happy
  path.

## 4. Fail-open / fail-closed classification — every `except` in the changed Python

**`code_grade.py`** — **zero `except` clauses** (confirmed: `grep except` → no matches).
Every error (`ast.parse` `SyntaxError`, `subprocess` failures, `commit_oid`'s `ValueError`)
propagates uncaught to the caller. Classification: **fail-closed by construction** (nothing here
swallows an error into a false success).

**`code-grade.py`** (CLI):
| Line | Catches | Behavior | Class |
|---|---|---|---|
| `:38-40` `_relative` | `ValueError` | re-raises as `ValueError("path outside repository…")` | fail-closed |
| `:71-74` `_paths_report` | `(OSError, SyntaxError)` | prints `PARSE ERROR`, appends to `ungraded` | fail-closed — `_status:151-153` returns **3** whenever `ungraded` is non-empty, distinct from a clean 0 |
| `:107-110` `_diff_report` pre-image loop | `(SyntaxError, ValueError)` | same `ungraded` path | fail-closed (same `_status` rule) |
| `:166-167` `main` | `ValueError` | `parser.error(str(error))` → argparse exits 2 | fail-closed |

**`gate_policy.py`**:
| Line | Catches | Behavior | Class |
|---|---|---|---|
| `:37-39` | `(OSError, json.JSONDecodeError)` | raises `GatePolicyError` | fail-closed |
| `:41-43` | `(KeyError, TypeError)` | raises `GatePolicyError` | fail-closed |
| `:51-52` | `KeyError` | raises `GatePolicyError` | fail-closed — and `validate-digest.py`'s `hook_mode` (`:1080-1082`) turns a `GatePolicyError` into `return 2`, i.e. blocking |

**`validate-digest.py`** (reviewer-relevant + hook wrappers):
| Line | Catches | Behavior | Class |
|---|---|---|---|
| `:544-546` `resolve_reviewed_commit` | `ValueError` from `commit_oid` | returns `None` → `reviewed_python_change` turns that into a range error appended to `err` | fail-closed |
| `:870-872` (root resolution in artifact-file check) | `Exception` | returns `None` | fail-open (silent) — low stakes, only disables a file-shape check with an explicit downstream fallback comment |
| `:921-923` `check_artifact_file` | `Exception` around `validate()` | prints "our bug, not theirs", `return 0` | **fail-open by explicit design** — but this path validates a *lead's* `digest.md` artifact-file shape, not the reviewer branch itself |
| `:959-963` hook stdin parse | `Exception` | prints, `return 0` | fail-open by explicit design (malformed hook payload) |
| `:994-997`, `:1019-1022`, `:1038-1041`, `:1055-1058` (`inflight_registry` bookkeeping) | `Exception` | prints, continues / non-blocking | fail-open by explicit design — documented as "our gap, not theirs," unrelated to the reviewer contract |
| `:1079-1082` `hook_mode` | `GatePolicyError` | prints, `return 2` | **fail-closed** (blocks the SubagentStop hook) |
| `:1083-1086` `hook_mode` | `Exception` (catch-all around `validate()`) | prints "our bug, not theirs", `return 0` | **fail-open by explicit, extensively documented design** (`:1072-1077`) — this is the one path where an *unexpected* exception inside the reviewer's `reviewed_python_change`/`resolve_reviewed_commit` (e.g. a `FileNotFoundError` if `git` were unavailable — not currently reachable, since `commit_oid` only raises `ValueError`) would silently pass an unvalidated digest through. No live trigger found; noted for completeness, not asserted as exploitable today (info, not a finding) |
| `:1111-1113` (CLI stdout reconfigure) | `Exception` | `pass` | fail-open, cosmetic (encoding fallback only) |
| **Plain CLI path** (`:1116-1122`, no `--hook`) | *no wrapper at all* | an uncaught exception in `validate()` produces a Python traceback and the interpreter's default non-zero exit | fail-closed (crashes rather than silently passing), confirmed by reading the dispatch block directly |

**`check-plan-routes.py`**:
| Line | Catches | Behavior | Class |
|---|---|---|---|
| `:331-335` | `harness_yaml.YamlParseError` | prints, distinct exit path ("not a violation, the checker being unable to run") | fail-closed (surfaced, not silenced) |
| `:473-475` (`_is_frozen`-style helper) | `Exception` | returns `False` | fail-closed — `False` means "not exempt from routing checks," the conservative default per the function's own docstring |
| `:535-536` | `ValueError` | prints, `sys.exit(2)` | fail-closed |
| `:582-584` | `OSError` (scandir) | prints, `sys.exit(2)` | fail-closed |
| `:596-597` | `OSError` (`DirEntry.is_dir()`) | appends to `unreadable` (reported, not skipped) | fail-closed by design, per the inline comment: "silently skipping it would be the same lie" |
| `:691-692` `live_invariant_numbers` | `OSError` | returns `None`; caller (`:723-726`) emits an explicit `NOTE … SKIPPED` finding | **fail-open, but loudly announced** — documented in the docstring as deliberately avoiding "the same fail-open shape the check exists to catch" |
| `:743-744` (per-feature BRIEF/plan read in the collision scan) | `OSError` | `continue` — silently skips that one file for that one feature, no NOTE emitted for this narrower case | fail-open, silent, localized — lowest-severity item in this table: it only weakens an invariant-number-collision hygiene check, not a release gate |
| `:779-782`, `:789-792` | `ValueError` | prints, `sys.exit(2)` | fail-closed |

**Net:** every catch that touches an actual release/merge gate (`gate_policy.py`, the
`code_grade`/`ungraded` paths in `code-grade.py`, `hook_mode`'s `GatePolicyError` branch) is
fail-closed. The only fail-open paths are (a) explicitly documented "our bug, not theirs"
non-blocking behavior around the *validator's own* internal errors and inflight bookkeeping —
consistent, deliberate house style — and (b) the silent per-file skip in the invariant-collision
hygiene scan, which is cosmetic. None of these fail-open paths is the mechanism behind Finding
§1; §1 is a design gap (missing cross-check), not an exception-handling defect.

## 5. Command-injection surface — ruled out

**`--base`/`--head` cannot reach `git` as an option.** `code-grade.py:162-163` resolves both
through `code_grade.commit_oid` *before* either value is used in a `git diff` invocation.
`code_grade.py:281-284`: `commit_oid` raises `ValueError` immediately if
`revision.startswith("-")` — a value like `--upload-pack=…` or `--output=…` never reaches
`subprocess.run` at all — and additionally invokes `git rev-parse --verify --end-of-options
{revision}^{{commit}}`, so even a revision that only *contains* a leading dash inside a
non-first position is still resolved through `rev-parse`'s own option/revision boundary. The
same guard is exercised by `validate-digest.py:541-546`'s `resolve_reviewed_commit`, used by the
reviewer's `reviewed_python_change`. `test-validate-digest.py:1788-1793` exercises exactly this
(`"--no-patch..HEAD"`, `f"--output={output_path}..HEAD"`) and asserts rejection — confirmed
already covered by the shipped test suite, not a gap.

**`ast.parse` performs no execution.** Every use in the diff (`code_grade.py:274`,
`code-grade.py:107`, in `_body_hashes`) is standard-library AST parsing of source text into a
syntax tree; no `compile(..., exec)`, `eval`, or `exec` call appears anywhere in the changed
files (confirmed by direct read of `code_grade.py` and `code-grade.py` in full).

**Config/frontmatter loading uses a safe loader, not `yaml.safe_load` by name but equivalent in
effect.** `gate_policy.py:37` uses `json.load` (never a code-execution risk). YAML parsing goes
through `harness_yaml.py`'s single shared loader: `harness_yaml.py:223`
`yaml.load(text, Loader=_StrictSafeLoader)`, where `_StrictSafeLoader` (`:132`) subclasses
`CSafeLoader`/`SafeLoader` (`:129`), never the unsafe default `Loader`/`FullLoader` — confirmed
by reading the class definition. No arbitrary-object construction is possible through this path.

**Ruling: no command-injection or arbitrary-code-execution surface in this diff.** Severity: n/a
(nothing to report; both mechanisms checked and found sound).

## 6. Absolute-path / secret / identity leakage

Scanned every print/error string added in this diff (`git diff … | grep -niE
"print\(|token|secret|password|api_key|environ|getenv|abspath|home|realpath"`). Findings: none
carry credentials, tokens, environment values, or usernames. The only path-shaped output is
repo-relative or repo-internal (`MANIFEST {path}` in `check-plan-routes.py:147`, `PARSE ERROR:
{path}` in `code-grade.py:263,299`, `check-digest: {found}` in `validate-digest.py`) and in every
case the path either originates from the same local user's own CLI argument (echoed back, not a
disclosure across a trust boundary) or from within the checkout the tool is already running
against. `os.path.abspath(__file__)` (`validate-digest.py:872,894`) is used only to seed
`sys.path`/resolve the script's own directory; it is never printed. No `os.environ`/`getenv`
reads exist in the changed files. **Severity: info — no leakage found; these are local dev-CLI
tools with no privilege boundary between the invoking user and the paths reported.**

---

`must_fix`: §1 must be closed with a `review_sha` binding before `code_grade: n_a` (or any
`code_grade` value) can be trusted from a reviewer digest — the gate this feature exists to add
is currently satisfiable by any digest that names a convenient no-op range, and the test suite
enshrines that exact shape as the passing case.
