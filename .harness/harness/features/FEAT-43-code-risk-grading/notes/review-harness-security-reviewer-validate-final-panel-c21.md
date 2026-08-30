# Security review — FEAT-43-code-risk-grading — validate-final-panel-c21

Pin `17106762c5`, range `7ccfae8dd7644bc3aaea612dabf4317c0d804f99..17106762c588b3d1c0df45efbcb6128604efb185`.

## SEC-01: CLOSED as a class

Range-independence demonstrated by construction. Every forged `code_grade: n_a` digest below —
Q8's three enumerated shapes plus five of my own invention — was refused at exit 1 with the
**identical** message (`"code_grade='n_a' is only valid when the reviewed diff has no Python
file."`), because the decision now comes from `merge-base(origin/HEAD, review_sha)..review_sha`,
never from the digest's own `reviewed:` string. Commands run in this worktree, all via
`python3 .claude/skills/harness/bin/validate-digest.py harness-code-reviewer <file>`:

| Shape | `reviewed` (digest-claimed) | exit |
|---|---|---|
| Q8-A `pin..pin` | `17106762..17106762` | **1** |
| Q8-B `pin~1..pin` | `34a49c4..17106762` | **1** |
| Q8-C honest base | `7ccfae8d..17106762` | **1** |
| mine: no-`.py` descendant pair ending at pin | `1171202..17106762` (a post-pin bookkeeping commit whose diff to the pin has zero `.py` paths — confirmed via `git diff --name-only`) | **1** |
| mine: tag-spelled head | `34a49c4..archive/worktree-wt140-273-g1710676` (tag resolves to the pin) | **1** |
| mine: abbreviated head | `7ccfae8d..1710676` | **1** |
| mine: `^{commit}`-peeled head | `7ccfae8d..17106762^{commit}` | **1** |
| Q8-D (control): `code_grade: fail` over the forged no-op range, `VERDICT: FAIL` | `17106762..17106762` | **0** — `digest ok` |

The control row is the load-bearing negative case, not a bypass: `fail`/`pass`/`grade_2` are
deliberately ungated on base derivation (Q8), and the ungated direction only lets a reviewer
*over-report* a broken build, never buy a false clean. (My first attempt at this row used
`VERDICT: PASS`, which correctly failed for the unrelated pass/fail-consistency rule — re-ran with
`VERDICT: FAIL` to isolate the SEC-01 property alone.)

**mine: cross-feature artifact hijack** — `artifact:` pointed at
`FEAT-19-central-product-config/notes/…` (a real, already-shipped feature with `branch: none`,
`review_sha: 63b83c7`) with `reviewed: "7ccfae8d..63b83c7"`. Refused at exit 1, but for a
*different* reason: `review_sha (63b83c7) is already an ancestor of the default branch` — FEAT-19
is merged, so its derived range is degenerate and Q8's third fail-closed clause catches it. This
is not incidental luck (`git merge-base --is-ancestor 63b83c7 origin/main` confirms), but it also
does not structurally close the hole — see Q5 below.

## Binding-subsystem audit (`validate-digest.py`, ~330 new lines)

- **Fail-open paths: none found.** Traced every branch of `_derived_reviewed_python_change`,
  `_default_branch_or_none`, `_merge_base_or_none`: every failure (`origin/HEAD` unresolvable,
  `review_sha` unresolvable, no merge base, degenerate range) returns `(None, <error>)`, and every
  caller `err.append`s it — never proceeds to grant `n_a`. Confirmed live (table above).
- **Git argument injection: ruled out**, same mechanism cycle-13 already cleared. `_merge_base_or_none`'s
  two args are `origin/HEAD`'s own symbolic-ref output (always `refs/…`) and an already-resolved
  40-char OID from `commit_oid` (`code_grade.py:286-288` rejects any leading `-` before it ever
  reaches `git`, and pins via `--end-of-options … ^{commit}`) — no raw digest text reaches `git`
  as an argument.
- **Path traversal in `artifact:` — low, not exploitable today.** `FEATURE_DIR_IN_ARTIFACT_RE`
  (`[^/\s]+` per segment) syntactically accepts a literal `..` segment
  (`.harness/../features/whatever/…`), which `os.path.join` will walk up one level. Reproduced:
  resolves to `<root>/features/whatever/feature.json`, which doesn't exist, so `_read_review_sha`
  fails closed (`could not be read`, exit 1) — same outcome as any bogus path. It grants no
  capability beyond what a reviewer already has by choosing any other segment name, and a
  `harness-code-reviewer` has no `Write` scope outside its own report/Expertise, so it can't plant
  a target file to land on. Worth tightening the regex to exclude bare `..` segments as hygiene,
  not a blocker.
- **TOCTOU: theoretical only.** `feature.json` is read twice per `n_a` validation — once inside
  `code_grade_bound_to_review`, once inside `resolve_review_sha` (same root cause as the duplicate
  error below). A concurrent writer between the two reads is the only way to diverge them; this is
  a single local process with no privilege boundary between the invoking user and the checkout —
  consistent with cycle-13's ruling on this file's trust model. Info, not a finding.

## Scepticism point 3 (Q5) — measured, not assumed

Measured (not the dispatch's "42"): **40** `feature.json` files in this worktree. **4** carry
`branch: none` (FEAT-01, FEAT-15, FEAT-19, FEAT-28) — the only population where
`_branch_corroboration_error` has nothing to corroborate against, so the artifact-hijack shape
above is live *in principle* for any of them. Checked all four: FEAT-15 and FEAT-28 have
`review_sha: none` (unpinned, `_read_review_sha` refuses immediately); FEAT-01's `review_sha` is a
malformed `a606d7a..9b07cfc` range (never resolves as a single commit); FEAT-19's is real but
already merged (degenerate, refused as shown above). **Zero of the four are exploitable at this
pin, in this repo state.**

This is not a structural closure, though — it is inventory. The design gap is real: a
`branch: none` feature that is (a) validly pinned, (b) not yet merged to the default branch, and
(c) whose own diff happens to touch no `.py` file would let any *other* feature's reviewer borrow
its `review_sha` as a free `n_a` token by pointing `artifact:` at its notes path. `branch: none`
is a legitimate, recorded state (not a bug), so this population is not going away.
**Severity: med** — a genuine self-attested "which feature" hole with a describable attacker and
gain (a careless/compromised reviewer digest, not "this could be insecure" speculation), gated by
preconditions not currently satisfied by any live feature. **Does not gate this review**: SEC-01's
mandate was closing the digest-chosen-range bypass, which the range-independence table above
closes completely; Q5 is explicitly framed as non-gating in `STATE.md`, and I concur — recommend
it as a backlog row (e.g., require donor `review_sha` to resolve at all only when its feature's
own status is terminal/shipped, or extend corroboration to also check the target feature isn't
`in_progress`/`review`).

## Scepticism point 4 — duplicate binding error, confirmed

`artifact: none` + `code_grade: n_a` prints the identical
`"code_grade cannot be bound to review_sha: artifact 'none' does not name a …"` line **twice**
(reproduced, exit 1). Root cause: `code_grade_bound_to_review` and, separately,
`resolve_review_sha` (reached only for `code_grade == "n_a"`) each independently call
`_resolve_feature_dir` on the same digest text — two call paths into one producing site, no
dedup. **Severity: info.** No security consequence: both prints carry byte-identical, templated
content (the only variable is `path!r`, Python's `repr()`, not raw attacker text — no ANSI/log
injection surface), and this file's own error paths already fail closed regardless of how many
times the refusal is printed. Purely cosmetic; backlog, not a blocker.

## Rest of the diff

Files touched: 5 Python source files (`check-plan-routes.py`, `code-grade.py`, `code_grade.py`,
`gate_policy.py`, `validate-digest.py`), 5 Python test files, 2 shell/skill/agent doc sets, and
this feature's own state/notes. Scanned the full diff for `shell=True`, `eval(`, `exec(`,
`pickle`, `os.system`, and for token/secret/password/api_key/getenv/environ strings: no
production-code hits. The one `os.environ` use (`test-code-grade-cli.py:125`) builds a `PATH`
override for a test fixture that wraps `git` to assert on its invoked arguments — a test tool, not
a leak. No new command-injection or credential-exposure surface found beyond what cycle-13 already
cleared (§5/§6 of the cycle-13 note, unchanged by this pin's diff).

## Verdict

SEC-01 CLOSED as a class — range-independence held under every shape tried, including five this
panel invented that Q8 did not enumerate. `must_fix` empty; highest severity found is `med` (Q5,
non-gating by the ruling above, backlog-worthy). PASS.

```yaml
VERDICT: PASS
DIGEST:
  headline: "SEC-01 closed as a class — 8 forged reviewed-range shapes (3 Q8-enumerated, 5 invented) refused n_a identically; residual cross-feature artifact-hijack (Q5) is real but unexploitable today, ranked med, non-gating"
  in_scope: true
  scope_reason: "diff adds ~330 lines to validate-digest.py's own trust-boundary code (review binding, git ref resolution, cross-feature corroboration) plus the code_grade.py/code-grade.py gate this feature ships"
  severity_max: med
  findings: 4
  must_fix: []
  threat_model:
    - { boundary: "digest-claimed reviewed range vs system-of-record review_sha", stride: "T", mitigated: true }
    - { boundary: "which feature.json a digest's artifact: line resolves to (branch:none population)", stride: "S", mitigated: false }
    - { boundary: "artifact: path segment traversal (FEATURE_DIR_IN_ARTIFACT_RE allows '..')", stride: "T", mitigated: true }
    - { boundary: "git ref/argument construction in _merge_base_or_none / commit_oid", stride: "T", mitigated: true }
  open_questions:
    - { id: Q1, question: "Q5's residual cross-feature branch:none hijack — accept as backlog (as this review recommends), or require closure before further features add branch:none records?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-43-code-risk-grading/notes/review-harness-security-reviewer-validate-final-panel-c21.md
```
