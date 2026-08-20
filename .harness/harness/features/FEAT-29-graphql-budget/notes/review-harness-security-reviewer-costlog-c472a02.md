# Security review — gh cost log data exposure (FEAT-29 T-03) — c472a02

## Headline

No current call path puts a secret into `argv` recorded by `gh_cost_log.record()`. The module has
real gaps — truncation is not redaction, the log directory is not gitignored, the file is created
world-readable, and enabling it prints no warning — but every one of them is latent: none is
exploitable today because nothing wired through `factory_gh.run_gh` or `gh-sync.py`'s `gh()` ever
puts a credential in argv. PASS, advisory only.

## 1. Can a secret reach the file? — swept, none found

Every `run_gh(`/`gh(` call site across `.claude/skills/harness/bin/*.py` (excluding tests) was
enumerated. Full flag inventory of `-f`/`-F` value pairs — the only positions `_sanitize_argv`
touches (`gh_cost_log.py:89-97`):

- `factory_gh.py:314-318,409-413,509-513`: `owner=`, `number=`, `field=`, `cursor=`, `query=`
  (the module's own hardcoded GraphQL query text) — all internal identifiers or query text, never a
  credential.
- `factory_gh.py:645`: `ref=`, `sha=` — git ref data.
- `gh-sync.py:541,674,679,688,754`: `title=`, `description=`, `state=`, `state_reason=` — feature
  text already destined for a public GitHub issue body, not a secret.
- `gh_issues.py:22,31`: `sub_issue_id=`, `issue_id=` — internal issue IDs.

No call site anywhere uses `--with-token`, `-H`/`--header` with an `Authorization` value, or a URL
with embedded credentials. `gh`'s own authentication is out-of-band (keychain/token file the CLI
manages itself) — it is never passed as an argv token in any of these invocations. **Clean result,
stated plainly: on every current call path, nothing secret is in argv to begin with.**

## 2. Is truncation-at-80 a redaction control? — No, and it is not described as one

`_sanitize_argv` (`:89-97`) truncates only the value immediately following `-f`/`-F` past
`_MAX_ARG_LEN = 80` (`:37`), and the docstring states its purpose is bloat control ("so a query body
does not bloat the recorded line") — nothing in the module claims redaction. Two consequences if a
future call site ever did carry a credential:

- A classic `gh`/GitHub token (`ghp_...`, 40 chars) or any secret under 80 chars passed as an `-f`/`-F`
  value would be written **in full**, untruncated.
- A secret passed via any flag other than `-f`/`-F` (a header, `--with-token`, a bare positional) is
  not touched by `_sanitize_argv` at all — the guard is scoped to two flags, not to argv generally.

This is real: `test-gh-cost-log.py` (grepped, no hits for `redact`/`secret`/`token`/`password`)
confirms secret-handling was never a design input, only bloat.

## 3. Where the file lands, and who can read it

- **Not gitignored.** Root `.gitignore` has no rule for `.harness/logs/**`; sibling files
  (`.harness/logs/2026-07-27.md` etc.) are already tracked (`git ls-files` confirms). If a secret
  ever reached `gh-cost-<date>.jsonl`, a routine `git add -A`/`git add .` would stage it for commit —
  the file itself sat as `?? .harness/logs/gh-cost-2026-08-19.jsonl` in `git status`, i.e. already
  present and only one `git add` away.
- **Created world-readable.** Observed on disk: file `-rw-r--r--` (0644), directory `-rwxr-xr-x`
  (0755, from the process umask 022) — `record()` (`:126-132`) calls `os.makedirs(..., exist_ok=True)`
  and `open(path, "a")` with no `os.chmod`/restrictive mode anywhere in the module. Any local account
  on the machine can read it.

**On this ship-review's own record, B-8 ("gitignoring the cost log") was struck as "moot" because the
opt-in default made it so** (`notes/ship-review-2026-08-19-02.md:97-98`). That framing conflates two
different controls: the opt-in default shrinks the *time window* recording happens; gitignore/chmod
would shrink *what a secret, once recorded, can reach*. Finding 1 is why B-8 is low-severity today —
because no call site puts a secret in the file — not because the missing gitignore/permissions
stopped mattering. If a future wrap-site addition ever threads a token through `-f`/`-F` (finding 2),
these two absent controls are what would have contained it, and they are not there.

## 4. Does OFF-by-default change the risk?

Yes, materially, for the window: `_enabled()` (`:47-53`) gates every entry point (`record()` at
`:112-113`, `measured()` at `:157`) on `HARNESS_GH_COST_LOG=1`, default `"0"` — confirmed by reading
`os.environ.get(..., "0") == "1"`. Recording is inert unless an operator explicitly opts in while
investigating a burn, which is the framing the dispatch offers and it holds.

**But nothing warns the operator at the moment of opting in.** The only documentation of the
env var's behavior (opt-in, unredacted, bloat-truncation-only) lives in `BRIEF.md:50-52` and
`plan.yaml` — feature-internal planning artifacts, not anything printed by the tool or in
user-facing docs (`README.md`, `docs/`, `.harness/README.md` — grepped, zero hits for
`HARNESS_GH_COST_LOG`). An operator who sets the var for a burn investigation gets no in-the-moment
notice that what gets written is raw, un-redacted, and not gitignored.

## Verdict rationale

Every question the dispatch asked resolves to "no exploit today, real latent gaps." Nothing in this
diff crosses a trust boundary with an actual credential in flight. The three gaps (2/3/4) are
defense-in-depth items — worth doing before this module's coverage is ever widened past
`run_gh`/`gh-sync.py`'s two wrap sites, not worth blocking ship on.

## Recommendations (non-blocking)

- Add `.harness/logs/gh-cost-*.jsonl` (or all of `.harness/logs/`) to `.gitignore`.
- `os.chmod(path, 0o600)` on create in `record()`.
- Rename or annotate `_sanitize_argv`/`_truncate` so a future maintainer adding a wrap site does not
  mistake bloat-truncation for redaction.
- One-line stderr notice when `_enabled()` is first true, naming that recording is raw and the file
  is not gitignored.
