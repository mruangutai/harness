# Scope review — BUG-285 amended plan, plan-panel cycle 1

## Conclusion

One `high` finding, gating: T-02's DECIDED `except (json.JSONDecodeError, OSError)` clause is
incomplete. It omits `UnicodeDecodeError`, so a non-UTF-8 `feature.json` will crash uncaught into
`factory_cli.run`'s generic handler and print an exception class name — reproducing the exact
issue-#208 shape REQ-06 requires to survive "exactly." No task's `verify:` or any `SC` exercises
that input. Because the clause is marked "DECIDED, do not substitute your own judgement," the
executing engineer cannot fix this without a plan amendment. Everything else in the amended plan —
traceability, dependency order, the three `verify:` blocks as literal shell — is sound.

## Finding

- **severity: high** — T-02's DECIDED except clause `(json.JSONDecodeError, OSError)` in
  `load_factory` omits `UnicodeDecodeError`, so a non-UTF8 feature.json crashes uncaught into
  `factory_cli.run`'s generic handler and prints an exception class name — the exact issue-#208
  regression REQ-06 requires to not happen — and no verify or SC in the plan exercises that input.

  Grounding: today's `load_factory` (`factory_decompose.py:120-123`) wraps
  `harness_yaml.load_file(path)` in `except harness_yaml.YamlParseError`. `load_file`
  (`harness_yaml.py:253-262`) opens with `encoding="utf-8"` and separately catches `OSError` *and*
  `UnicodeDecodeError`, both re-raised as `YamlParseError` — its own docstring names this exact
  failure mode: "a manifest that is not valid UTF-8 … raised straight past every caller's `except
  YamlParseError` — verified live … enforcement silently off." T-02's intent replaces this with an
  explicit open+`json.loads`, but the DECIDED except set is only `(json.JSONDecodeError, OSError)`
  — `UnicodeDecodeError` is a `ValueError` subclass, not an `OSError` subclass, so it is not caught.
  It propagates to `factory_cli.run` (`factory_cli.py:72-93`), whose catch-all prints
  `"unexpected failure: {type(exc).__name__}: {exc}"` — literally the class-name leak REQ-06
  forbids. T-02's own intent misstates this as covered ("OSError is the second arm and covers the
  read failure `load_file` used to absorb on your behalf") — it covers the *read* failure, not the
  *decode* failure, which `load_file` deliberately caught as a second, separate arm. Untested:
  T-03's fixture is a well-formed YAML mapping (valid UTF-8), SC-08's pre-existing case `(1c)` is
  malformed-JSON-and-YAML (also valid UTF-8) — neither exercises encoding failure, and SC-06's
  inspection only greps for the literal catch types being present, not for behavioural completeness.

## Q1–Q7

- **Q1**: Worth doing. The 79-file scan is clean today, but the plan's own Constraints section
  independently forbids duplicate keys and YAML-only syntax in real `feature.json`, so closing the
  latent divergence is real value even with zero current disagreements. Unit + the existing
  integration suite are **not** enough — neither exercises the encoding-failure branch the fix
  itself narrows (see Finding). The duplicate-key loosening (JSON now silently last-wins where
  `harness_yaml` used to refuse) is already named in BRIEF's Constraints/Risk sections; nothing in
  the tree appears to depend on the old refusal, so no separate finding there.
- **Q2**: Mentions, does not fully pin. The inline `python3 -c` probe (T-02 verify, line 3) only
  checks `except SystemExit` fired, not the message; T-03's check 3 does pin `SystemExit` +
  `EXIT_REFUSED` + path-in-stderr, but only for the well-formed-YAML fixture. SC-08 (pre-existing)
  pins it for malformed-both fixtures. Nothing pins it for the encoding-failure branch — see
  Finding.
- **Q3**: No. `harness_yaml.load_file` absorbs `OSError`, `UnicodeDecodeError`, `DuplicateKeyError`
  and general YAML parse errors, all as `YamlParseError`/subclasses (`harness_yaml.py:222-262`).
  T-02's replacement `(json.JSONDecodeError, OSError)` covers the JSON-parse-error and read-failure
  cases but not the decode-failure case. REQ-06's "exactly" does not survive for that one input.
- **Q4**: Yes, correct topological order (`T-03 depends_on: [T-02]`), and T-03's `verify:` runs the
  new unit file plus the unit-kind runner — both exercise `load_factory`'s post-T-02 JSON behaviour,
  which only exists once T-02 has landed. No issue.
- **Q5**: Doesn't change the answer. The self-certification structure (mutation probe delivered
  through note → DIGEST → orchestrator pathspec → git-show grading) is identical for SC-03 and
  SC-09; doubling the count doubles the exposure to the same already-recorded delivery-chain risk
  (open `PF-2242299b…`, disposition `open`) but introduces no new failure mode. Still `info`-level,
  not re-filed here.
- **Q6**: Yes. The rewritten Problem/Risk sections state the measured 79-file/zero-disagreement
  result, both directions of loader disagreement, and both consequences (nothing regresses, nothing
  improves, future duplicate-key/comment documents behave differently) — an operator reading only
  the BRIEF is not misled about scope or blast radius.
- **Q7**: Mostly observable (SC-01/02/03/04/07/08/09/10 assert behaviour, and SC-07/09 explicitly
  forbid asserting a class name). SC-05 and SC-06 are structural/implementation checks by design
  (diff shape, literal catch types) — SC-06 in particular greps for `json.JSONDecodeError` and
  `OSError` being present and `harness_yaml.load_file` being absent, which is exactly the pinning
  that forecloses catching `UnicodeDecodeError` and is why the Finding above is invisible to every
  `verify:`/`SC` in this plan.

## Other checks (no findings)

- REQ-01..08 all trace to a task (T-01/02/03) and every SC-01..10 maps to a task's verify or to
  inspection; no orphan REQ, no orphan `traces:`.
- Dependency shape is a valid topological order; no cycle.
- All three `verify:` blocks read as valid shell/YAML block scalars and execute as written; T-02's
  inline `python3 -c` probe is genuinely discriminating (exit 1 pre-edit on the YAML-only fixture,
  exit 0 post-edit) — checked against the actual `open(..., encoding=...)`/`json.loads` semantics.
- Confirmed `import json` already at `factory_decompose.py:35` and `harness_yaml` still used at
  `:480` for `load_plan` — T-02's claims about existing imports are accurate.
- The two known process defects (stale `approval.status: approved` over a twice-amended task set;
  stale `lanes:` table) are already escalated/recorded (D-05) and not re-reported here.
