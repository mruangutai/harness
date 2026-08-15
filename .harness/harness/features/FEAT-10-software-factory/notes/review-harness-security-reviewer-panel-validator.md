# Security review — FEAT-10 software factory, working tree vs f9488a2

## Verdict: PASS (severity_max = info)

Read all 15 untracked `factory_*.py`/`test-factory-*.py` modules under
`.claude/skills/harness/bin/` in full (not diffed — they are `??`, per the dispatch's
establishing note), plus the four tracked-diff files (`run-unit-tests.sh`, `harness.json`,
`DECISIONS.md`, `DECISIONS-INDEX.md`), the read-only `.harness/factory/fleet.yaml`, and
`test-factory-integration.py`'s stub-execution and environment-substitution paths in detail. No
`must_fix`. Every real mechanism checked resolves to a documented mitigation or a
same-or-higher-trust actor already holding the capability a theoretical exploit would grant
(Expertise P-02). Three items are worth carrying forward as non-blocking `open_questions`.

## Scope

In scope per the dispatch: 15 new factory modules/tests, `run-unit-tests.sh`, `harness.json`,
`DECISIONS.md`/`DECISIONS-INDEX.md`, and `fleet.yaml` as read-only context. Confirmed the
untracked files via `git status --porcelain` — `git diff HEAD` alone would have shown nothing for
them. T-08 (`check-state.sh`, `test-check-state.py`) and all other held dirt were not opened.

## What was checked and the result

**1. argv construction / shell injection (`factory_gh.py`, `factory_workspace.py`).**
`grep -n "shell=True"` across both files: zero matches. Every `subprocess.run` call is
`[binary] + list(args)` — list-form argv, `stdin=subprocess.DEVNULL`. This structurally forecloses
shell metacharacter injection from any value (title, body, branch, repo) reaching either `gh` or
`git`. Confirmed by direct read of `run_gh` (`factory_gh.py:79-102`) and `run_git`
(`factory_workspace.py:38-61`) — no other invocation site in the tree.

**2. Flag/argument injection via a leading `-` — three distinct mechanisms, checked separately
rather than asserted as one property (an earlier draft of this report over-generalized this; the
three do not share a risk profile):

- **`--title`/`--body` (`factory_gh.create_issue`, `factory_land.py:68-71`).** Values are passed
  as separate argv tokens *after* their flag (`["--title", title, "--body", body]`), never
  `--flag=value` concatenation. `gh`'s CLI (Cobra/pflag) is documented to consume the token
  immediately following a value-taking flag unconditionally, regardless of a leading dash, in this
  two-token form. **Not independently verified live**: hard bound #3 forbids live `gh` calls, and a
  non-mutating smoke test (`GH_TOKEN=invalid gh issue create --repo ... --title -x ...`) was
  blocked by the sandbox's own command classifier before it reached `gh`. Rated `info`: even in the
  worst case the values reaching this path are plan-authored task titles (already signed, same
  trust tier as the code) or an issue title read back from GitHub (item 4 below). `open_questions`
  Q1 asks for a one-time offline smoke test to close this residual.
- **Bare positional label arguments (`factory_gh.ensure_labels`/`add_label`,
  `factory_gh.py:117-126,150-151`).** These *do* take a bare positional (`["label", "create",
  label, ...]`) where pflag's argument-consumption rule does not apart apply — a positional
  starting with `-` can be parsed as an option by `gh`'s own top-level flag scanner. Checked every
  call site in this diff (`grep -n "ensure_labels\|add_label("`): all three
  (`factory_decompose.py:304,316`, `factory_claim.py:328`) pass either a fixed literal
  (`"harness"`, `"chore"`, `"bug"`, `"factory:claimed"`) or `f"feature:{feat_id}"` — always
  prefixed with a non-empty fixed string, so the resulting token can never begin with `-`
  regardless of `feat_id`'s content. Confirmed not exploitable in this diff; the mechanism would be
  live the day a caller passes an unprefixed label. Not a finding today.
- **`run_git(["checkout", default_branch], path)` (`factory_workspace.py:129`).** This is a genuine
  unprefixed bare positional: `default_branch` comes straight from `fleet.yaml`'s
  `repos[].default_branch`, validated only for truthiness (`factory_config.py:126`), no format
  check. The other three `checkout` call sites in the same module always wrap the value as
  `f"origin/{default_branch}"` first, which removes the leading-dash risk by construction; this one
  does not. Source is 100% operator-authored `fleet.yaml` (same trust tier as the code itself —
  reaching this requires already controlling the harness checkout), so `info`, not a finding. Worth
  a one-line defensive note for whoever touches this file next: prefixing with `origin/` here too,
  matching the module's own established pattern, would close it for free.

**3. A distinct mechanism: fleet data reaching a structured mini-language, not a bare argv token
(`factory_claim.py:237`).** `query = f'{station_field}:"{ready_option}" is:open'`, passed via
`--query` as a single argv token to `gh project item-list` — safe from *argv* injection (one
token), but `station_field`/`ready_option` are interpolated into GitHub's search-query syntax
without escaping an embedded `"`. A `fleet.yaml` value containing a quote character could alter the
query's semantics. Same trust tier as item 2's third case (operator-authored `fleet.yaml`); `info`.

**4. Path traversal, three-tier root resolution (`factory_config.harness_root`,
`workspace_path`, `FEATURES_ROOT`).** `harness_root()` only trusts `CLAUDE_PROJECT_DIR` when
`docs/harness/SPEC.md` is readable under it; a discarded value is announced on stderr, never
silently substituted (`factory_config.py:35-47`, confirmed by read). `workspace_path()` joins
`fleet["workspace_root"]` (schema-checked absolute path, operator-authored) with
`repo_name.split("/", 1)[-1]` — but `repo_name` is never attacker-reachable unconstrained: every
call site resolves it through `factory_config.repo_entry(fleet, name)`, which raises `FleetError`
on anything not an exact match to a `fleet.yaml`-declared repo name (`factory_config.py:142-152`),
or through `factory_claim.py:241-246`'s `repo_name not in repo_names: continue` filter against the
same fleet set. No board content, issue title, or environment variable reaches a filesystem join
without first being forced to equal a value the operator put in `fleet.yaml`. Not a finding.

**5. `factory_land.py:66-71` — the issue-title round trip.** `gh issue view` returns whatever the
issue's title currently is; `factory_land` trusts it verbatim as the opened PR's title. Traced who
can set it: `mruangutai/harness` is public (`BRIEF.md:57`), but retitling an *existing* GitHub
issue requires repo write access (author-or-collaborator), not mere issue-creation rights — a
public, non-collaborator visitor cannot retitle someone else's issue. A principal with that write
access already has the ability to push arbitrary commits, open their own PRs, or edit any file in
the repo directly — capability strictly greater than "set a PR's title text." Per Expertise P-02,
an actor who already controls a value already holds the privilege it grants: not an escalation.
`info`.

**6. `FACTORY_GH` / `FACTORY_GIT` as a binary-substitution vector.** Confirmed by both modules'
own docstrings and by `_gh_binary()`/`run_git`'s `os.environ.get(..., "git"/"gh")` — resolved at
call time, explicitly to let a test substitute a recorder. An actor able to set this process's
environment variables already has arbitrary code execution as that OS user; pointing `FACTORY_GH`
at an attacker binary grants nothing beyond what setting an environment variable already implies.
Test seam, not a trust boundary. `info`, not a finding.

**7. Whether the test suite itself can leak the operator's live `gh` session.** Checked, not just
grepped: `test-factory-integration.py` writes its stub `gh`/`git` executables under
`tempfile.TemporaryDirectory()` per case (never a fixed/shared path — confirmed at every
`write_exec(gh, ...)` call site), so no predictable-path race. Every `base_env()` call either sets
both `FACTORY_GH`/`FACTORY_GIT` to the stub, or omits one/both — checked each omission concretely:
Case (B) omits both and runs `claim` against a *missing* `--fleet` path, which raises `FleetError`
in `load_fleet` before `factory_gh.preflight()` is ever reached (`factory_claim.py:201-205`);
Case (D-config) omits both and runs the `config` tool, whose `_main` never imports or calls
`factory_gh` at all; Case (D-workspace) omits `gh_bin` only and runs `workspace`, which the file's
own docstring (and `factory_workspace.py`'s import list) confirms never calls `gh`. Each omission
is paired with a tool path that structurally cannot reach a real network call. The one intentional
live exception is the bottom-of-file live-git smoke check, which points `FACTORY_GIT` at the real
`git` binary against a throwaway local repo and never sets `FACTORY_GH` near it. No path in this
suite reaches the operator's authenticated `gh` session. Not a finding.

**8. Hostile `fleet.yaml`.** Verified the actual call chain rather than assuming it:
`factory_config.py` imports `harness_yaml`, never `yaml` directly (`grep -n "^import yaml"
factory_config.py` — no match); `harness_yaml.load_file` → `load_str` → `yaml.load(text,
Loader=_StrictSafeLoader)` where `_StrictSafeLoader` subclasses `yaml.CSafeLoader`/`yaml.SafeLoader`
only (`harness_yaml.py:100-234`) — never `yaml.Loader`/`FullLoader`/`UnsafeLoader`, so
`!!python/object/apply` and friends cannot construct arbitrary objects. `load_fleet` additionally
schema-validates every field (owner truthy, `board.number` is a non-bool int, all three station
names present, `repos` non-empty with `name`/`default_branch`, `workspace_root` absolute) before
any value is used, failing closed with a `FleetError` naming the exact bad key on all nine
documented malformed shapes. A hostile `fleet.yaml` requires write access to the harness checkout
itself — already full compromise of the operator's own machine. Not a finding.

**9. Token/credential material reaching stdout, stderr, or `feature.yaml`.**
`GhError.__str__`/`factory_cli.body()` only ever render `what`/`value`/`next_step`
(`factory_gh.py:32-46`) — never the raw captured `stdout`/`stderr`. `next_step` is
`_first_line(stderr) or _first_line(stdout)` (`factory_gh.py:97`) — the first line of whatever
`gh` printed on failure (diagnostic text; gh's own auth lives in its keychain/token store, never
passed through this code's argv or captured output). `FACTORY_DEBUG=1` prints
`traceback.print_exc()`, which prints the same bounded `body()` string, not the full captured
blobs or argv. The only file this feature writes, `factory_decompose.write_factory`, persists
issue numbers, item ids and edge lists the tool constructed itself — never raw `gh`/`git` output.
Not a finding.

**10. `factory_claim`'s candidate filter has no "harness"/"feature:" label gate — checked whether
that is exploitable on a public repo.** By design (`DESIGN.md:234`, `DEC-186`), an issue with no
resolvable `feature:` label is "not gated at all" and stays claimable — settled ruling, confirmed
matching in code (`factory_claim.py:290-303`). On its own this would be a real provenance gap on a
*public* fleet repo: an externally-authored issue reaching the `Ready` board column would be
claimed, branched, and PR-opened with no review of its content. Checked whether that channel
exists: **it does not, by explicit design** — `BRIEF.md:68-70` records that this increment uses
**no** Projects v2 auto-add workflow at all ("every board item is added explicitly by a factory
tool"). Every `Ready`-column item is added only by `factory_decompose.project_item_add`, itself
driven only by a signed `plan.yaml`, or by an operator/collaborator manually dragging a card
(requires *project* write access — a privilege the public issue-creation surface does not grant).
Not a finding today; recorded as `open_questions` Q2 because it is a **latent** trap: if a future
increment turns on auto-add for this board, or the fleet grows to include a repo where a
lower-trust principal holds project-write access, `factory_claim` would start claiming and PR-ing
arbitrary externally-authored issue content with zero label check.

## Fix order (qa's, carried per the dispatch)

1. **Agree, deferring**: the `harness.json`/`functional.cmd` misconfiguration QA's gate blocks on
   is a config-only diff with no security surface (widens `integration.detect`, drops a stale
   `_reason` string). Not my domain to rule on; nothing security-relevant there.
2. **Agree with routing `gh pr create` behind a `create_pull_request` helper on `factory_gh`** —
   module-boundary/testability point (the docstring at `factory_land.py:14-16` already flags it as
   a known gap), not a security defect I can independently corroborate at `factory_land.py:77`
   beyond what's already raised: the `"already exists"` match there is scoped to the combined
   stdout+stderr of the exact `gh pr create` call this process just issued against these exact
   args, so a mismatched-URL adoption is a correctness edge case, not a cross-boundary one. No
   objection to the ordering.
3. **Will not recommend patching `factory_land.py:77`'s predicate in place** — noted and honoured.

## Findings table

| # | Location | Severity | Status |
|---|---|---|---|
| 1 | `factory_gh.py`, `factory_workspace.py` — argv construction | info | confirmed safe (no `shell=True`, list argv throughout) |
| 2a | `factory_gh.create_issue`, `factory_land.py:68-71` — flag-value leading dash | info | not independently verified live (blocked); low real exposure |
| 2b | `factory_gh.ensure_labels`/`add_label` — bare positional | info | mechanism real, but every call site in this diff prefixes a fixed string; confirmed not exploitable today |
| 2c | `factory_workspace.py:129` `checkout default_branch` — bare positional | info | genuine unprefixed positional, but source is 100% operator-authored `fleet.yaml` |
| 3 | `factory_claim.py:237` — GH search-query interpolation | info | single argv token (no injection); fleet-authored content could alter query semantics |
| 4 | `factory_config` path resolution | info | confirmed bounded to fleet-declared or SPEC.md-probed roots |
| 5 | `factory_land.py:66-71` — issue-title round trip | info | actor who can retitle already holds repo write access (no escalation) |
| 6 | `FACTORY_GH`/`FACTORY_GIT` env override | info | documented test seam; env control already implies code execution |
| 7 | test suite's env/stub handling | info | confirmed no path reaches operator's live `gh` session |
| 8 | `fleet.yaml` parsing | info | confirmed `harness_yaml`→`yaml.safe_load`-equivalent path, full schema validation |
| 9 | Token/credential reaching stdout/stderr/`feature.yaml` | info | confirmed no sink carries raw captured output or argv |
| 10 | `factory_claim` candidate filter, no label gate | info | resolved today by "no auto-add workflow" (`BRIEF.md:68-70`); latent if that changes |

`must_fix: []`. `severity_max: info`.
