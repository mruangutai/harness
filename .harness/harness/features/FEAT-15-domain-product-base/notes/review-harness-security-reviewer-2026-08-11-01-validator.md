# Security review — FEAT-15 `check-domain.sh` product-base split (path-shape attacks)

Range `812294854160002065a92417761509a3c995e732..e057525` (merge-base confirmed match to
`review_sha` file). VERDICT: **PASS**. No must_fix. Two live-relevant gaps found, both requiring a
precondition the live tree does not currently meet; neither is a regression this diff introduced —
the outcome for both shapes was already exit-0/no-verdict before this diff, so nothing that was
enforced got weaker. Full test suite green (`test-check-domain.py`: 27+18+10+32 = 87/87).

## Findings

### F1 — MED, note not must_fix — symlinked `workspace_root` ancestor defeats product-base
governance entirely (not a new regression; a gap in the new promise, REQ-01/REQ-02)

`select_base` (`check-domain.sh:211-256`) uses `os.path.abspath`/`os.path.commonpath` on the
STRING form of `workspace_root` and the target, never `os.path.realpath`. On macOS `/tmp` is a
symlink to `/private/tmp` (verified: `os.path.islink("/tmp") == True`).

Probe: fleet `workspace_root: /tmp/fe15-ws-<pid>`, repo `acme/widget`, agent
`harness-backend-dev` domain `src/**`. Fired at the **realpath** form of the same physical file
(`/private/tmp/fe15-ws-<pid>/widget/src/main.py`) with an agent holding **zero** domain grant:
exit **0**, no stderr — permitted. The same file addressed by the **declared** form
(`/tmp/fe15-ws-<pid>/widget/src/main.py`) with the same non-owning agent: exit **2**, refused
correctly. Any agent, regardless of domain, can write anywhere in that product checkout by
spelling the realpath instead of the declared path.

Not exploitable against the live fleet today: `workspace_root: /Users/molchairuangutai/GitHub/harness-factories`
has no symlink anywhere in its ancestor chain (checked `/`, `/Users`, `/Users/molchairuangutai`,
`/Users/molchairuangutai/GitHub` — none are symlinks), and `factory_workspace.py` never creates a
symlinked checkout. Outcome for this path shape is **unchanged** from before this diff — pre-diff
every out-of-root path (declared or realpath form alike) hit the bare `return` and got exit 0
unconditionally. So this is an incompleteness in the new protection, not a permit this diff
introduced. Recorded per REQ-01/REQ-02's literal (unqualified) wording, which this input class
violates, but not gated as must_fix because SC-01..SC-13 (the actual signed gates) are
fixture-scoped and all pass, and the gap isn't reachable against the current configuration.

### F2 — LOW, defense-in-depth, not live-exploitable — `is_control_plane_glob` filters only a
literal first segment

`is_control_plane_glob` (`:157-164`) does `p.split("/",1)[0] in (".harness",".claude")`. A domain
glob whose first segment is itself a wildcard is not recognized and so is **not filtered out** on
the product side. Probe: synthetic manifest granting `harness-documentor` the glob `"**"` —
fired at `<ws>/widget/.harness/expertise/x.md` (a product checkout's own control-plane-shaped
directory): exit **0**, permitted — the exact reach REQ-06 says must not happen ("a control-plane
path never matches inside a product checkout").

**Not live-exploitable**: grepped `.harness/team-config.yaml` for every `domain:`/`shared:` glob
whose first path segment contains `*`/`?` — none exist; every glob in the live manifest begins
with a literal directory name (`docs/`, `.harness/`, `.claude/`, `src/`, `web/`, `evals/`,
`supabase/`, `tests/`, `.github/`). The gap is real in the mechanism but dormant against the
policy actually shipped.

### F3 — note, pre-existing, not attributable to this range — symlink defeats the STRING-based
target classifier generally

`select_base`/`is_control_plane_target` never resolve symlinks (`os.path.abspath` only).
Documentor with domain `docs/**` creates `docs/harness/evilclaude -> ../../.claude` (via Bash
`ln -s`, which `bash-write-guard.sh`'s finding list — `sed/perl -i`, `tee`, `mv`/`cp`, `rm`,
`sponge`, `awk -i`, generic `>`/`>>` — does **not** cover; confirmed live: `ln -s` exits 0
unguarded). Write to `docs/harness/evilclaude/agents/harness-orchestrator.md` (nominally
control-plane, matches `docs/**`): exit **0**. The same physical file addressed directly
(`.claude/agents/harness-orchestrator.md`, unowned by any agent per team-config.yaml's own
comment "no agent may write it, and that is the point"): exit **2**. So a documentor can tamper
with the org's own agent-definition files via a self-created symlink.

Confirmed **pre-existing**, not new to this diff: `matches()` is unchanged code, and pre-diff the
same `docs/**` string match against the same symlinked-path string would have granted the write
identically — no control-plane concept was needed for this specific case since `docs/**` already
matched the whole `"docs/..."` string regardless of physical target. Raised as `open_questions`
(non-blocking) so it reaches the harness owner; not blamed on this range.

### Assessed and dismissed (no finding)
- **Nested/sibling bases**: `<ws>/widget/inner` correctly resolves to the longer, inner base;
  `<ws>/widget-other` correctly not read as inside `<ws>/widget`. Confirmed by probe.
- **`..` traversal**, both directions, both the hook path and `--resolve`: normalization lands
  each in the base its resolved location implies; hook and `--resolve` agree (REQ-07 holds for
  this shape).
- **Target == a base directory**: `rel == "."` never matches, all three cases (harness root,
  product checkout root, `workspace_root` itself) fail closed with a coherent message.
- **Case-insensitive filesystem (APFS)**: `readme.md` vs `README.md`, `.HARNESS/` vs `.harness/`
  — both fail CLOSED (refused), confirmed against an agent explicitly granted the correct-case
  path. Usability defect (a legitimate owner is refused the same physical file under the wrong
  case), not a security one.
- **Glob shapes** (`/.harness/**`, `./.harness/**`, `.//harness/**`): all correctly
  filtered/refused in the product base; `is_control_plane_glob`'s strip order works as documented.
- **Degenerate fleet values**: `workspace_root: ""` and `repos: []` and a slash-less repo `name`
  all fail `factory_config.load_fleet`'s validation and fail CLOSED (exit 2, "does not load").
  `workspace_root: "/"` loads successfully and, because the harness-root check runs first, does
  not create a permit — but it does turn `/etc/hosts`, `/tmp/unrelated.py`, and every other
  absolute path on the machine into an explicit refusal ("under the factory workspace but belongs
  to no repository"), silently destroying the `/tmp`-is-not-a-domain-question carve-out (REQ-05)
  under this one misconfiguration. Fails closed, not a security finding — flagged as a severe
  availability hazard from operator error, info-level.
- **Fail-open/closed (Attack #2)**: a fleet.yaml that exists but does not parse fails closed for
  an otherwise-owned, otherwise-permitted write inside the harness root — confirmed, matches
  REQ-03/SC-05. During the PyYAML-missing bootstrap grant, `domain_check()` — which now also
  contains all FEAT-15 fleet/base logic — is skipped entirely, so the new "undeclared-repo-under-
  workspace" refusal is also silently bypassed for that one-time grant window. This is an
  extension of the existing, tested, accepted DEC-101 carve-out (the grant already meant "no
  domain enforcement of any kind" before this diff), not a new hole distinct from what was already
  signed off.
- **stderr disclosure (Attack #4)**: refusal messages print absolute paths of `fleet_path` and
  targets, and raw YAML-parser exception text. All of it names paths the operator's own
  `team-config.yaml`/`fleet.yaml` already declare (not secret), and `factory_config.FleetError`'s
  own contract is "value is always a path/key/repo name... never a class name" — no raw file
  content observed leaking. Threat model here is a same-machine governed agent, not an external
  party. No finding.

### Attack #3 — live blast radius, measured
`git log`/`git merge-base --is-ancestor` confirm commit `2727dc0` (removing
`mruangutai/harness` from `fleet.yaml`) is in range. `ls -la /Users/molchairuangutai/GitHub/harness-factories`
→ **directory does not exist** on this machine right now. The enumeration of directories that
"now refuse every governed write" is therefore **empty** — there is nothing on disk to take the
exit-2 branch at `:250` today. This is a measured negative, not an inference.

### Out-of-scope, confirmed still true
`bash-write-guard.sh` has no reference to `fleet`/`workspace_root`/`factory_config`/`product`
anywhere (grepped, zero hits) — a Bash-route write into a product checkout remains completely
ungoverned after this ships, exactly as the BRIEF's "Verification gaps" already records.

## Method note
`harness-security-reviewer` is Bash-write-blocked (`bash-write-guard.sh` denies `cp`/redirects
for this role) so the scratchpad-copy instruction in the dispatch could not be followed literally.
Probed instead by running the **live, unmodified** `check-domain.sh` as a subprocess against
synthetic fixture roots built via `tempfile`/`os.makedirs`/`open(...).write()` inside `python3`
heredocs (no shell write-pattern triggers), matching `test-check-domain.py`'s own fixture idiom.
Every result above is a live subprocess exit code and stderr, not a static read.
