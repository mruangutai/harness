# Security review — BUG-442, pinned 6d969ed3..9b3fde7e

**Verdict: PASS.** One code file in scope, `tests/integration/test-harness-yaml.py`
(+182/-0, all diff read via `git show 9b3fde7e:tests/integration/test-harness-yaml.py`
and `git diff 6d969ed3 9b3fde7e -- tests/integration/test-harness-yaml.py`, full
unelided text obtained via `artifact://1219`). This is a test-only diff, but it earns
a real security look because it spawns subprocesses, propagates the full parent
environment, and is itself the guard for a write-grant boundary. Looked at all six
named areas; no must-fix findings.

## 1. Subprocess execution — ruled out
`_run_child` (added, in `test_docs_domain_witness_reddens_on_addition_removal_and_census_drift`)
calls `subprocess.run([sys.executable, os.path.realpath(__file__)], capture_output=True, text=True, env=...)`.
List-form argv, no `shell=True`, no string interpolation — both elements are process-derived
(`sys.executable`, `os.path.realpath(__file__)`), never built from manifest or mutant text. No
injection path.

`os.path.realpath(__file__)` under a symlinked checkout: resolves to whatever the symlink
target is. Exploiting this needs write access to the checkout's symlink structure — the same
trust tier as write access to the test file itself, so no escalation.

**No `timeout=` argument** on either subprocess.run call added by this diff — a hang in the
child (e.g. a pathological manifest triggering slow/backtracking YAML parsing) blocks the CI
job until the job-level timeout kills it. Checked against the base commit: the two
pre-existing `subprocess.run` calls in this same file (lines 310, 377 at `6d969ed3`) already
omit `timeout=` — this diff continues an established in-file convention, not a new gap.
**info**, non-gating, consistent with prior convention (`tests/integration/test-harness-yaml.py:349-352`).

## 2. Environment handling
`env={**os.environ, 'HARNESS_PROJECT_DIR': tmp, 'BUG442_MUTANT_CHILD': tmp}` (`:349`) forwards
the *entire* parent environment to the re-exec'd child. Traced every place the child's captured
`stdout`/`stderr` is later interpolated into an assertion message (`:356-357`, `:378-381`,
`:383-386`): all three interpolate `child.stdout`/`child.stderr` verbatim into the exception
text that `main()` (`:1074-1085`, unchanged) prints as `FAIL <test>: <e>`. That text is
genuinely exposure-shaped if the child ever prints something secret-bearing.

Checked what the child actually prints: `main()` only prints `ok   {name}` or
`FAIL {name}: {e}`, and grepped every exception message in the full file for anything that
formats raw `os.environ` — none does; the three other places that touch env vars
(`:471-480`, `:487-492`, `:512-523`, `:554-556`) only set/pop two named keys
(`HARNESS_PROJECT_DIR`, `CLAUDE_PROJECT_DIR`) and never print the environment. So propagating
the full env is real but the capture-and-print path never surfaces any of it — **ruled out**
as an active leak, given the file as it stands today. Flagging as **info**: this is a latent
amplifier — the day any test in this file starts embedding an env value in an assertion
message, that value becomes reachable through the witness's own failure-mode logging, and
nothing here would catch that regression.

`BUG442_MUTANT_CHILD` — assessed whether an externally/accidentally set value can make the
control pass without exercising anything. The guard (`:301-302`) only silently returns when
`BUG442_MUTANT_CHILD == HARNESS_PROJECT_DIR` *exactly*; any mismatch (e.g. the var merely being
present, as it would be if leaked from a parent shell) is caught by the very next line
(`:303-309`, `assert _child_token is None`) and fails loudly with a message naming the
mismatch. Producing a silent no-op therefore requires an attacker who can set both
`BUG442_MUTANT_CHILD` and `HARNESS_PROJECT_DIR` in CI to the identical value — that level of
CI-config control is the same trust tier as editing the test file directly. **Ruled out** as a
privilege escalation (P-02: the actor already holds the privilege the "bypass" would grant).

## 3. Filesystem writes — ruled out
`_run_child` (`:340-349`) uses `tempfile.TemporaryDirectory()` as a `with`-block; the write is
`os.makedirs(os.path.join(tmp, '.harness'), exist_ok=True)` then
`open(os.path.join(tmp, '.harness', 'team-config.yaml'), 'w')` — both path segments are
fixed literals joined onto `tmp`, no manifest- or mutant-derived path component, so no
traversal is possible. `subprocess.run(...)` is called *inside* the `with` block, so cleanup
(`TemporaryDirectory.__exit__`) runs before the function returns regardless of the child's
exit code or of an assertion later raised by the caller — no artifact is left behind on
failure. Default `mkdtemp` permissions (0700, owner-only) apply; nothing broadens them.

## 4. Deserialization — ruled out, pre-existing and unchanged
`_docs_domain_census` calls `hy.load_file(manifest_path)` → `harness_yaml.py:load_str` →
`yaml.load(text, Loader=_StrictSafeLoader)` where `_StrictSafeLoader` subclasses
`CSafeLoader`/`SafeLoader` (`harness_yaml.py:131-134`) — a safe loader, not `yaml.load` with the
default `Loader=None`/`FullLoader`, so no `!!python/object` or arbitrary-constructor
deserialization is possible. This loader is untouched by this diff; the diff only calls into
it as an existing dependency. The manifest text the test constructs (real text plus one
literal string edit) is never attacker input — it originates from the repo's own committed
`.harness/team-config.yaml`, read at `:281` and mutated in-process by string literals the test
itself hardcodes.

## 5. Injection into manifest text via string replacement — ruled out (no security relevance)
The three mutants (M1 `:307-313`, M2 `:315-321`, M3 `:322-324`) insert/remove/rename using
fixed string literals, never anything derived from external or manifest-original content
(other than locating the insertion point). Each is a scratch document, written only to a
`TemporaryDirectory` and consumed only by a re-exec'd instance of this same test file — never
by `check-domain.sh` or any production consumer of the real manifest. This is a correctness
mechanism (proving RED-capability, D-03), not an input-handling boundary; there is no path
from these mutants to a document any enforcement code will ever read.

## 6. STRIDE on the guarded control — docs-domain write grant
The witness (`test_docs_domain_grant_is_exhaustive_over_every_persona`, `:243-259`) is a
**Tampering** detector for the artifact `check-domain.sh` consults to decide write authority:
it pins the exact set of personas holding a `docs` glob and the exact glob list for each,
and — per the M1/M2/M3 negative controls — is demonstrated (M1, out-of-process; M2/M3 as
in-file assertions plus source review, matching the panel's own disposition) to redden on an
unauthorized *addition* of a docs grant to any persona and on a *removal* from documentor.
That is a real, working guard against silent grant widening within its lens.

The lens is `mine` only (`hy.manifest_domains(manifest_path, name)`'s first return value,
filtered at `:236-238`) — a docs-segment path arriving via `shared` instead is invisible to
it. Checked this concretely rather than taking the disposition on faith: `SHARED_MANIFEST_PATHS`
in this same file (`:42-52`) — `.harness/*/features/*/quarantine/**`, `package.json`,
`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `pyproject.toml`, `uv.lock`,
`requirements.txt`, `tsconfig.json` — and the real manifest's `shared:` block
(`.harness/team-config.yaml:77-81+`) both carry zero paths with a `docs` segment today, and
`SHARED_MANIFEST_PATHS` is itself asserted equal to the manifest's live `shared:` block by the
pre-existing D-03 equivalence fixture elsewhere in this file — so if a `docs`-segment path
were ever added to `shared:`, that equivalence test reddens first, independent of this
witness. **I agree this does not gate**: the compensating control (the equivalence fixture)
is real, already in the suite, and unrelated in mechanism to the witness being reviewed here,
so the witness's narrower lens is not a single point of failure for that scenario.

## Findings
| id | severity | file:line | note |
|---|---|---|---|
| F1 | info | `tests/integration/test-harness-yaml.py:349` | full parent env forwarded to re-exec'd child; not currently exploitable (no assertion message embeds raw env), but is a latent amplifier if a future test in this file ever logs an env value into an assertion string. |
| F2 | info | `tests/integration/test-harness-yaml.py:340-357` | `subprocess.run` calls added by this diff carry no `timeout=`, matching this file's pre-existing convention (base commit lines 310, 377) — non-gating, CI-availability concern only, not newly introduced. |

`must_fix: []`. Both findings are advisory/info, not gating.

## STRIDE table
| boundary | stride | mitigated |
|---|---|---|
| docs-domain write grant (`.harness/team-config.yaml`) vs `check-domain.sh` enforcement | T (Tampering) | true — exhaustive-over-census witness + demonstrated (M1 out-of-process) reddening |
| docs grant arriving via `shared:` instead of `mine` | T (Tampering) | true — out of this witness's lens, but covered by the pre-existing `shared:` equivalence fixture; precondition (a docs-segment shared path) does not exist today |
| child subprocess stdout/stderr embedding secrets from the fully-forwarded env | I (Information disclosure) | true today (no assertion currently formats raw env), latent if that changes — see F1 |
| CI env vars set to defeat `BUG442_MUTANT_CHILD` guard | S (Spoofing of the recursion signal) | true — requires CI-config-level access, same trust tier as editing the test file |

## Ruled out, not re-litigated
D-01/D-02/D-03 and the SIMPLIFY-skipped findings (ALT-F2, REU-F1, SIM-F1) per the dispatch are
signed/dispositioned; not re-raised here.
