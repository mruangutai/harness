```yaml
VERDICT: PASS
DIGEST:
  headline: >-
    factory_decompose's loosened tail_regex is NOT exploitable beyond privilege the caller
    already holds — ACCEPTABLE as shipped; two MED design gaps in the new writer (unvalidated
    tail_regex parameter, exact-string baseline collision that lets invalid JSON overwrite a
    matching-corrupt base) are real but unreachable through today's four production callers.
  factory_decompose_exploitable: "NO — requires filesystem write + working gh auth + an
    approved plan the caller already controls; grants no privilege beyond what invoking Bash
    already provides, and is a net tightening vs. factory_decompose's own pre-diff state
    (zero destination check -> basename check)."
  in_scope: true
  scope_reason: >-
    New locked writer (feature_json_write.py) is the sole read-modify-write path for
    feature.json across three callers; a loosened destination check and a monotonic-ratchet
    validator are exactly the injection/tampering-shaped surface this role audits, per dispatch.
  severity_max: med
  findings: 5
  must_fix: []
  threat_model:
    - boundary: "CLI positional (factory_decompose.py feature_dir) -> feature.json write location"
      stride: T
      mitigated: true
    - boundary: "write_feature_json's caller-supplied tail_regex parameter"
      stride: T
      mitigated: false
    - boundary: "monotonic non-regression baseline (exact problem-string comparison)"
      stride: T
      mitigated: false
    - boundary: "require_destination's realpath resolution outside the lock (TOCTOU)"
      stride: T
      mitigated: true
    - boundary: "S2 OMP hook advisory text"
      stride: I
      mitigated: true
  open_questions:
    - id: Q1
      question: >-
        DEC-199's "exactly four consumers" is stale: 5 production write_feature_json call
        sites exist (factory_decompose.py x1, feature-json-merge.py x1, gh-sync.py x3), not
        four, and dispatch background states six. Which count is authoritative, and does the
        decision need amending? (decision-accuracy, not a security defect — routed here per
        O-05, not this role's call.)
      blocking: false
    - id: Q2
      question: >-
        Should require_destination (or write_feature_json) enforce the "basename is literally
        feature.json" invariant unconditionally, independent of any caller-supplied
        tail_regex, so the core owns that one floor instead of delegating it entirely to
        caller discipline? See Finding B.
      blocking: false
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-1030-stale-anchor-write-hazard/notes/review-harness-security-reviewer-c0.md
```

# Security review — BUG-1030-stale-anchor-write-hazard (review-c0)

Diff `6d6d1cea..83282dea`, worktree
`.claude/worktrees/harness/BUG-1030-stale-anchor-write-hazard`. Read-only per DEC-174; no
source touched. All Python claims below were checked against a throwaway repro run under
`/tmp/sec1030` (left in place — `rm` on it was refused by my own read-only guard, harmless).

## The primary question — is `factory_decompose`'s loosening exploitable?

**No, not beyond privilege the caller already holds.** [reasoned+executed]

- `factory_decompose.py:326-333` — `feat_dir = args.feature_dir` is a raw CLI positional, not
  derived from `plan.yaml`'s `feature:` key (that field is `feat_id`, used only as a GitHub
  label — **executed**: read `_main`, confirmed `feat_id = plan.get("feature")` never touches
  path construction). The dispatch's "crafted feature id" framing is a false lead for this
  file; the only lever is the positional itself.
- `factory_decompose.py:155` — `FEATURE_JSON_BASENAME_TAIL = re.compile(r"(?:^|/)feature\.json$")`
  matches any resolved absolute path ending in `feature.json` — **executed**, confirmed by
  regex test. `write_factory` (`:224`) passes this to `write_feature_json`, so
  `require_destination` (harness_merge.py:158-171) accepts `factory_decompose.py /tmp/anywhere
  --repo owner/name --parent 1` and writes `/tmp/anywhere/feature.json`, given a
  `plan.yaml` there with `approval.status: approved` and a `feature:` key.
- But: (1) **executed** — read the full `bash-write-guard.sh` pattern set (lines 405-573):
  the only recognized write shapes are redirects, `sed`/`perl`/`awk` in-place, `tee`, `mv`/
  `cp`, `rm`, `sponge`, and git worktree/HEAD moves. A `python3 factory_decompose.py <path>`
  invocation is invisible to it entirely, with or without this diff — a governed agent that
  can run *any* local Python helper via Bash already has an unguarded write channel (the
  guard's own docstring: "Unparseable commands pass ... the post-run tree audit then
  catches"). Nothing here grants NEW capability. (2) **reasoned** from `_main`'s step order
  (`:349-396`): the first local write happens only *after* `plan.get("feature")` validates,
  `factory_gh.preflight()` (real `gh auth status`) succeeds, and `ensure_labels`/board reads
  against a real, fleet-configured repo succeed — a much heavier bar than "point it anywhere."
  (3) the write is confined to a file literally named `feature.json` holding schema-validated
  JSON built entirely from `factory_decompose`'s own internal `factory` dict — no
  attacker-arbitrary bytes, no code execution.
- **Relative to `factory_decompose.py`'s own pre-diff state this is a net tightening, not a
  loosening**: `test-factory-decompose.py:311-316`'s own comment states "a bare tempdir passed
  a feature.json worked only because write_factory carried no destination check at all before
  this feature." The "med, by reasoning" rating in the analysis note compares against
  `gh-sync`'s stricter tail, not against what this file itself was.

**Verdict: acceptable as shipped.** No fix required; see Finding B for a real, if
currently-latent, sharpening this deserves anyway.

## Findings

**A — Finding B (MED, reasoned).** `feature_json_write.py:84` — `write_feature_json`'s new
`tail_regex` parameter is accepted with zero validation in `require_destination`
(harness_merge.py:158-171: bare `tail_regex.search(resolved)`). Nothing requires a supplied
regex to even pin the literal filename `feature.json`. Today's two callers
(`FEATURE_JSON_TAIL`, `FEATURE_JSON_BASENAME_TAIL`) both do, so there is no live exploit — but
the module's *one* stated invariant ("this tool only writes feature.json") is entirely
caller-administered, not core-enforced, for a brand-new file whose whole purpose is to be the
one trusted gate. **Alternative:** assert the resolved basename equals `feature.json`
unconditionally inside `require_destination`'s caller (or a fixed check in
`write_feature_json` itself), on top of whatever directory-shape `tail_regex` a caller
supplies — path *shape* stays caller policy, filename does not.

**B — Finding C (MED, executed).** `feature_json_write.py`'s monotonic-non-regression
baseline (`_baseline_problems`/`_transform`, `:145-176`) compares problem strings by exact
text, including the embedded `json.JSONDecodeError` message. Two genuinely different
malformed JSON payloads that share an invalid prefix produce byte-identical
`"<path>: not valid JSON: <msg>"` strings:
```
>>> json.loads("{ x totally different junk AAAAAAAA")   # ValueError at char 2
>>> json.loads("{ x completely other junk BBBBBBBBBBBBBBBBBBBB more")  # same char 2
# both: "Expecting property name enclosed in double quotes: line 1 column 3 (char 2)"
```
Repro against the real module (`/tmp/sec1030`, executed): a base file holding the first string,
`write_feature_json(path, lambda base: SECOND_STRING)` — **the write succeeds, no
`MergeRefusal`, and the file now holds `SECOND_STRING`**, genuinely invalid JSON, on disk.
This directly falsifies the module's own docstring claim (`feature_json_write.py:105-108`):
"a write that would corrupt a SCHEMA-CLEAN document (**or produce invalid JSON at all, from
any base**) is refused." That is false whenever the base is *already* invalid JSON with a
matching parse-error position — trivial to construct, not a crafted edge case.
**Not reachable today**: all 4 production callers build their candidate text from
`json.loads(base.decode(...))` themselves (`gh-sync.py` `_record_status`/`_record_pr`/
`save_recorded`; `factory_decompose.py` `write_factory`'s inner `transform`,
`:211`) or via `feature_json_write.parse_doc` (`feature-json-merge.py:28`) — both raise before
ever handing `write_feature_json` a malformed candidate, so an unparseable base crashes the
caller's own transform first, every time — **executed**: read all four transform bodies to
confirm. **Alternative:** compare by category (an `is_valid_json` boolean plus, for schema
problems, `(pointer, validator)` pairs) instead of the raw exception/message text, so two
independently-broken documents can never be conflated by coincidence.

**C — Finding D (LOW/info, reasoned).** `require_destination`'s tail-regex match runs against
the fully-resolved path with no anchor to the invoking checkout — a resolved destination
landing inside a *different* harness worktree/clone on the same machine
(`/other/checkout/.harness/features/FEAT-x/feature.json`) satisfies the same regex.
Realpath normalization is sufficient to stop a `..`-bearing argument or a symlink from
*disguising* an out-of-tree destination as legitimate; it does **not** confine writes to the
tree the caller is actually working in. This is inherited unchanged from `require_destination`
(pre-existing in `harness_merge.py`, already shared by `plan-merge.py`/`observations-merge.py`
before this diff — not introduced here), but this feature is the first to route feature.json,
a schema/board-authoritative document, through it. Same exploitability floor as Finding A
(needs pre-existing local write capability); rate info given no root-anchoring exists anywhere
in this family of tools today.

**D — Finding E (info, reasoned).** `harness_merge.locked_update` (`:120-145`) takes the flock
before reading, transforming, validating, and `os.replace`-ing — every check that matters runs
under one continuous hold, confirmed by reading the function body directly. The one operation
outside the lock is `require_destination`'s single `os.path.realpath` call
(`feature_json_write.py:170-172`, ahead of `locked_update`). A symlink-component swap in the
window between that resolve and the lock's own open would need local race capability at least
equal to Finding A's precondition — pre-existing to `require_destination`, not new here.
**Positive confirmation**: `gh-sync.py`'s `_record_status`/`_record_pr` transforms now
re-decode `base` fresh *inside* the lock rather than reusing their pre-lock read (diff comment:
"Re-read under the lock rather than reusing `doc`") — this correctly closes the exact
read-then-clobber race the feature exists to fix. Confirmed by reading the diff; no gap.

**E — S2 advisory (clean).** `.omp/extensions/harness-hooks.ts:830-846` — the appended notice
is a fixed literal string ("Harness: no target path could be extracted from this edit...")
with no interpolated path, file content, or stack trace. **Executed**: read the code directly;
no string formatting of any variable feeds the advisory text. No data exposure.

## Standard sweep (executed)

- **Secrets**: grepped all 17 changed files plus the new backend-dev receipts for
  key/token/password/PEM-shaped strings. None found.
- **Injection**: `gh-sync.py`'s `subprocess.run([GH] + args, ...)` call sites are unchanged by
  this diff (confirmed by reading the diff hunks — only the `feature.json` write path changed);
  all list-form argv, no `shell=True`, no string-built shell commands anywhere in the touched
  files.
- **Authorization** (`feature-json-merge.py`'s new `set-key`/`set-github`/`append-run`, allows
  any top-level key including `status`/`review_sha`/`pr` with no allowlist) — **assessed and
  dismissed**: this is the identity/authorization gap `harness_merge.py`'s own module
  docstring already discloses and defers ("This core has NO identity source ... reachable from
  a read-only persona ... That gap is issue #627 and is not fixed here."). Not introduced by
  this diff, and strictly safer than the raw-text hand-edit it replaces (schema-checked
  instead of unchecked).

## Disclosed residuals — confirmed/refuted

- `factory_decompose` loosening: **confirmed present, refuted as exploitable** — see above.
- Realpath "normalizes rather than prevents": **confirmed** — see Finding D; sufficient for
  the stated threat (disguised traversal), not for cross-checkout confinement.
- Lock/atomic-replace TOCTOU: **confirmed correct** for the read-modify-write itself; **one
  narrow, pre-existing, low-severity window** at the pre-lock realpath resolve — see Finding E.
- Baseline widening from a hostile/unparseable base: **confirmed possible in the library,
  refuted as reachable today** — see Finding C; this is the strongest finding in this review
  and the one worth fixing regardless of current unreachability, since it sits inside brand-new
  enforcement-layer code whose entire job is to be trusted.
