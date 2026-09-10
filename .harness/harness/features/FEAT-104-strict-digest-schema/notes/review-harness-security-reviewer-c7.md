# Security review — FEAT-104-strict-digest-schema @ 6126ac07 (base abff2a84)

## BLUF
One real gap, in-scope and code-grounded: the new closed-schema enforcement (T-06/T-07, D-11) binds
the `schema_version` floor only at **file creation**. An update write to an **already-created**
`schema_version: 2` run can freely declare `schema_version: 1` in the same payload while smuggling
undeclared step/evidence keys — `check-domain.sh` accepts the write (no comparison against the
on-disk version), and `check-state.sh`'s at-rest sweep only ever reads the *current* value, so the
downgraded run is invisible to the audit forever after. This defeats REQ-02's own stated promise
("binds every run written after the change") for any run, at any time, with an ordinary write the
writer already had permission to make. No fixture in the 507/181/82 new test lines exercises a
version-2-then-1 transition — every existing/update fixture keeps the version constant across
before/after. Remedy lives entirely inside the DEC-174 carve-out (`check-domain.sh` and/or
`check-state.sh`), so I report it rather than fix it. **Route: main-session.**

Everything else examined — the shell bootstrap, the new JSON-schema validation logic itself, the
`validate-digest.py` digest-contract closure, the new schema file, and the instruction-surface/decision
docs — is sound. No injection, no traversal, no secret leakage, no escape-injection, no exit-0
bypass found in those.

## What I examined
- Full `git diff abff2a84 6126ac07` stat (22 code/test files + docs/plan/notes) and the byte-for-byte
  diff hunks of every file in the enforcement/test census named in the dispatch.
- `check-domain.sh` +82: confirmed **zero new bash lines** — every added line is inside the existing
  single Python heredoc (T-13's one-interpreter design), so item 1 (shell quoting/eval/globbing) has
  no new surface to audit; the surrounding bash bootstrap is unchanged by this diff.
- `check-state.sh` +54: same shape, same conclusion — Python-only addition inside the existing heredoc.
- `run-state-schema.json` (new, 76 lines): pure JSON Schema data; `evidence.propertyNames.pattern`
  is `^[a-z][a-z0-9_]*$` — anchored, single-pass, no nested quantifiers, no ReDoS potential against
  attacker-controlled key names.
- `validate-digest.py` +93/-5: read the full diff (PASSTHROUGH/DOCUMENTED_OPTIONAL tables, the
  `optional_fields` merge, the new "undeclared digest key(s)" closure check) and traced how
  `optional_fields` is keyed (`persona` for PASSTHROUGH, `raw_persona` for DOCUMENTED_OPTIONAL) to
  rule out cross-persona field smuggling (e.g. a `harness-code-reviewer` return claiming the
  UI-reviewer-only `mode` field is still flagged as an undeclared key — confirmed by reading the
  keying, not run, since the logic is a straight dict lookup).
- Traced the untrusted-input path for `validate-digest.py`: `parse_digest()` (regex-based field
  extraction, not `yaml.load`) is unchanged by this diff. The shared loader used by `check-domain.sh`
  /`check-state.sh` for `state.yaml`/`plan.yaml` (`harness_yaml.load_file` → `_StrictSafeLoader`, a
  `SafeLoader`/`CSafeLoader` subclass) is also unchanged by this diff — confirmed pre-existing and
  safe (no `yaml.load` with an unsafe loader anywhere in the changed files).
- Path arguments to the new schema-loading code (`os.path.join(sys.argv[3], "run-state-schema.json")`
  in check-domain.sh, `sys.argv[2]` in check-state.sh) resolve to `_selfdir`, derived from
  `BASH_SOURCE[0]` — the script's own directory, never attacker/agent-controlled input. No traversal
  introduced (item 2).
- Every new rejection-message code path: `repr(key)` is used for all attacker-controlled step/evidence
  key names before interpolation into stderr text; Python's `str.__repr__` escapes control characters
  (category Cc, including ESC `\x1b`) as literal `\x` sequences rather than emitting the raw byte, so
  terminal-escape injection via a crafted step/evidence key is not possible (item 3). Exception-path
  messages (`%s: %s" % (type(exc).__name__, exc)`) only fire from schema-file/import/validator
  construction failures — not from attacker-supplied `state.yaml` values — except one case below.
- Fail-open check (item 4, the "can a crafted return exit 0" question): every new branch that could
  raise (`sorted()` over a set of mixed hashable types if a step used a non-string YAML key,
  `jsonschema.iter_errors` raising) is inside the same `try/except Exception` that already denies the
  write on any schema-check failure (`check-domain.sh`) or reports a violation (`check-state.sh`).
  Confirmed by reading the full try/except block: every exit from it, exceptional or not, adds to the
  denial/violation list. No path found where a crafted payload turns an intended-refusal into a silent
  pass. Resource exhaustion: the new validation loops are linear in the size of the payload the writer
  itself is submitting (self-imposed cost, not amplification against a third party); the schema itself
  bounds `evidence` to one level of scalar/array values, so no unbounded recursion is reachable through
  it.
- `tests/integration/fixtures/pre-t04-validate-digest.py.fixture` (2017 lines): a vendored *prior*
  snapshot of `validate-digest.py` itself, written to a tempdir and run as a subprocess only within
  `test-validate-digest.py`'s own T-08 regression check (proving the old, looser validator accepted a
  payload the new, closed one now rejects). Content is repo-controlled and code-reviewed like any other
  checked-in source; it is not reachable from any untrusted input path. Confirmed inert as advertised.
- Instruction-surface diffs (`harness-{eng,product,validator}-lead.md` ×2 runtimes, both `SKILL.md`
  files): prose only, routing an agent's dispatch-question answers to `adequacy_notes`/`evidence`/the
  digest artifact instead of a new digest key. The added hunks are byte-identical between the
  `.claude/agents/*.md` and `.omp/agents/*.md` twins (diffed directly). No processing of untrusted
  input, no security-relevant behavior change.
- `DECISIONS.md`/`DECISIONS-INDEX.md`/`SPEC.md`: DEC-223 documents this feature's own closure and
  explicitly, deliberately names one pre-existing hole — `stop_hook_active` short-circuits
  re-validation on a re-prompted return (`validate-digest.py:1827`, unchanged by this diff, already
  present before abff2a84). This is a previously-accepted, now-documented risk, not a new one; I did
  not add it to must_fix (O-05).
- Full-diff secret/credential grep (`api[_-]?key|secret|token|password|bearer|-----BEGIN|ssh-rsa|AKIA…`)
  — only incidental, unrelated hits ("design token", "coverage tokens" test strings). No leaked
  credentials.

## Finding

**MED-HIGH — schema-version downgrade defeats the closed-schema guarantee this feature introduces.**
`check-domain.sh`'s new `_creating` gate (`not _post and absolute_path is not None and not
os.path.lexists(absolute_path)`) is the *only* thing that ever forces `schema_version >= 2`, and it
fires only when the target file does not yet exist. The closed-step-schema validation block that
follows is gated purely on the **proposed payload's own** `schema_version` (`_valid_version`) — never
on what is currently on disk. So: create a run at `schema_version: 2` (forced, closed schema, as
intended) → later, in an ordinary update write to that same file, submit `schema_version: 1` plus any
undeclared step/evidence key → `_creating` is False (file exists) so the floor never fires, and
`_valid_version` is False (1 < 2) so the closed-schema block never fires either. The write is accepted.
`check-state.sh`'s T-07 sweep is symmetric: it only validates steps when the run's **current**
`schema_version` reads >= 2, so once downgraded the run is silently exempted from the at-rest audit
for the rest of its life, indistinguishable from a legitimate historical version-1 run.

- **Who:** any of the harness team personas that already hold ordinary, sanctioned domain write
  access to their own run's `state.yaml` (that's the normal, expected write path for every team lead).
- **What:** a single update write declaring `schema_version: 1` on a run that was created at
  `schema_version: 2`.
- **Impact:** permanently and silently exits the closed-schema guarantee (REQ-02, D-11, SC-11/SC-15)
  for that run — arbitrary undeclared step keys and malformed `evidence` shapes flow through
  unchecked at write time and unaudited at rest, indistinguishable after the fact from a genuine
  pre-feature legacy run. This is the asymmetry that makes it a real gap rather than the intended
  grandfather clause: **creating** at version 1 is refused outright by the floor, but **downgrading**
  to version 1 after creation is unrestricted — a strictly more powerful bypass than what creation
  itself allows.
- **Verified by static read**, not execution: bash-write-guard.sh correctly refused my own attempt to
  exercise this against a temp fixture (I am read-only per this role, working as designed — see
  `open_questions`). The full 82-line/54-line diffs were read in their entirety twice; there is no
  comparison anywhere in either new block against the schema_version already present on disk, and no
  test in `test-check-domain.py`/`test-check-state.py` constructs a create-at-2-then-update-at-1
  transition (every `_existing_write`/`_run_state` fixture keeps `before`/`after` at the same version).
- **Not covered by an existing decision:** D-11/SC-11/SC-15 talk about the 356 pre-existing,
  never-touched version-1 files staying writable — a different case from a version-2 run being
  downgraded mid-life. Not the `stop_hook_active` hole either (that one is documented and accepted;
  this one is not documented anywhere I found).
- **Remedy** would live in `check-domain.sh` (compare the proposed `schema_version` against the
  on-disk value on non-creation writes, or refuse any decrease) and/or `check-state.sh` — both are
  DEC-174 carve-out files. **route: main-session.**

## Threat model
| boundary | STRIDE | mitigated |
|---|---|---|
| agent-authored `state.yaml` write vs. check-domain.sh closed-schema gate | Tampering | false — schema-version downgrade bypass above |
| agent-authored digest text vs. validate-digest.py closed-key contract | Tampering | true — PASSTHROUGH/DOCUMENTED_OPTIONAL keyed correctly per raw_persona, undeclared-key closure verified |
| crafted step/evidence key vs. operator's terminal (stderr rendering) | Information disclosure / injection | true — repr() escapes control chars |
| run-state-schema.json path resolution | Tampering (path traversal) | true — path built from BASH_SOURCE-derived selfdir, not agent input |
| re-prompted digest vs. Stop-hook re-validation (`stop_hook_active`) | Tampering | false, but precondition-absent for this diff — pre-existing, explicitly documented in DEC-223, not introduced here |

## Answers to the four numbered items
1. **Shell quoting/eval/globbing:** no new bash was added in either script; both diffs are pure Python
   inside the pre-existing single heredoc interpreter. Nothing to flag.
2. **Path escape/traversal/symlink:** the new schema-file path is built from the script's own
   `BASH_SOURCE`-derived directory, never from agent-supplied content. No traversal found.
3. **Echoed attacker content / terminal injection:** all attacker-controlled key names reach stderr
   only through `repr()`, which escapes control characters (including ESC). No raw-byte injection path
   found.
4. **Untrusted parse surface:** `parse_digest()` and `harness_yaml.load_file`'s `_StrictSafeLoader`
   (Safe/CSafeLoader-derived) are both unchanged by this diff and already safe. Every new
   exception-raising branch in the schema-validation code is inside a try/except that still denies the
   write / reports a violation on failure — no crafted input reaches a silent exit 0. New validation
   loops are linear in the writer's own payload size; no amplification vector found. The one real gap
   is the version-comparison omission above, which is an invariant gap, not a parser-safety gap.
