# Security review — FEAT-41-one-station-vocabulary — c0

**BLUF: FAIL.** Both gates named in the dispatch have real bypasses. The critical one is not in
`plan-sign-gate` at all — it is `check-domain.sh`'s plan.yaml route denial, which matches the
write target by **case-sensitive filename text**. On this workstation's filesystem (macOS/APFS,
case-insensitive by default) a governed agent whose domain covers the feature directory can write
a byte-identical clone of `plan.yaml` under a differently-cased name and land the bytes in the
real file, with **zero** enforcement from either gate. This defeats SC-07, SC-09 and the entire
D-07/DEC-120 threat model in one call, no shell tricks required.

## Findings, by severity

### 1. CRITICAL — `check-domain.sh`'s plan.yaml route denial is case-sensitive; `harness-orchestrator`'s wildcard domain reaches the real file through a differently-cased name. Blocks ship.

`check-domain.sh:1044` — `RE_PLAN_YAML = re.compile(r"^\.harness/[^/]+/features/[^/]+/plan\.yaml$")`,
matched at `:1444` against `_norm(target)`. The regex has no `re.IGNORECASE` and no path
canonicalization beyond `os.path.abspath`/`os.path.relpath` (`_norm`, `:984`) — it never calls
`realpath` or normalizes case. `harness-orchestrator`'s domain grant is
`{ path: .harness/*/features/**, upsert: true }` (`team-config.yaml:45`) — the **only** persona
grant in the manifest that is a recursive wildcard over a feature directory rather than an exact
filename (contrast `harness-pm`'s exact `.harness/*/features/*/plan.yaml`, `:113`).

**Reproduced end-to-end against the live hook code** (decision-only; no real file touched — target
was a nonexistent sibling path, which is sufficient because the check never stats the file for
this decision):
```
Write("...features/FEAT-41-one-station-vocabulary/plan.yaml",  agent=harness-orchestrator) -> exit 2 (approval_guard fires)
Write("...features/FEAT-41-one-station-vocabulary/Plan.yaml",  agent=harness-orchestrator) -> exit 0, NO stderr
Write("...features/FEAT-41-one-station-vocabulary/PLAN.YAML",  agent=harness-orchestrator) -> exit 0, NO stderr
Write("...features/FEAT-41-one-station-vocabulary/plan-copy.yaml", agent=harness-orchestrator) -> exit 0, NO stderr (any new filename, not just case variants, since RE_PLAN_YAML requires the literal name)
```
`harness-pm` writing the same case/name variants is correctly refused (no matching domain grant) —
this is specific to a wildcard-domain persona, and `harness-orchestrator` is exactly that persona,
and exactly the tier DEC-120/D-07 says must not be able to write the signature.

**Failure scenario:** `harness-orchestrator` — the tier this feature exists to keep off plan.yaml's
write path — issues one `Write` to `.../Plan.yaml` (or any non-`plan.yaml`-named file inside its
own feature directory) with a full plan.yaml body, including a forged `approval:` block. On this
host's default case-insensitive APFS, that write lands on the same inode as `plan.yaml`. Neither
`check-domain`'s plan.yaml route denial nor `approval_guard` (which is reached from the same
domain-allow path and is *also* apparently keyed off the exact filename, since no message printed
at all for the cased variants) ever sees it. `plan-merge.py`'s lock, station-vocabulary validation
and `_verify_spliced` splice-integrity check are never invoked — this is a raw filesystem write.
The post-Bash sweep (SC-06) does not help either: it only fires after a **Bash** call with no
`file_path` in `tool_input` (`check-domain.sh:~1499`, the `else:` branch); a `Write` call takes the
narrower `elif target:` branch that checks only the literal written path, so a same-session
corruption via `Write` is never subsequently globbed and re-validated. And even if it were, SC-06
only checks station values against the vocabulary — it does not check signature authenticity, so a
forged-but-vocabulary-legal `approval:` block would pass it silently regardless.

**Scope note:** the underlying weakness (case-sensitive, non-canonicalized path matching in
`check-domain.sh`'s shape gate) is pre-existing and applies to all five `SHAPE_PATTERNS`, not
introduced by this diff. What FEAT-41 changes is the **consequence**: T-09 is the first time this
exact mechanism is asked to protect a user's signature rather than a line-count budget, and it is
not equal to that job. Portability note: this specific reproduction depends on a case-insensitive
filesystem (default macOS/Windows, not default Linux) — but the broader "any non-`plan.yaml`-named
file inside a wildcard domain evades the gate entirely" bypass (`plan-copy.yaml` case above) needs
no case-insensitivity at all and is filesystem-independent.

**Remedy shape** (not prescribing implementation): the route denial needs to key off something the
gate cannot be lied to about — e.g., resolve the target via `os.path.realpath` and compare
case-normalized on case-insensitive platforms, or independently reject *any* write to a path whose
`realpath` resolves inside an existing `plan.yaml`'s directory with a name that case-fold-equals
`plan.yaml`, or (more robust) don't rely on filename matching at all and instead deny plan.yaml-
directory writes to any file `approval_guard` would also need to inspect.

### 2. HIGH — `plan-sign-gate.py`'s verb-adjacency check is defeated by a leading `--`; the resulting command **actually executes** `sign-approval`. Blocks ship (weakens SC-07 as measured, not as ruled).

`plan-sign-gate.py:116` — `if is_tool(t) and toks[i + 1:i + 2] == [VERB]: return True` requires the
verb token to sit **immediately** after the tool token. `python3 .../plan-merge.py -- sign-approval
--file x.yaml` tokenizes (verified via `shlex.shlex(..., punctuation_chars=True)`) to
`[..., 'plan-merge.py', '--', 'sign-approval', '--file', 'x.yaml']` — the token after
`plan-merge.py` is `--`, not `sign-approval`, so `denies()` returns `False` and the gate exits 0.

This is not inert: `plan-merge.py`'s own `argparse.ArgumentParser(...).add_subparsers(...)`
(`plan-merge.py:763-805`) **accepts** a leading `--` before the subcommand name — reproduced with a
standalone `argparse` harness: `parser.parse_args(["--", "sign-approval", "--file", "x.yaml"])` →
`Namespace(cmd='sign-approval', file='x.yaml')`. So an agent typing `--` before the verb (a common,
non-adversarial habit — "always separate flags from positionals") both evades the refusal *and*
successfully signs. This is a full, ordinary-looking bypass of the one property SC-07 names, not a
theoretical evasion.

Two further evasions confirmed reachable and executable, though closer to deliberate obfuscation
than habit — rated lower but real: `echo sign-approval | xargs -I{} python3 .../plan-merge.py {}
--file x.yaml` (verb arrives via `xargs` substitution, invisible to the tokenizer) and any
Python/script indirection that shells out to `plan-merge.py sign-approval` from inside a file the
agent wrote and ran (`python3 helper.py`) — the gate only ever inspects the literal Bash command
text of the *triggering* call, never anything a spawned interpreter does. Both were empirically
confirmed to return exit 0 against the real gate. These match the file's own documented residual
("a binary produced only by shell expansion is invisible here") in *spirit*, but the `--` case is a
distinct, previously-undocumented gap — the tool name is not obscured at all, only the
adjacency-to-verb heuristic is wrong — and the xargs/subprocess-indirection cases are a broader
class than the documented "shell expansion of the tool name" residual: here the **verb**, not the
tool name, is the thing hidden from the token stream. Confirmed via `variable indirection` also
evading as already disclosed in the file's own docstring (not a new finding).

**Remedy shape:** treat a leading `--` (and, more generally, any token argparse would silently
consume before the first positional) as transparent in `denies()`'s adjacency check, not as an
opaque separator.

### 3. MEDIUM — `plan-sign-gate.py` has no top-level exception guard; a malformed hook-payload shape crashes to exit 1, which DEC-100 defines as non-blocking (full silent bypass). Reachability-closed under the current registration, but worth hardening.

`plan-sign-gate.py:73` (`payload.get("agent_type")`) and `:76` (`payload.get("tool_input")`) run
**outside** the `try/except` at `:64-67`, which covers only `json.load`. Reproduced: a top-level
JSON value that is not a dict (`list`, `null`, a bare string) or a `tool_input`/`command` of the
wrong type each raise an uncaught `AttributeError`/similar → Python's default uncaught-exception
exit is **1**, and per DEC-100 (`DECISIONS.md:944`, confirmed again at `:2492`/`:2654`) "only `exit
2` blocks... any other exit — including an uncaught exception — is non-blocking and the write
proceeds." A syntax error introduced by any future edit to this file has the identical effect (a
`SyntaxError` also exits 1) — reproduced separately by injecting a syntax error into an equivalent
script and confirming `exit 1`; this is a *general* property of the wrapper, not specific to the
payload path. By contrast, a **missing** `plan-sign-gate.py` file coincidentally exits 2
(`python3 <missing path>` itself exits 2 on `FileNotFoundError`) and so accidentally still blocks
— fail-closed for the wrong reason, and only by luck of Python's own exit-code convention for that
one failure mode; it does not generalize to "interpreter dies → block."

This is the exact "fail-open crash" class `DECISIONS.md:2654` already records fixing once in this
repo, in `validate-digest.py` — that fix's own lesson was "wrap the one call that could actually
raise in `try/except`... fail OPEN, LOUDLY, matching `check-domain.sh`'s precedent" for a
*non-security* validator. For a gate whose stated whole job is refusal (`plan-sign-gate.py`'s own
docstring: "REFUSING IS THE POINT"), the correct application of that lesson is fail **closed** on
internal error (force `exit 2`), and this file does neither consistently: it fails open on JSON-
parse failure by design (matching `gh-close-gate.py`'s own precedent, `gh-close-gate.py:24-27` —
not a new deviation), but its exception guard is **narrower** than that same precedent: `gh-close-
gate.py` wraps the entire "parse JSON, then extract `tool_input.command`" sequence in one
`try/except` (`gh-close-gate.py:24-27`); `plan-sign-gate.py` only wraps the parse step, leaving the
two subsequent `.get()` calls unguarded. That is a real, if narrow, regression relative to the file
it says it is modelled on.

**Reachability:** the `PreToolUse` matcher for this hook is exactly `"Bash"` (`.claude/settings.json`,
confirmed unregistered for any other tool), and Claude Code constructs `tool_input` for the Bash
tool per its own fixed schema (`{"command": <string>, ...}`), so under normal operation the
malformed-shape crash paths above are **not reachable by an agent's ordinary tool use** —
closing on provenance: this assumes the platform never delivers a Bash `tool_input` of the wrong
shape. I could not verify that assumption against the live Claude Code/OMP runtime from a static
review; if it is ever violated (a compatibility-layer bug, a future tool matcher widened to a
second tool), the bypass is immediate and total. Rated MEDIUM rather than HIGH on that
provenance-closure, not LOW, because the fix is one line and the class has already bitten this repo
once.

### 4. INFO — `worktree_terminal.py:classify`'s plan.yaml station read is correctly fail-safe on every enumerated input; recorded rather than silently passed over.

Verified by tracing every branch of `_read_landed_plan_yaml` (`worktree_terminal.py:~178-232`) and
`_scan_top_level_status` (`:~234-247`) into `classify` (`:~336-368`): missing file, git failure,
empty blob, YAML parse exception, and `MissingDependency` (PyYAML absent) all resolve to
`"unresolved"`, which `classify` never treats as `"terminal"` — the record is added with
`klass: "unresolved"`, not deleted. An absent top-level `status:` key, a `status:` value outside
the six-station vocabulary, and (the specific worry named in the dispatch) an indented per-task
`status:` line all fall through to the `else` branch — the worktree is **omitted from the terminal
set entirely**, not deleted. The column-0 anchor (`line.startswith("status:")`, no leading
whitespace tolerance) is real and does exactly what its docstring claims: a task-indent `status:`
line cannot shadow the top-level key because it never starts the line. Every wrong-answer path
converges on "do not delete." No finding.

### 5. INFO — `plan-merge.py`'s `_verify_spliced` (STEP 9) closes the specific defect class it names, not the full class of splice corruption.

`plan-merge.py:232-262` verifies the spliced output re-parses as YAML and that every `UNION_KEYS`
list's item-**id** sequence matches the expected merge (base ids plus newly-added proposal ids).
This closes exactly the measured incident (`_reindent` bugs / structural corruption producing
unparseable or id-mismatched output) and the `approval:` block is separately protected
byte-identically regardless of this check (`apply_merge` step 7, `:412-420` — never routed through
`_verify_spliced`'s comparison at all, so this doesn't weaken that guarantee). It does **not**
verify field-level content within an item beyond id-list membership/order — a hypothetical splice
defect that swaps or corrupts a field *within* a correctly-id-matched item would still pass. Given
the measured incident this exists for was structural (id/parseability), and the approval block has
its own independent byte-identity guarantee, this is recorded as a scope note, not a finding that
blocks ship.

### Board writes / `gh_board.py` / `gh-sync.py` — no findings

`factory_config.station_column` (`factory_config.py`) raises `FleetError` on any value outside the
six `MANDATED_STATIONS` **before** producing a column name, and `gh_board.set_station` calls it
before any `factory_gh` call (`gh_board.py`, `column = factory_config.station_column(station)` at
the top of the function, ahead of the `try:`/GraphQL call) — an unvalidated station value cannot
reach the GitHub boundary. `gh_board.project`'s two raise sites (`_task_cards`, `_parent_station`)
validate before values ever enter the returned mapping. Every `subprocess.run` call site touched by
this diff in `gh-sync.py` uses list-form argv, never `shell=True` — no injection surface. No
credential/token/secret strings found in a full-diff grep (`token` hits are all the parsing sense —
shlex tokens, whitespace-split tokens — never a credential).

## DIGEST answers to the two explicit questions

- `plan-sign-gate` (the sign-approval refusal hook): **YES, has a fail-open branch.** The `--`
  adjacency bypass (finding 2) is a full, ordinary-looking, confirmed-executing bypass of the
  refusal. The exception-guard gap (finding 3) is a second, narrower fail-open branch,
  reachability-closed under the current Bash-only registration.
- `check-domain` plan.yaml route denial: **YES, has a fail-open branch**, and it is the more
  severe of the two (finding 1) — case-insensitive-filesystem same-file writes and any
  differently-named file inside a wildcard domain both evade it completely, with no compensating
  detection anywhere in the described mechanism (SC-06's sweep does not cover the `Write`-tool
  route, and would not catch a vocabulary-legal forged signature even if it did).

## Not independently re-verified (named, not silently skipped)

- Hook **timeout** behavior (blocking vs non-blocking on a hung interpreter) — undocumented in this
  repo's own DEC-100 platform-unknowns record and not testable from a static review; open question.
- Whether the live Claude Code/OMP runtime can ever deliver a non-canonical `tool_input` shape to a
  `matcher: "Bash"` hook (finding 3's provenance assumption) — assumed false, unverified against the
  live runtime.
- `feature_json_write.py` (D-13) — **unchanged by this diff** (`git log base..review_sha -- feature_json_write.py`
  returns nothing); read anyway for completeness: locked via `harness_merge.locked_update`
  (fcntl lock, same-dir tempfile, fsync, `os.replace` — atomic), schema-validated before write,
  path resolved rather than trusted literally. No finding; out of diff scope.
