# Security review — BUG-440 digest/verdict reconciliation (review_sha 2964cddb)

## BLUF
Read-only local state-gate addition; no meaningful attack surface beyond a low-severity
output-spoofing gap in the new finding message's path/name interpolation (not the token
interpolation, which is already hardened). No ReDoS, no path traversal, no write, no
secrets in the four corrected `feature.json` records. `severity_max: low`, nothing gates.

## Scope established
Base for the two target files: `27507695` (immediate parent touching either file per
`git log -- check-state.sh test-check-state.py`). Feature commits: `3722a2c3` (logic +
four `feature.json` corrections) and `2964cddb` (pinned sha; test-only reuse, no
behavior change — `git show --stat 2964cddb` is 4 deletions in the test file only).
Full diff for the two code files verified at `check-state.sh:601-608`, `:650-658`,
`:1526-1557`; test at `test-check-state.py:4618-4712`.

## 1. Untrusted-input parsing / ReDoS — no finding
`^\s*VERDICT:` and `^\s*VERDICT:\s*(\S+)` (`check-state.sh:1541,1544`) are anchored,
single-quantifier patterns (`\s*`, `\S+` over a negated class) with no nested or
ambiguous quantifier composition — linear in input size, not exponential-backtracking
candidates. `list(re.finditer(...))` (`:1541`) materializes one match per line-start
`VERDICT:` occurrence, bounded by file size — and the whole file is already fully
`.read()` into `_dtext` and passed through `_vd_mod.validate()` one line earlier
(`:1530-1531`), a cost this diff did not introduce (the prior code did
`_vd_mod.validate("lead", open(dg,...).read())` in one expression — same read, same
memory footprint). No new DoS surface. The comment at `:1540` binds this regex pair to
`validate-digest.py:1155-1160` byte-for-byte — confirmed identical: same tail-anchor
finditer, same take-last, same `re.search` capture (`validate-digest.py:1153-1160`).
Confirmed live by the new test itself, which builds a digest with tail-anchored VERDICT
and non-tail junk and asserts `validator.validate("lead", text) == []` — same code path.

## 2. Data exposure / output-format spoofing — low finding
The new message (`check-state.sh:1551-1557`):
```
f"INV-37: {os.path.basename(_feat_dir)} run {_rid}: "
f"digest verdict {_dm.group(1)!r} in {os.path.relpath(dg, H)} differs from "
f"feature.json verdict {_rv!r} in {os.path.relpath(os.path.join(_feat_dir,'feature.json'), H)}; ..."
```
The two attacker-shaped **value** tokens are `!r`-quoted: `_dm.group(1)` (the digest's
tail VERDICT capture — bounded to `\S+`, so no embedded newline, but can contain other
non-whitespace control bytes e.g. ESC `\x1b`) and `_rv` (the `feature.json` verdict,
confirmed by the dispatch to be an unbounded `str()` of arbitrary YAML). `repr()`
escapes non-printable/control characters into backslash sequences, so `!r` is
**sufficient** for these two — a crafted `verdict: "\x1b[31mFAKE"` in `feature.json`
prints as the literal 12-character sequence `'\x1b[31mFAKE'`, not a raw escape, and
cannot introduce a newline (no whitespace is `\S`-matchable... but ESC is not `\s`
either — repr still neutralizes it either way).

The **name/path** components are *not* wrapped in `!r`: `os.path.basename(_feat_dir)`,
`_rid` (`os.path.basename(rundir)`), and the two `os.path.relpath(...)` results. All
four are directory-name-derived, and directory names are POSIX-legal to contain a
literal newline (only `/` and NUL are forbidden). Findings are printed one-per-line with
no per-message escaping: `for m in bad: print(f"  VIOLATION  {m}")` (`check-state.sh:2504`).
A `runs/<id>/` or `features/<feat>/` directory named with an embedded
`\n  VIOLATION  <forged text>` would break out of the single-line format and inject an
indistinguishable extra finding line, or corrupt an automated consumer that greps
`^  VIOLATION` per output line. **This is a pre-existing pattern across the whole file**
— every other `bad.append(f"{feat}: ...")` / `f"{_run_rel}: ..."` call (e.g.
`:622,1490,1497` in the INV-36 block just above) interpolates the same unescaped
name/path components; this diff's authors actually improved on that convention by
`!r`-quoting the two genuinely-adversarial value tokens and left the file's existing
name/path convention unchanged rather than widening it. Exploiting it requires local
filesystem write access to create a maliciously-named directory under
`.harness/<repo>/features/**` — the same privilege level the dispatch already assumes
for forging a `feature.json` verdict, so no privilege escalation (P-02). Rating: **low**,
advisory — worth a follow-up to `!r`-quote name/path components repo-wide, out of this
diff's scope.

## 3. Path handling — no finding
`dg = os.path.join(rundir, "digest.md")` and `os.path.join(_feat_dir, 'feature.json')`
are always built from `rundir`/`_feat_dir`, which are themselves `os.path.dirname(...)`
of glob matches templated as `os.path.join(H, "*", "features", "*", "runs", "*", ...)`
(`check-state.sh:1479`, `:1526`) — every match is syntactically rooted under `H`, so
`os.path.relpath(dg, H)` can never contain `..`; there is no attacker-controlled
component that reaches the glob's fixed literal segments. `os.path.basename()` on
either side strips any embedded `/`, so no cross-directory reference is possible via
the name itself (only literal newlines/control bytes survive, per §2). Symlinked run
directories following through `open()` is a pre-existing property of the whole file
(the pre-diff code already did `open(dg,...).read()` for validation) and requires the
same local-write precondition as §2 — not new, not escalated.

## 4. Integrity / STRIDE tampering
**Writes:** none. The new test itself proves this: it hashes `feature.json` and every
`digest.md` before and after running the check and asserts `before == after`
(`test-check-state.py:4682-4685`), which the `case_bug440_...` function's return
condition (`mixed_ok`) requires to pass.

**Can the comparison be silenced by tree shape?**
- Runs never claimed by any `feature.json` entry are, by the approved contract itself,
  outside the compared intersection — `if _rid in _recorded:` (`:1548`) simply does not
  fire, matching the brief's stated scope (`its run id is claimed by a feature.json
  runs[] entry`). Not a suppression bug; it is the specified boundary (D-04/D-07), and
  a run with no claiming entry was never checked by any invariant before this feature
  either.
- Duplicate `runs[]` ids for the same run (D-07's live case, `FEAT-45`) cannot be used
  to launder a bad digest: the loop iterates **every distinct recorded value**
  (`dict.fromkeys(_recorded[_rid])`, `:1554`) and appends one finding per differing
  value. Adding a second, digest-matching duplicate entry does not suppress the finding
  against the original, still-differing entry — an attacker would have to overwrite the
  original entry itself, which is direct `feature.json` tampering equal in privilege to
  what the check is designed to catch, not a bypass of the check via shape alone. This
  is a genuinely attack-resistant property of the D-07 design, worth recording as a
  positive.
- Keying `run_verdicts` on the feature **directory path** (`os.path.dirname(fy)` at
  `:654`, matched against `_feat_dir = os.path.dirname(os.path.dirname(rundir))` at
  `:1550`) rather than bare feature name prevents cross-repo collision as D-04 states —
  confirmed both glob templates share the same `H`-rooted prefix shape, so the keys are
  produced consistently.
- The `run_verdicts` build sits directly beside the unconditioned `runs.append(...)`
  (`:654-656`), not inside any `_squad == "validator"` branch — confirmed, matching
  D-04/D-07 and PF-b884d6ee.

## 5. Four corrected `feature.json` records — no finding
All four diffs in `3722a2c3` are plain enum-token swaps with no secret-shaped or
credential-shaped content:
- `FEAT-07-verify-teeth-batch-probe/feature.json`: `"FAIL"` → `"ESCALATE"`
- `FEAT-22-docs-layout-migration/feature.json`: `"INCOMPLETE"` → `"PASS"` (×2)
- `FEAT-25-claim-feature-root/feature.json`: `"PASS"` → `"FAIL"`
- `BUG-440-digest-verdict-reconciliation/feature.json`: adds a `github` block
  (`milestone`, `parent`, `attached`, `issues`, `source_issues` — all public issue/PR
  numbers), no verdict correction.
No secrets, tokens, or unrelated payload in any of the four.

## Threat model
| boundary | STRIDE | mitigated |
|---|---|---|
| digest.md text (agent-authored, read by check-state.sh) | Tampering/Spoofing | true — tail-anchor semantics match validate-digest.py byte-for-byte; VERDICT token pre-constrained to enum by `validate()` before INV-37 runs |
| feature.json `runs[].verdict` (unbounded str) | Information disclosure / output spoofing | true for the value itself (`!r`) |
| feature.json/run-directory names in the new message | Information disclosure / output spoofing | false — unescaped, pre-existing file-wide convention, low severity, local-write precondition only |
| gate write surface | Tampering | true — proven no-write by hash-equality test |
| tree-shape suppression (duplicate ids, unclaimed runs) | Repudiation | true — duplicate-id case is attack-resistant by design (D-07); unclaimed-run case is in-scope-by-contract, not a suppression |

## Open questions
None blocking.

## Verdict
`PASS`, `severity_max: low`. No `must_fix`.
