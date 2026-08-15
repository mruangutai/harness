# Review — FEAT-15 domain-product-base — e057525

**BLUF: PASS with notes.** Spec compliance holds (REQ-01..08, SC-01..13 verified; T-05's DEC-189
entry is complete and accurate). One med finding: the `### am.1` block under DEC-174 uses a heading
shape the index generator does not recognize, so `DECISIONS-INDEX.md`'s DEC-174 row silently carries
no amendment marker. No must_fix.

Pin verified: `git merge-base HEAD main` = `812294854160002065a92417761509a3c995e732`, matches the
recorded `review_sha` file. `git diff --stat HEAD` is empty — working tree is exactly `e057525`
bytes, so every command run below (including `gen-decisions-index.py`, `run-unit-tests.sh`) ran
against pinned bytes, not drift.

## Stage 1 — spec compliance

All REQ-01..08 trace to plan tasks; nothing in the diff is unexplained by a REQ/D. SC-10 (green
suite) reproduces: `run-unit-tests.sh` exit 0, `test-check-domain.py` exit 0, 0 FAILs.
`check-plan-routes.py` (tree-wide, T-04's second verify) reports `0 violation(s) across 10 plan(s)`,
exit 0 — the DEVIATION lines for T-01..T-05 are expected (DEC-174 carve-out declared
`main-session-direct` while granted to backend-dev/dev-ops/documentor by glob).

**SC-07** (exactly one expectation flip, two repointings, nothing else): confirmed by diffing every
removed line in `test-check-domain.py` —
```
-case("a shared path is allowed and serialized", f"{ROOT}/package.json", 0)
-    allowed = fire(root, "allowed/thing.md")
-    r4 = fire(root, "allowed/d.md")
```
Exactly the three named changes. No other expectation moved.

**SC-11 / DEC-189** (`docs/harness/DECISIONS.md:5506-5573`, not am.1 — the T-05 entry is its own
heading, `## DEC-189`): states the empty live set explicitly ("The live set of affected files is
EMPTY, stated explicitly rather than omitted"), names all eight `shared:` entries verbatim, and
records `Observed at d0f0ee9` — `d0f0ee9` is in-range. The docs/ dependency claim reproduces:
`git ls-tree -r --name-only e057525 -- docs/ | grep -v '^docs/harness/'` → only `docs/PRINCIPLES.md`.
T-05's verify (`gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md`) exits 0 at the pin.

**SC-08**: the fleet resolve call sits inside `domain_check()`, immediately after the
`harness_yaml.manifest_domains()` try/except (its `DuplicateKeyError`/`YamlParseError` handlers),
under the comment `THE FLEET AND THE BASE (FEAT-15 T-01/T-02, REQ-01 through REQ-06)`, and before the
`if base is None: return` branch — i.e. before any glob is matched and before the former
outside-root bare-return. `domain_check()` itself only runs when `_run_domain and not _no_parser`
(`check-domain.sh:657`), which is two pre-existing gates, not new ones:
- **missing `team-config.yaml`** → `_run_domain=False` → fleet never checked at all. Pre-existing
  DEC-101 fail-open, orthogonal to REQ-03 (which concerns the *fleet* file, not the manifest).
- **a live PyYAML bootstrap-grant session** (`_no_parser=True`) → `domain_check()` skipped, so the
  new fleet-unreadable refusal and the new product-base enforcement are *also* bypassed for that one
  session. This is a real expansion of what DEC-101's spend-once escape now covers (pre-FEAT-15 the
  escape only bypassed harness-base glob checks, since product paths got no verdict either way).
  Not flagged as a violation — DEC-101 already accepts a full domain-check bypass during the one
  bootstrap session — but worth recording since it is new scope for an old accepted risk.

## The four things to attack

**(A) SC-09/REQ-07 — resolve vs hook agreement.** Built the four-outcome comparison with absolute
targets (a fixture fleet, `acme/widget`, `src/**` granted to `harness-backend-dev`):

| target | HOOK exit | RESOLVE exit/stdout |
|---|---|---|
| `<root>/src/main.py` (harness base, refused) | 2 | 0 / `NOBODY` |
| `<ws>/widget/src/main.py` (product base, granted) | 0 | 0 / `harness-backend-dev` |
| `<ws>/undeclared/src/main.py` (workspace, no repo) | 2 | 2 / `` |
| `/tmp/…` (outside both) | 0 | 0 / `NOBODY` |

No cell has the resolver naming an owner the hook refuses, or naming NOBODY where the hook would
grant a persona. The `/tmp` cell looks asymmetric (hook permits silently, resolver still prints
`NOBODY`) but is intended and not a disagreement in SC-09's sense: the hook's "no verdict" means
*not a domain question*, never *someone owns it*; the resolver's contract (DEC-179) is to never be
silent, so it says NOBODY rather than nothing. REQ-05 and DEC-179 are each satisfied on their own
terms.

**Relative-target asymmetry — checked and dismissed.** Confirmed empirically that IF the hook ever
received a relative `tool_input.file_path`, `os.path.abspath(target)` (`check-domain.sh:570`) would
join it against the process cwd while `--resolve` (`:341`) joins against the derived root, producing
real disagreement — reproduced live: same relative string `src/main.py`, cwd set to a product
checkout dir, hook exits 0 (permit) while `--resolve` from the same cwd prints `NOBODY`. But no real
caller reaches this: every case in `test-check-domain.py` fires an absolute `file_path` (matching the
Write/Edit/NotebookEdit tool contract, which requires absolute paths), and `check-plan-routes.py`'s
only relative-path caller (`resolve_agents`, entries from a plan's `files:` list) goes through the
`--resolve` branch, which already resolves relative-against-root correctly. Dropped, no live route.

**(B) SC-12 — `Permitted for you:` line, all 16 personas.** Drove a harness-base refusal
(`<root>/zzz-never-granted-anything/x.md`) through the hook for every persona carrying a `domain:`
list against the live manifest:

```
harness-orchestrator: .harness/features/**, .harness/features/*/notes/answers-*.md, .harness/features/*/notes/ship-review-*.md, .harness/expertise/harness-orchestrator.md, .harness/features/*/observations/harness-orchestrator.md
harness-pm: .harness/features/*/BRIEF.md, .harness/features/*/PLAN.md, .harness/features/*/plan.yaml, .harness/features/*/notes/research-*.md, .harness/notes/research-*.md, .harness/features/*/notes/uat-*.md, .harness/codebase/product-surface.md, .harness/codebase/glossary.md, .harness/expertise/harness-pm.md, .harness/features/*/observations/harness-pm.md
harness-visual-designer: .harness/features/*/DESIGN.md, .harness/features/*/notes/mockups/**, .harness/features/*/notes/prototypes/**, .harness/expertise/harness-visual-designer.md, .harness/features/*/observations/harness-visual-designer.md
harness-documentor: docs/**, README.md, .harness/README.md, .harness/codebase/INDEX.md, .harness/codebase/architecture.md, .harness/features/*/notes/receipt-harness-documentor-*.md, .harness/expertise/harness-documentor.md, .harness/features/*/observations/harness-documentor.md
harness-frontend-dev: .harness/codebase/ui-surface.md, .harness/features/*/notes/receipt-harness-frontend-dev-*.md, .harness/expertise/harness-frontend-dev.md, .harness/features/*/observations/harness-frontend-dev.md
harness-backend-dev: .claude/skills/harness/bin/**, .harness/codebase/api-surface.md, .harness/codebase/domains/**, .harness/features/*/notes/receipt-harness-backend-dev-*.md, .harness/expertise/harness-backend-dev.md, .harness/features/*/observations/harness-backend-dev.md
harness-ai-dev: .harness/codebase/llm-patterns.md, .harness/features/*/notes/receipt-harness-ai-dev-*.md, .harness/expertise/harness-ai-dev.md, .harness/features/*/observations/harness-ai-dev.md
harness-data-engineer: .harness/codebase/data-flows.md, .harness/features/*/notes/receipt-harness-data-engineer-*.md, .harness/expertise/harness-data-engineer.md, .harness/features/*/observations/harness-data-engineer.md
harness-dev-ops: .github/**, .harness/harness.json, .claude/skills/harness/bin/**, .harness/codebase/stack.md, .harness/features/*/notes/receipt-harness-dev-ops-*.md, .harness/expertise/harness-dev-ops.md, .harness/features/*/observations/harness-dev-ops.md
harness-qa: .harness/features/*/notes/qa-*.md, .harness/features/*/notes/review-harness-qa-*.md, .harness/expertise/harness-qa.md, .harness/features/*/observations/harness-qa.md
harness-code-reviewer: .harness/features/*/notes/review-harness-code-reviewer-*.md, .harness/expertise/harness-code-reviewer.md, .harness/features/*/observations/harness-code-reviewer.md
harness-security-reviewer: .harness/features/*/notes/review-harness-security-reviewer-*.md, .harness/codebase/trust-boundaries.md, .harness/expertise/harness-security-reviewer.md, .harness/features/*/observations/harness-security-reviewer.md
harness-ui-reviewer: .harness/features/*/notes/review-harness-ui-reviewer-*.md, .harness/expertise/harness-ui-reviewer.md, .harness/features/*/observations/harness-ui-reviewer.md
harness-product-lead: .harness/features/*/runs/*-product/**, .harness/expertise/harness-product-lead.md, .harness/features/*/observations/harness-product-lead.md
harness-eng-lead: .harness/features/*/runs/*-eng/**, .harness/expertise/harness-eng-lead.md, .harness/features/*/observations/harness-eng-lead.md
harness-validator-lead: .harness/features/*/runs/*-validator/**, .harness/expertise/harness-validator-lead.md, .harness/features/*/observations/harness-validator-lead.md
```

1. **False positive (advertised, can't grant control plane)?** None. Verified each persona's dropped
   glob by hand (e.g. `web/src/**`, `src/**`, `evals/**`, `Dockerfile`, `tests/**` are correctly
   absent for every persona that holds them) — every advertised glob is either `.harness`/`.claude`
   prefixed or genuinely overlaps one of the four named entries (`docs/**`, `README.md`, `.github/**`
   for documentor and dev-ops).
2. **False negative (can grant, omitted)?** The synthetic shape from the dispatch, a mid-path
   wildcard like `docs/*/guide.md`, would indeed be silently dropped by the heuristic overlap test at
   `check-domain.sh:634-636` (it only compares each glob directly against the four literal entries,
   never re-derives from `is_control_plane_target`). No live glob in `.harness/team-config.yaml` has
   this shape — checked every domain entry by hand. Absence of a pin, not a live break: low.
3. **`(no writable domain declared)` for a persona that has one?** Never, for any of the 16 —
   every persona carries at least `.harness/expertise/<name>.md` and
   `.harness/features/*/observations/<name>.md`, both control-plane, so `_advertise` is never empty
   in the harness base for a real persona.

**Workspace/fleet-unreadable messages** (`:250-254`, `:201-207`): both name the target (or fleet
path) and give two concrete fixes or say who repairs the file, satisfying REQ-02/REQ-03. `:250-254`
(no declared repo) does **not** name the persona — `select_base()` takes no `agent` parameter, so it
structurally cannot without a signature change, and "what may this persona write in that base" has no
referent since no base was ever selected. SC-12's general clause literally asks for the persona; the
message is fully actionable without it (the fix — add the repo, or remove the directory — is
persona-independent). **Low**, spec-literal gap only.

**(C) SC-08 edges** — covered above under Stage 1.

**(D) SC-11 / DEC-189 doc** — covered above under Stage 1; fully compliant.

## The two unreviewed items

**`2727dc0` ([harness:human], fleet.yaml + test-no-distribution.py).** The comment at
`fleet.yaml:14-19` claims: "with the entry present, `--resolve` returned NOBODY... with it absent,
`--resolve` exits 2." Re-measured at `e057525` with a fixture fleet toggling `mruangutai/harness` in
`repos:`: **present → exit 0, stdout `NOBODY`; absent → exit 2, "under the factory workspace but
belongs to no repository declared in..."** — comment is **true**. `test-no-distribution.py`'s new
`case3_absence_harness_is_not_a_fleet_member` pairs the absence assertion with a presence assertion
(`repos` count == 1), so it is not a vacuous negative-only check.

**`### am.1` under DEC-174 (`docs/harness/DECISIONS.md:4649`).** MED FINDING. Every other amendment
in this document uses the heading form `### DEC-<N> amendment [<n>] — <title>`
(e.g. `### DEC-171 amendment`, `### DEC-137 amendment 2`, confirmed by grep), which is what
`gen-decisions-index.py`'s `AMEND_HEADING_RE` (`:25`) matches. This block's heading is
`### am.1 (2026-08-11) — three checkout modes...` — matches **neither** `AMEND_HEADING_RE` nor
`AMEND_BOLD_RE` (`:26`), confirmed by running both regexes against the literal line. Consequence:
`DECISIONS-INDEX.md`'s DEC-174 row (`:192`) carries **no `am-span` token**, even though this is a
real, load-bearing ruling (harness removed from its own fleet). **T-05's verify passes vacuously
here** — `gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md` exits 0 only because it proves
the committed index matches what the *blind* generator produces, not that the amendment is indexed
(DEC-169 shape: the presence check the diff performs is real, but it never asked whether the thing it
diffs against is itself complete). Failure scenario: an agent following CLAUDE.md's own instruction
("read `DECISIONS-INDEX.md`, grep it for the surface you are touching") greps for `DEC-174`, sees no
amendment marker, and never opens the section explaining why `mruangutai/harness` is deliberately
absent from `fleet.yaml` — the reasoning is invisible via the documented navigation path, even though
`case3_absence_harness_is_not_a_fleet_member` still blocks the mechanical regression if anyone tries
to re-add the entry. **Med, not high** — the compensating test control means the ruling can't be
silently reversed, only its *rationale* can go undiscovered.

## Stage 2 — code quality

- `resolve_fleet`'s catch (`check-domain.sh:200`) is a bare `except Exception`, not the three named
  types in plan.yaml T-01's intent (`factory_config.FleetError`, `harness_yaml.YamlParseError`,
  `ImportError`) — a literal plan-text deviation, flagged per protocol regardless of merit. Verified
  empirically that every realistic failure (missing `workspace_root`, missing `repos`, broken YAML)
  produces an actionable `FleetError` message, because `factory_config.load_fleet` validates every
  field itself before returning — nothing in the try body can raise a bare `KeyError`. Judged
  **likely beneficial**: a bare catch fails *closed* (exit 2) on any future internal bug in this
  function, where a narrow catch would let an unanticipated exception crash the hook to exit 1, which
  is non-blocking (DEC-100) and would be a worse fail-open — the same pattern this codebase's own
  F-01 comment and DEC-101 carve-out already warn against ("allowing by crash is not allowing").
- `select_base`'s `(None, None, None)` outside-both return: both call sites (`domain_check()` at
  `:573`, the `--resolve` branch at `:345`) check only `base is None` before touching the other two
  return values, and return/exit immediately when it is — safe at both.
- Test comment in `test-bash-write-guard.py` ("Write exits 2, Bash exits 0" for `src/**` granted +
  `<root>/src/main.py`) — re-measured, **true**.
- `test-bash-write-guard.py`, `test-no-distribution.py`, `fleet.yaml` are touched by no plan task's
  `files:` list. Info, not a gate: justified by DEC-174 am.1 as the authority for the human commit,
  and a forced repair for the sibling guard's fixture divergence, explicitly disclosed in the new
  comment rather than silently patched.

## Verdict inputs

No must_fix. Severity max: med (the am.1 heading finding). Everything else is low/info with a stated
reason for not escalating.
