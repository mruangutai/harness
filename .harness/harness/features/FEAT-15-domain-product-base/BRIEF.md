# BRIEF — FEAT-15 Domain enforcement across the factory's two roots

## Problem

An agent writing into a product checkout is not governed at all. Measured at `06ae963` with payloads
put straight through the hook: `harness-documentor` writing a product repo's `src/secrets.py` exits
**0**, `harness-code-reviewer` — which owns no source path anywhere and holds no Edit tool — writing
the same file exits **0**, and `harness-documentor` writing `src/main.py` inside harness exits **2**.
The same logical path is blocked inside this repo and permitted outside it. The cause is the
outside-root branch of `check-domain.sh`'s `domain_check()`, whose `commonpath` comparison ends in a
bare `return` — no verdict, no message, no log line. `root` is always the harness repo, so the twelve
product-shaped globs in `.harness/team-config.yaml` describe paths under
`<workspace_root>/<repo>/` that the guard never evaluates. They appear to work only because harness
happens to own a `docs/` and a `README.md` of its own. The operator experiences nothing: no error,
no failed gate, the write simply lands.

## Goal

Harness is the control plane and the only place agents run; product repos live independently, carry
no harness, and are cloned into `workspace_root/<repo>` where agents work on them from a
harness-rooted session. This feature makes the write guard understand that geography: a path inside a
declared product checkout gets the same domain verdict the equivalent path would get inside harness,
a path in the factory's own workspace belonging to no declared repo is refused, and a fleet
declaration that cannot be read stops writes rather than quietly permitting them. Scratch files stay
none of the guard's business.

## Requirements

- REQ-01: An agent writing a file inside a declared product checkout receives the same domain verdict
  it would receive for the equivalent path inside the harness repo — permitted for the persona that
  owns that shape of path, refused for one that does not.
- REQ-02: A write to a path under the factory workspace that belongs to no repository declared in the
  fleet is refused, with a message naming the fleet declaration.
- REQ-03: When the fleet declaration exists but cannot be read as a valid declaration, every governed
  write is refused — not only writes to workspace paths — and the message names the file and says who
  can repair it.
- REQ-04: A project with no fleet declaration behaves exactly as it does today; the absence is a
  deliberate, tested case rather than an accident of error handling.
- REQ-05: A scratch path outside both the harness repo and the factory workspace continues to receive
  no verdict.
- REQ-06: A control-plane path never matches inside a product checkout, and a product-shaped path
  never matches inside the harness repo — except for the four harness-owned paths named in the
  constraints below, which resolve in **both** bases, so harness's own docs, readme and CI keep the
  personas that write them today and a product checkout's equivalents keep theirs.
- REQ-07: The plan-time route resolver and the write-time guard give the same base answer for the
  same path, so a plan cannot be signed on a route the build will refuse.
- REQ-08: The rule the guard now applies, and the risk the operator accepted with it, are recorded
  where the next reader of the decision record will find them.

## Constraints

- **The build is main-session-direct and must not be dispatched.** `check-domain.sh` is a DEC-174
  carve-out file named in `CLAUDE.md`. Every task touching it or `test-check-domain.py` is executed
  directly by the operator's main session, with tests run explicitly and a human reading the diff.
  No build squad is spawned; there is no qa squad on this feature, so every criterion below is
  verified by a command the operator runs.
- **Four rulings are settled and are not re-opened.** (1) The base a path resolves against is
  inferred, with no `team-config.yaml` schema change: `.harness/` and `.claude/` are control-plane,
  everything else is product, **plus four harness-owned paths named explicitly** —
  `docs/harness/**`, `docs/PRINCIPLES.md`, `README.md`, `.github/**`. (2) A path under
  `workspace_root` whose repo is not in the fleet is refused. (3) An unparseable fleet declaration
  fails closed on every write. (4) `/tmp` and anything outside both bases keep today's no-verdict
  behaviour.
- **The four named entries are the operator's verbatim list and the list is closed.** It was measured
  complete against the present tree (checked at `96d5d5c`, unchanged at `f3452bf`): harness has
  `.github/`, `README.md` and `docs/` — and inside `docs/`, everything except `docs/PRINCIPLES.md`
  lives under `docs/harness/` — and has no `src/`, `tests/`, `evals/`, `web/src/`,
  `supabase/migrations/` or `Dockerfile`. `docs/harness/**` is not widened to `docs/**`; no fifth
  entry is added. A future addition is covered by the accepted risk below, not by widening.
- **The rule is two-sided, and stated mechanically because prose is what admits the wrong reading.**
  In the **harness base** every glob is matched, control-plane and product alike, and a match is
  accepted only if the base-relative TARGET is control-plane — its first segment is `.harness` or
  `.claude`, or it matches one of the four named entries. In the **product base** globs whose first
  segment is `.harness` or `.claude` are excluded and the rest match normally; **the four named
  entries play no part on the product side — they are target-side only.** Consequently
  `<harness>/src/main.py` under a `src/**` grant is refused, `<product>/.harness/expertise/x.md`
  under a `.harness/expertise/**` grant is refused, and `docs/**` grants both
  `<harness>/docs/harness/guide.md` and `<product>/docs/guide.md`.
- **The accepted risk, replacing — not removing — the one carried from the grilling, and now
  narrower: this is one more place to remember.** A future harness-owned path that begins with
  neither `.harness/` nor `.claude/` must be added to the explicit list or it silently becomes a
  product path. A per-entry base tag, a two-list split and a `harness:` prefix marker were each
  offered and declined, because each changes the value grammar every future entry must remember.
  **No machinery is added to detect the omission; the operator ruled that out.** This is accepted,
  not fixed.
- The path derivation for a checkout is never restated: `factory_config.workspace_path()` is the one
  place it exists and it is called.
- Planned against the working tree of `chore/203-end-copy-distribution` at `f3452bf`; the original
  probes were taken at `06ae963` and the routing simulation at `96d5d5c`, and `check-domain.sh` and
  `test-check-domain.py` are unchanged across all three. No branch is created and nothing is
  committed — the operator does that at signature.
- **Out of scope:** #240, the `factory_workspace` refusal guard; absolute-path hook registration
  (root cause 3 is dead — the `factory_*` modules spawn no Claude session); reworking
  `team-config.yaml`'s schema; `bash-write-guard.sh`.

## Success Criteria

- SC-01: From one fixture whose fleet declares a repo other than harness, a persona granted a
  product-shaped glob may write that path inside the product checkout, and a persona not granted it
  is refused the same path — both from the same fixture, so neither an allow-all nor a block-all
  guard can pass.
  verify: automated        evidence: integration
- SC-02: With a fixture manifest granting `src/**` only, writing `<harness root>/src/main.py` is
  refused while writing `<workspace>/<repo>/src/main.py` is permitted — the product half of the
  mirror-image bug, asserted as a pair.
  verify: automated        evidence: integration
- SC-03: With a fixture manifest granting a `.harness/**` path, writing it inside the harness root is
  permitted while writing the identically-spelled path inside the product checkout is refused — the
  control-plane half of the mirror-image bug, asserted as a pair.
  verify: automated        evidence: integration
- SC-04: A write under `workspace_root` to a directory naming no repository in the fleet is refused
  with exit 2, and the message names the fleet declaration.
  verify: automated        evidence: integration
- SC-05: With a fleet declaration present but unreadable as a declaration, a write the agent
  otherwise owns **inside the harness repo** is refused with exit 2 and the message names
  `fleet.yaml` — proving the closure covers every write, not only workspace paths.
  verify: automated        evidence: integration
- SC-06: With no fleet declaration at all, that same in-root write is permitted and a
  workspace-shaped path still receives no verdict — asserted against SC-05 in the same test file, so
  absent and unparseable are provably distinct outcomes rather than one error path.
  verify: automated        evidence: integration
- SC-07: The existing outside-both-bases cases — `/tmp`, `/var/folders`, another checkout — still
  exit 0 with no verdict (measured at `96d5d5c`: the live `workspace_root` is
  `/Users/molchairuangutai/GitHub/harness-factories`, and none of the three paths is under it, so the
  new undeclared-repo refusal cannot claim them), and every shape-phase, post-mode and bootstrap case
  that passed at `06ae963` still passes. **Exactly ONE existing expectation is allowed to change**:
  the case `a shared path is allowed and serialized` (`<harness root>/package.json`), which loses its
  serialized-allow because all eight entries in the manifest's `shared:` block are dependency
  manifests and lockfiles with no control-plane prefix and none is among the four named entries.
  The case `documentor writing docs/` (`<harness root>/docs/harness/guide.md`) **keeps exit 0** — the
  ruling's `docs/harness/**` entry is what preserves it, and a flip there is a regression, not a
  permitted change. **Two further existing assertions lose their grant and are repaired by changing
  the PATH, never the expectation**, because each is one half of a pair that stops discriminating if
  both halves assert refusal — a block-all guard would then pass it: the two fixture assertions
  granted by `FIXTURE_MANIFEST`'s product-shaped `allowed/**`, namely `SC-05 pair: permitted allowed
  AND forbidden blocked, one manifest` and `the marker self-unlinks once PyYAML imports again`. Each
  keeps exit 0 on a control-plane path. The disposition of the in-root allow assertions was
  re-derived at `f3452bf` — the count is deliberately unstated, because three readers produced three
  different numbers from it and the phrase never pinned its counting rule; the dispositions below
  are what binds, and each was independently verified; `check-domain.sh` and `test-check-domain.py` are byte-identical to
  `96d5d5c` and the manifest's only change since is one control-plane glob for documentor. Any
  expectation changed beyond the one named above is a regression — stop and report it.
  verify: automated        evidence: integration
- SC-08: The fleet declaration is read once per hook invocation, before the outside-root branch and
  before any glob is matched, so a broken declaration cannot be skipped by a target that does not
  look like a workspace path. A reviewer cites the single call site by its surrounding content, not
  by line number.
  verify: inspection
- SC-09: `check-domain.sh --resolve` and the write path agree on the base for the same product path:
  the resolver names the persona the guard permits, and names nobody for a path the guard refuses.
  verify: automated        evidence: integration
- SC-10: The whole suite is green after the change — `run-unit-tests.sh` exits 0 — so the new base
  logic has not disturbed the shape phase, the post-mode sweep or the bootstrap escape.
  verify: automated        evidence: integration
- SC-11: The operator, reading the decision record after the change, can state exactly which
  harness-repo paths lose a route and which do not: no live harness file loses one, because the four
  named entries carry `docs/harness/**`, `docs/PRINCIPLES.md`, `README.md` and `.github/**`; the loss
  is the eight `shared:` entries, which become product-only in the harness base and are latent
  because no such file exists in this repo today. The entry states the empty live set explicitly
  rather than omitting it, and records the sha it was observed at — the claim rests on nothing in
  `docs/` sitting outside `docs/harness/` except `docs/PRINCIPLES.md`, which is a tree property that
  can move between signature and goal-check.
  verify: inspection
- SC-12: A refusal issued for a product path is readable on its own: the message names the target,
  the persona, what that persona may write in that base, and — for a workspace path belonging to no
  declared repository — the fleet declaration and the two ways to fix it. A reviewer reads the
  emitted stderr of the refusal cases and cites it.
  verify: inspection
- SC-13: The four named entries resolve in **both** bases, asserted from one fixture and one manifest
  that grants `docs/**` and `README.md` to one persona and `.github/**` to another. Inside the
  harness base, `docs/harness/guide.md`, `docs/PRINCIPLES.md`, `README.md` and
  `.github/workflows/tests.yml` are permitted, while `docs/guide.md` — a harness path under `docs/**`
  but under none of the four entries — is refused, proving `docs/harness/**` was not widened to
  `docs/**`. Inside the product checkout, `README.md`, `docs/guide.md` and `.github/workflows/ci.yml`
  are permitted for the same two personas, proving the four entries did not displace the product
  side. **The product half is the assertion nothing else in this feature covers**: the routing
  measurement that produced `0 violation(s)` models in-harness resolution only and is structurally
  blind to it.
  verify: automated        evidence: integration

## Verification gaps

- `test-check-domain.py` is claimed by `harness.json`'s `unit` detect glob
  (`.claude/skills/harness/bin/test-*.py`) but is executed from `run-unit-tests.sh`'s
  `INTEGRATION_SCRIPTS`. Every criterion above names `evidence: integration`, which is the bucket
  that actually runs it. `--kind unit` would report green without executing a single case here.
  The detect/runner disagreement is pre-existing and is raised for the backlog, not fixed here.
- `component`, `ui`, `eval` and `typecheck` have `cmd: null`. None of them covers this surface — the
  change is a Bash-and-Python hook with no UI and no model behaviour — so nothing here rests on a
  null kind.
- **No UAT criterion, deliberately.** `gates.uat` is `blocking_when_uat_criteria_exist`, and the only
  honest UAT here would need a real product checkout under `workspace_root` — which has never
  existed, and which the fleet does not yet declare a second repository for. A blocking gate resting
  on infrastructure nobody has stood up is a gate that cannot pass, so SC-12 is an inspection of the
  refusal text instead. Standing up a second fleet repository and exercising a live refusal is worth
  a backlog item; it is not a condition of this feature shipping.
- **Not proven by anything in this feature:** a write into a product checkout made through Bash.
  `bash-write-guard.sh` keeps its own outside-repo rule and is explicitly out of scope, so that route
  stays ungoverned after this ships.

## Open questions

Q1 is **ruled and retired**: option (c), the four explicit control-plane entries, with no change to
the inference grammar. It is recorded in `## Constraints` above, not here.

- **Q7 — blocking at signature, not blocking the build.** The ruling names four entries; it does not
  say in so many words whether the classifier keys off the manifest **glob** or the resolved
  **target**. This brief and the plan are built on target-keyed: a glob is matched, then the target's
  own base-relative path decides whether the match is accepted. Glob-keying cannot express the
  ruling, and that is checkable rather than arguable — `.harness/team-config.yaml` grants
  harness-documentor `docs/**` and contains no `docs/harness/**` entry anywhere, so a glob-keyed
  classifier has nothing to match two of the four entries against. It is also the semantics the
  operator's clean routing number was measured under: under glob-keying `docs/**` stays product-only
  and FEAT-12 T-12/T-14 and FEAT-14 T-09/T-10 resolve to NOBODY. Correct this reading at signature if
  it is wrong; the plan is built to it either way.
- **Q8 — not blocking.** The four entries are matched anchored against the base-relative target with
  the guard's existing `glob_to_re`/`matches` idiom, so `README.md` means the repository-root readme
  and never `docs/README.md`, and `.github/**` never matches `vendor/.github/x`. Flagged because it
  is the clause that stops the closed list from silently widening later.

## Approval

status: approved
approved-by: operator
date: 2026-08-11
