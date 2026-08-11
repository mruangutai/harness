# Grilling — issue #239, domain enforcement across the factory's two roots — 2026-08-10

## Destination

An agent writing into a product checkout gets the same domain verdict it would get writing the
equivalent path inside harness: permitted for the persona that owns `src/**`, denied for one that
does not. No path the factory works on is silently ungoverned.

## Settled

- **THE BUILD IS MAIN-SESSION-DIRECT. It may be planned, it may not be dispatched.**
  `check-domain.sh` is a DEC-174 carve-out file. The harness plans its own enforcement layer and
  never executes changes to it — green gates cannot vouch for the code that produces them. Plan
  normally; the operator's main session makes the edits, runs the tests explicitly, and the operator
  reads the diff.

- **Root cause 3 from the ticket is DEAD and drops out of scope.** "The hooks never fire in a product
  repo" required an agent to run with the product checkout as its project dir. It never does: the
  `factory_*` modules spawn no Claude session — they are CLI tools an agent invokes — so every agent
  runs from harness and all seven hooks in `.claude/settings.json` resolve and fire. Absolute-path
  hook registration is not part of this feature.

- **The base each glob resolves against is INFERRED FROM ITS PREFIX, not tagged.** A glob beginning
  `.harness/` or `.claude/` resolves against the harness repo; every other glob resolves against the
  product checkout. No manifest schema change, no 84 entries edited, and it matches how the paths
  already read. **The accepted risk, stated so it is not discovered later: a future control-plane
  path that does NOT begin with those two prefixes would be silently treated as a product path.**
  An explicit `base:` tag per entry and a two-list split were both offered and declined as costing a
  schema change and a tag every future entry must remember.

- **A path under `workspace_root` belonging to no repo in `fleet.yaml` is REFUSED.** `workspace_root`
  is factory territory; a checkout there for an unlisted repo is stale or a mistake, and no persona's
  domain describes writing to it. Fail closed inside the factory's own directory. Declined: treating
  it like `/tmp` and returning no verdict.

- **An unparseable `fleet.yaml` FAILS CLOSED on every write.** Not just on paths under
  `workspace_root` — the hook cannot identify those paths when the value that defines them is the
  thing that failed to parse. This matches what a malformed `team-config.yaml` already does and
  DEC-171's shape for the two `PreToolUse` hooks. A broken rulebook that silently permits is the
  exact failure this ticket exists to remove.

- **`/tmp` and anything outside BOTH bases keep today's no-verdict behaviour.** The reasoning at
  `check-domain.sh:398-404` is sound and `bash-write-guard.sh:211` agrees: blocking a scratch file
  taught an agent to route around a hook whose own message said outside-repo was not its problem.
  A product checkout is not `/tmp`; a scratch file still is.

## Not yet specified

- Whether an ABSENT `fleet.yaml` differs from an unparseable one. A project with no factory has no
  workspace and therefore no product paths, so today's behaviour is already correct there — but the
  distinction should be deliberate and tested, not incidental.
- Where the fleet read happens and whether it is cached within a single hook invocation. It is a
  local YAML read on a hot path; correctness first, but pm should say whether it is read once or per
  candidate path.
- How the product repo's identity is derived from a path — matching `<workspace_root>/<name>/` against
  `fleet.yaml`'s repo names, where `name` is the segment after the owner (`factory_config.py:166-171`
  is the one place that derivation exists and must not be restated).

## Out of scope

- **Absolute-path hook registration** — see root cause 3 above.
- **`factory_workspace`'s missing refusal guard.** Tracked as #240 (P1): different file, different
  failure mode. It must not be folded in here.
- **Reworking `team-config.yaml`'s schema.** The prefix-inference ruling exists precisely to avoid it.
- **`bash-write-guard.sh`.** It has its own outside-repo rule and its own carve-out status. Whether it
  needs the same treatment is a separate question nobody has asked yet.

## Facts I verified (so pm does not re-derive them)

Measured 2026-08-10 at `3569a20`, plus a direct probe of the hook.

- **84 writable domain paths.** 70 are `.harness/**` state, 2 are `.claude/skills/harness/bin/**`,
  and **12 are product-shaped**: `src/**`, `web/src/**`, `tests/**`, `evals/**`,
  `supabase/migrations/**`, `src/**/schema*`, `src/**/prompts/**`, `web/src/**/*.test.*`, `docs/**`,
  `README.md`, `.github/**`, `Dockerfile`.
- **The 12 only appear to work today because harness has its own `src/` and `docs/`.** That accident
  is also the reason prefix inference must not let `src/**` match inside harness when the agent is
  working on a product.
- **Probe, no `CLAUDE_PROJECT_DIR` set, payloads through `check-domain.sh`:**
  `harness-documentor` → a product-repo `src/secrets.py` exits **0**; `harness-code-reviewer` →
  the same path exits **0**; `harness-documentor` → `src/main.py` inside harness exits **2**.
  The same logical path is blocked inside the repo and permitted outside it.
- **The fail-open is `check-domain.sh:406`** — `if commonpath(...) != root: return`, a bare `return`
  with no verdict.
- **The `factory_*` modules spawn no Claude session.** No `Task`, no `Agent`, no `claude` invocation
  in any of them; their only `CLAUDE_PROJECT_DIR` use is `factory_config.py:40-45`, which prefers it
  when a `docs/harness/SPEC.md` probe succeeds and announces a discard on stderr rather than swapping
  silently.
- **`workspace_path` is defined once**, `factory_config.py:166-171`: `workspace_root` joined with the
  repo name AFTER the owner. Both `factory_workspace.py` and `factory_land.py` call it rather than
  restating the rule.
- `.harness/factory/fleet.yaml` declares `workspace_root: /Users/molchairuangutai/GitHub/harness-factories`
  and one repo, `mruangutai/harness`. **The workspace directory does not exist yet** — no factory
  checkout has ever been made, so nothing here was observed in a live factory run.
