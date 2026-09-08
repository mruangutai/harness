# Security review — BUG-124-run-dir-squad-suffix — c4

review_sha: 6c037de463fd2b7be0c6ffa4df04ce801aac86e2 (diff base 80ce35d1)

## VERDICT: PASS — in scope, no findings gate

This is a dispatch-time security **control** (a guard whose job is to refuse), so it
is squarely in scope. I read all four named files in full and traced the control's
failure modes the dispatch specifically asked about. Every concrete bypass I could
construct either doesn't reach a code path that raises, or is already the operator's
signed, accepted tradeoff (PF-334e1b370c596f88c39730bf43579f13). No new finding.

## Census — what I read

- `harness_boundary.py`: full bodies of the four new helpers (`run_dir_grant_globs`
  L816-848, `_RUN_DIR_REF_RE`/`run_dir_refs` L855-876, `run_dir_slug_ok` L878-890,
  `run_dir_forms` L892-915), plus `glob_to_re`/`matches` (L315-348) since
  `run_dir_slug_ok` calls them on attacker-influenced candidate text.
- `dispatch-guard.sh`: full file (314 lines) — both python3 invocations (the
  non-isolated derivation subprocess L37-58, the `-I` isolated hook body L60-314),
  the run-dir shape-check block (L153-186) and its `try/except SystemExit: raise /
  except Exception` wrapper.
- `tests/integration/test-dispatch-guard.py`: full file (745 lines), esp. cases
  18-23 (the run-dir cases) including case 18's paste-back assertions (h).
- `tests/unit/test-harness-boundary.py`: full bodies of the six new
  `run_dir_*`/`write_synthetic_run_dir_manifest` cases (L582-704), incl. the
  garbage/binary-manifest case.
- Cross-referenced (read-only, outside the four-file set, to ground severity):
  `check-domain.sh` L356-358 — confirms write-time enforcement derives its target
  from `tool_input.file_path`/`notebook_path` (the real Write/Edit call), never
  from dispatch-prompt text.
- `plan.yaml` approval block (L1-30) and findings PF-334e1b370c596f88c39730bf43579f13
  / PF-20b1d027656f333f87b7c54ddf742281 (L186-221) — operator rulings, signed
  2026-09-07.

## Control-bypass questions, answered

**Can the `except Exception` fail-open be triggered by crafted prompt text?** No.
Traced every call in the shape-check block: `run_dir_refs` is pure regex
`finditer`/`str.rstrip` over `str` input (never raises on adversarial content);
`run_dir_slug_ok` → `matches` → `glob_to_re` always compiles (every glob char is
either translated to a fixed token or `re.escape`d, so no glob text — trusted
config or otherwise — can produce an invalid pattern). The only real exception
sources are I/O (`import harness_boundary`, module absence) — the intentional,
documented DEC-100 fail-open, not something a dispatch prompt can steer.

**Is `HARNESS_RUN_DIR_DERIVED`/`HARNESS_RUN_DIR_GLOBS` a caller-settable bypass?**
No. Both are set via `VAR=value python3 -I -c '...'` on the same line that invokes
the governed interpreter (`dispatch-guard.sh` L60), which always wins over any
identically-named variable already present in the hook process's inherited
environment. `_derived`/`_globs` are computed fresh, in-script, from the actual
exit status and stdout of the derivation subprocess (L37-58) every invocation —
there is no path where a pre-set env var reaches the check unmodified.

**Does prompt-derived text reach the manifest-derivation subprocess or a shell?**
No. That subprocess's only argv is `$GUARD_BIN_DIR` (from `BASH_SOURCE`, not
attacker-influenced); `$payload` is piped only to the second, `-I`-isolated
interpreter, and only via `json.load(sys.stdin)` — never shelled, never
string-interpolated into a command. The manifest path is
`os.path.join(root, ".harness", "team-config.yaml")` where `root` comes from
`hb.resolve_root(sys.argv[1], ...)` — no prompt text feeds it.

**ReDoS / unbounded resource use on the dispatch prompt?** `_RUN_DIR_REF_RE`
(`\.harness/([^/\s]+)/features/([^/\s]+)/runs/([A-Za-z0-9._-]+)`) has no nested or
overlapping quantifiers — each `[^/\s]+`/`[A-Za-z0-9._-]+` run is locally
unambiguous, linear per candidate substring. The synthesized `matches()` candidate
(`.harness/{repo}/features/{feature}/runs/{slug}/x`) is bounded to 5 `/`-segments
by the f-string's own literal delimiters regardless of how long `repo`/`feature`/
`slug` are, so `glob_to_re`'s `.*`/`[^/]*` translation of a (small, config-derived)
glob against it cannot blow up combinatorially. Attacker-controlled length scales
the match cost linearly, same order as the existing `FEATURE_RE` first-line scan.

**Stderr/log data exposure?** The refusal interpolates the attacker's own
`(repo, feature, slug)` back into stderr — self-disclosure of text the same
dispatching agent already wrote, not a cross-tenant leak. `slug` is restricted to
`[A-Za-z0-9._-]`; `repo`/`feature` exclude whitespace — no newline/control-char
injection that could forge a different diagnostic line.

## SC-08 escape-smuggling — assessed, already settled, not re-flagged

The dispatch specifically asked me to check whether `[.]harness/` anchor-breaking
(the paste-safety rewrite, D-05) lets a dispatcher pre-type the escaped form to
dodge `run_dir_refs` detection from the start, not just paste back a genuine prior
refusal. Confirmed structurally: `run_dir_refs` matches only the literal substring
`.harness/`, so a prompt written directly as `[.]harness/x/features/y/runs/badslug`
produces zero refs and the shape check never runs — indistinguishable from a
legitimate paste-back (case 18h in the integration suite exercises only the
legitimate half).

This is exactly finding `PF-334e1b370c596f88c39730bf43579f13` (severity `med` in
plan.yaml, L186-193), and it is **ruled, not open**: the operator's signed approval
(`plan.yaml` L9-11, 2026-09-07) accepts it explicitly — "escape spelling is
write-time-checked by check-domain.sh regardless; accepted mid-run-cost tradeoff,
not a bypass." I independently confirmed the mechanism behind that ruling:
`check-domain.sh` L356-358 derives its enforcement target from
`tool_input.file_path`/`notebook_path` — the real Write/Edit tool call — which is
completely unreachable from dispatch-prompt text. So smuggling past this shape
check only defers detection from dispatch time to write time; it grants no
unauthorized write. Per this run's ALREADY SETTLED list and rule O-05, I do not
add this to `must_fix` — it is the operator's call, already made.

## Findings

None reach `must_fix`. `severity_max: info` (in-scope, assessed, nothing open).

artifact: this file
