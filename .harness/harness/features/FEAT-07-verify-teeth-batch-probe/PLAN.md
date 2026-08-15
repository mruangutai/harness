# PLAN — FEAT-07 Verify teeth, batched signature, probed environment

## Lanes — resolved here, not at build time

Every task below carries `execution_mode:` (FEAT-06's house style). Three consecutive features
discovered routing mid-build; this declares it up front. Resolved against `.harness/team-config.yaml`
at `4091b36`:

| Surface | Lane | Grant |
|---|---|---|
| `docs/**` | `harness-documentor` | `team-config.yaml:116` |
| `.claude/skills/harness/bin/**` | `harness-backend-dev` / `harness-dev-ops` | `:155`, `:197` |
| `.claude/skills/harness-*/SKILL.md`, `.claude/skills/harness/SKILL.md`, `.claude/commands/harness.md`, `.claude/agents/*.md` | **main session** (declared step) | unowned — nothing in `team-config.yaml` grants them |

T-01 is the one deviation from that table, and D-02 records why.

Re-checked after the Q1/Q2 revision, because two tasks changed their `files:`. T-02 gained
`.claude/skills/harness-tdd-enforcement/SKILL.md` (D-06) and T-01's `files:` is unchanged. The new
path matches the table's third row — `.claude/skills/harness-*/SKILL.md`, main session, ungranted —
so no lane moves and no `execution_mode:` changes. The one consequence is that T-02 and T-04 now
write the SAME file; T-04 runs first and T-02 appends, declared as `depends_on` on T-02.

Re-checked again on the architecture-review revision: T-01, T-02, T-03, T-06 and T-09 changed their
BODIES; not one changed its `files:`. So no lane moves on this revision either, and the shared-file
hazard between T-02 and T-04 is unchanged in shape but now stated as a hard constraint in T-02 (F6).

Re-checked a THIRD time on the D-07 redirect. T-01, T-02, T-03, T-04, T-06 and T-09 changed their
BODIES; **not one changed its `files:`** — the redirect adds a FIELD to surfaces the plan already
edits, not a surface. So no lane moves, no `execution_mode:` changes, and the T-02/T-04 shared-file
ordering is untouched. Re-resolved against `.harness/team-config.yaml` at `4091b36`: the three lane
rows above are byte-identical there (`:116`, `:155`, `:197` re-read, not recalled).

## Decisions

- D-01: **The validator gets a SECOND gate structure — a fail-value gate, separate from the existing
  `n/a` gate — and it covers `suite` as well as `task_verify`.** — rationale: the Settled ruling was
  that `task_verify: fail` *or* `n/a` with `VERDICT: PASS` is rejected, "exactly mirroring `suite`
  under DEC-173". Measured at `4091b36`, that mirror delivers only half: `GATE_FIELDS` is consulted
  **only inside the NULLABLE placeholder branch** (`validate-digest.py:477-484`), so it can only ever
  see `n/a`. The two gates are therefore distinguished by MECHANISM, not by field — `GATE_FIELDS`
  (inside the placeholder branch) answers "declined to report", the new table (outside it) answers
  "reported a failure". **This entry previously said the reverse — that the fail gate was
  `task_verify`-only and the identical `suite: fail` + `PASS` fail-open "stays open (Q2, out of scope
  here)". The user ruled the other way** (answers file Q2): fix it here, in T-01, rather than filing
  it. The reason the reversal is right and the original reading was wrong: shipping a fail gate whose
  table has one field, while an adjacent field in the same dict has the identical hole, leaves the
  next reader to conclude the omission was considered and intended. Tradeoffs: two gate mechanisms
  where the Settled ruling assumed one; a live behaviour change to a gate every squad passes through,
  now stated at BRIEF level rather than buried here; and the blast radius is wider than the Settled
  ruling's language covers, which is why BRIEF carries the four-row table.
- D-02: **The validator half and the fixture half ship as ONE task in the main-session lane**,
  deviating from `team-config.yaml`'s grant of `.claude/skills/harness/bin/**` to `harness-backend-dev`
  (`:155`) and `harness-dev-ops` (`:197`) — rationale: DEC-174's compensating control is a human
  reading the diff, and the diff only vouches for itself if it contains the test that proves it;
  splitting the halves also opens a red-suite window in which every *other* task's `verify:` fails for
  an unrelated reason, because `test-validate-digest.py` is first in `run-unit-tests.sh:6`'s `SCRIPTS`
  list. One task eliminates the window rather than documenting it; tradeoffs: the main session does
  work a member is granted, and the deviation is recorded here because the PLAN template (lines 9-11)
  requires a `## Decisions` entry for any departure from a `team-config.yaml` convention.
- D-03: **`dev-ops` gains `task_verify` in BOTH gate structures and must NOT gain `suite` in EITHER.**
  — unchanged in substance by the Q2 ruling; restated because there are now two structures rather than
  one, and "there" was written when there was only `GATE_FIELDS`. Rationale: the user's ruling removes
  the carve-out for `task_verify` only; `suite: n/a` + `PASS` stays legal for dev-ops because
  `test_matrix` maps config/scaffolding/docs to `[]` (DEC-100), so "no tests apply" is the correct
  outcome, not a dodge (`validate-digest.py:66`). Tradeoffs, and the second is now larger than it was:
  the mental model "dev-ops is exempt from gate fields" becomes wrong, so the comment block at
  `:57-72` has to state that exemption is per-field; and excluding `suite` from the FAIL table as well
  leaves `dev-ops` `suite: fail` + `PASS` ACCEPTED (re-measured at `4091b36`: `digest ok`, exit 0),
  which is a real instance of the defect class this feature closes, left open one persona over.
  DEC-100 justifies the `n/a` half and says nothing about `fail`. The user's call stands and is not
  reopened here; the cost is made visible instead — recorded in BRIEF `## Verification gaps` and
  pinned by the SC-15 fixture, so the next edit to it is deliberate rather than accidental.
- D-04: **The dispatch-carries-`verify:` rule lands in `harness-zero-micro-management/SKILL.md`
  only** — not in `.claude/skills/harness/teams/build.yaml` and not in `.claude/agents/harness-eng-lead.md`.
  Rationale: `build.yaml` already fixes the dispatch-text source with `prompt: from_task_intent`
  (`:60`), and its own comments (`:46-49`) call a config key that no runtime evaluates dead weight, so
  a `verify:`-passing key there would be a comment wearing a key; and a second copy in `harness-eng-lead.md`
  is the inline-drift shape DEC-126 and DEC-158 exist to prevent. Zero-micro is loaded by all three
  leads, so one copy covers every dispatcher; tradeoffs: `harness-eng-lead.md:68` already carries a
  dispatch-prompt rule for the debug flow, so a reader who looks there first finds nothing about
  `verify:`.
- D-05: **The fail gate DOES cover `qa`'s `matrix_ok`, and the table is keyed by per-field failing
  VALUE rather than by field name.** — rationale: this is the explicit ruling the answers file
  requires rather than leaves implied. `matrix_ok` is the project's only blocking gate
  (`harness.json` `gates.qa_gate: blocking`), and `validate-digest.py:63-66`'s own comment calls QA
  claiming it passed when the suite did not run "the audit's worst row". Re-measured at `4091b36`:
  `matrix_ok: false` + `VERDICT: PASS` returns `digest ok`, exit 0. Scoping it out would close the
  fail-open on two string fields and leave it open on the one field the project actually blocks on,
  inside the same commit — an inconsistency a future reader would read as intentional. Tradeoffs, and
  the second is a real cost: (a) the failing value is not uniform — `suite` and `task_verify` fail as
  the string `fail`, `matrix_ok` fails as the boolean `False` (verified: `parse_scalar("false")`
  returns `False`, not `"fail"`), so a gate keyed on "the value is the string `fail`" would silently
  never fire on `matrix_ok`; the table must therefore carry the failing value per field, which is more
  structure than a set of field names; (b) `0 == False` is `True` in Python, so a naive comparison
  would reject `matrix_ok: 0`-shaped values by accident — the comparison must be type-strict, and
  T-01 specifies it.
- D-06: **The REQ-08 receipt clause lands in `.claude/skills/harness-tdd-enforcement/SKILL.md`, one
  copy, and nowhere else.** — rationale: the clause must reach all FIVE dev specialists, and verified
  at source, the obvious home does not. `harness-digest-dev` is preloaded by only four —
  `.claude/agents/harness-dev-ops.md:8-12` lists `harness-handoff`, `harness-expertise` and
  `harness-tdd-enforcement` and NOT `harness-digest-dev` — which is exactly why T-03 exists; a clause
  landing there alone would leave dev-ops uncovered and the ruling unsatisfied. `harness-tdd-enforcement`
  is preloaded by exactly the five and by no one else (`grep -ln harness-tdd-enforcement
  .claude/agents/*.md` returns those five files; `grep -rn tdd-enforcement .harness/team-config.yaml
  .claude/settings.json .claude/skills/harness/bin/` returns nothing, so agent frontmatter is the
  only loader — the path was `.claude/hooks/`, which does not exist in this repo, so the command
  emitted a warning and proved nothing; corrected to `settings.json`, where the hooks are actually
  configured, and re-run at `4091b36`). It is also the topical home: this file already governs "did you actually run the thing that
  proves it", and already carries the worked example T-04 corrects. **On BRIEF's constraint that the
  probe rule "must not land in `harness-handoff` — its lines are paid by all 16 agents at every
  spawn": that precedent is a COST argument, and applying it points here rather than away.**
  `harness-handoff` is where the receipt PATH is already defined (`:71-73`), which is the pull toward
  it; but the receipt path is a rule all 16 agents need, whereas "carry your task's `verify:` command
  and its output" is meaningless to a lead, a reviewer or the orchestrator. Putting it in
  `harness-handoff` would charge 11 agents for a rule they cannot act on — the same arithmetic that
  kept the probe rule out. Tradeoffs: the receipt rule is now split across two files (path in
  `harness-handoff`, content requirement in `harness-tdd-enforcement`), so a reader looking only at
  the path definition does not learn what must be in it — T-02 mitigates by naming the receipt path
  explicitly in the clause rather than saying "your receipt"; and `harness-tdd-enforcement` gains a
  rule about a non-TDD artifact, so its title under-describes it.
- D-07: **The `dev` and `dev-ops` schemas gain a declared `task: T-NN|none` field, and `task_verify`
  binds only when `task` names a real `T-NN`.** — **THE USER'S RULING, taken at the round-2 signature
  gate (`notes/answers-amf-fix-product.md` Q1). It is settled, not a recommendation.**
  **The problem it solves, in outcome terms.** After T-01 lands, a `harness-backend-dev` or
  `harness-dev-ops` dispatched for anything that is NOT a PLAN task cannot return `VERDICT: PASS` at
  all. Omitting `task_verify` is rejected (SC-01). `n/a` + PASS is rejected with no carve-out (SC-03).
  `fail` + PASS is rejected (SC-02). `pass` is a lie — there was no command. **No legal value
  exists.** The architecture review that found this IS that shape: a `harness-backend-dev` returning
  `VERDICT: PASS` with no task and no `verify:` command, accepted only because T-01 has not landed.
  Other live cases: an Expertise distillation, a `harness-systematic-debugging` research pass, any
  lead-issued investigation. `.claude/settings.json`'s `SubagentStop` matcher is `harness-.*`, so it
  fires on every harness agent's stop, not only build steps — the case cannot be dodged by routing.
  **REJECTED ALTERNATIVE, recorded so a future scan does not re-suggest it: a fourth `task_verify`
  value, `no-task`.** It was this entry's own recommendation and it was cheaper — one string in one
  schema set, no new validator logic, no new required field, no fixture rework. **The user's reason
  for rejecting it, recorded verbatim in substance:** `no-task` reinstates a self-declared bypass
  with no receipt obligation, which is structurally the shape the user's own earlier ruling rejected
  one round trip before. This plan said so itself: REQ-08 makes a `pass` show its command and that
  command's verbatim output, while `no-task` obliges nothing at all — there is no command it could
  ever be asked to show. So `no-task` was CHEAPER TO ABUSE than lying with `pass`, and it left
  nothing on the dispatch side to check it against.
  **What the ruling buys, and it is the whole content of the choice:** the escape hatch becomes
  `task: none`, a task-id-shaped string in the same vocabulary T-05 already forces onto the dispatch
  prompt. The audit therefore becomes a string equality between two durable artifacts rather than a
  presence question with nothing on the other side. It is NOT a proof — see BRIEF
  `## Verification gaps`, which states plainly that `task: none` is still self-declared and that
  nothing in `validate-digest.py` reads the dispatch.
  **The cost, ACCEPTED by the user and not re-priced here:** roughly double T-01's diff; a new
  conditional-requirement mechanism in a `SCHEMAS` dict that is flat today, inside a DEC-174 file
  whose only other control is a human reading the diff; and a new REQUIRED field propagating to
  T-02, T-03, T-06 and every dev-persona fixture. The mechanism's own shape is D-08, and D-08 carries
  the fixture obligation that comes with it.
  **Consequences written into this plan:** BRIEF REQ-02 is amended (the exemption axis is the
  dispatch, not the persona) and REQ-10 added; BRIEF SC-17 is REPLACED by the four-branch criterion
  and SC-01..SC-06, SC-07, SC-16 and SC-18 are amended for the conditional; T-03's dev-ops sentence
  is corrected (F1b); T-02's REQ-08 receipt clause is scoped to returns declaring `task: T-NN`
  (F1b); T-02/T-03/T-06 carry the `task: T-NN|none` field alongside the THREE-member `task_verify`
  enum.
- D-08: **The conditional is BIDIRECTIONAL and its `task: none` branch is PINNED here rather than
  left to be discovered: when `task: none`, `task_verify` may be OMITTED or a placeholder (`n/a`),
  and `task_verify: pass` or `fail` is REJECTED as a contradiction.** — rationale: D-07 settles that
  the obligation switches off; nobody had ruled on what happens when a return switches it off and
  then supplies a value anyway, and that is exactly where a conditional mechanism silently fails
  open. Three sub-rulings, each with its reason:
  (a) **Omission is legal when `task: none`.** This is the branch D-07 exists to create.
  (b) **A placeholder is ALSO legal when `task: none`, and the `n/a` gate does not bind there.**
      DEC-121 and the `harness-handoff` skill every agent preloads say a field is never said with
      silence — "an absent field is ambiguous; an explicit empty one asserts you looked". A dev-ops
      on a distillation dispatch will therefore write `task_verify: n/a`, which is the honest
      spelling under the rule it was preloaded with. Rejecting it would tell an agent to violate its
      own contract, so the conditional switches OFF the `GATE_FIELDS` `n/a`-with-PASS rule too: there
      was no gate to decline. The explicit assertion has not been lost, it has MOVED — `task: none`
      is itself the explicit "I looked; there is no task", and it is a required field.
  (c) **`pass` or `fail` with `task: none` is REJECTED, whatever the VERDICT.** Both are
      self-contradictory: the return declares there is no task's `verify:` command and then reports
      that command's result. Accepting either is the fail-open — a dev that DID carry a task, wrote
      `task: none` by mistake or by design, and reported `fail`, would be handed a PASS. Rejecting
      costs nothing legitimate, because (a) and (b) both remain open to an honest return that carries no PLAN task.
  **Mechanism, and it is deliberately the smallest thing that does this:** one `CONDITIONAL =
  {"task_verify": "task"}` dict and one helper that asks whether the governor field says `none`.
  Tradeoffs: (i) it is a genuinely new kind of rule in `SCHEMAS`, which has only flat
  field→allowed entries today, so the file now has two things to understand rather than one — priced
  and accepted at D-07; (ii) it is a fail-open shape by construction, so it carries a fixture
  obligation the flat entries do not: BOTH branches of the conditional must be fixtured, which is
  SC-17(a)-(d) and T-01 step (11) cases (g2)-(j2); (iii) a MISSING governor must bind the
  requirement, not release it — `str(None).lower()` is `"none"` in Python, so a helper written
  `seen.get("task")` instead of `seen.get("task", "")` would silently switch the requirement off for
  every return that omits `task`, which is the exact fail-open this decision exists to close. T-01
  specifies the default and the comment.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-08-04

<!-- RE-PLANNING RESETS THIS. A plan approved for one task set must never carry its
     signature onto a changed one. -->

## Features

- FEAT-07: Verify teeth, batched signature, probed environment
  traces: REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-08, REQ-09, REQ-10, REQ-11
  tasks: T-01, T-02, T-03, T-04, T-05, T-06, T-07, T-08, T-09, T-10

## Tasks

- T-01: Add the gated `task_verify` field AND the fail-value gate to the validator and its fixtures, in one change
  execution_mode: main-session-direct — reason: carve-out (`validate-digest.py` is named in
    CLAUDE.md's DEC-174 list; `test-validate-digest.py` rides with it by D-02). Direct edit, tests
    run explicitly, a human reads the diff.
  depends_on: none
  files: `.claude/skills/harness/bin/validate-digest.py`, `.claude/skills/harness/bin/test-validate-digest.py`
  intent: >
    EIGHT edits in `validate-digest.py`, numbered (1)-(8) below, each independently required — a
    change to the schema alone ships the dev-ops carve-out the user ruled out, and a change without
    (6) ships D-07's field with no conditional behind it.
    (1) `NULLABLE` (`:51-55`): add `"task_verify"`, so `n/a` short-circuits the enum check the way
        `suite` does. Without this a blocked dev cannot report honestly (REQ-03). Do NOT add `"task"`
        — its `none` is a declared answer, not a declined one, and putting it in `NULLABLE` would
        route it into the placeholder branch and out of its own regex check.
    (2) `SCHEMAS` (`:76-91`): add BOTH new fields to the `"dev"` entry (`:81`) AND to the `"dev-ops"`
        entry (`:90`), and to NO other persona. These are separate persona schemas; `ALIAS`
        (`:111-121`) maps the four eng specialists to `"dev"` and `harness-dev-ops` to `"dev-ops"`, so
        both entries are needed to bind all five.
        (2a) `"task_verify": {"pass","fail"}` — a THREE-value field in practice, because `n/a` is
             deliberately NOT an enum member: `NULLABLE` (step 1) short-circuits it before the enum
             check, which is the one mechanism DEC-173 established for "did not happen" and the
             reason the redundant `n/a` member was removed from dev-ops's `suite` (`:85-88`'s
             comment). There is no fourth member — D-07 rejected `no-task`.
        (2b) `"task": TASK_ID_RE` where `TASK_ID_RE = re.compile(r"T-\d+|none")` is defined next to
             `SCHEMAS`. `re` is already imported. This is D-07's field and it is a NEW KIND of schema
             value: every existing entry is either a set or a bare type, so a `re.Pattern` needs its
             own branch in the per-field loop — that is step (3).
             **MEASURED in the interpreter at `4091b36`, not read off the source, because the whole
             "`task` is a real constrained field" claim rests on it and D-05 is the precedent for
             getting this wrong:** `parse_scalar("T-01")` returns the plain string `'T-01'` and
             `parse_scalar("none")` returns the plain string `'none'` (NOT Python `None` — the
             placeholder branch compares strings); `TASK_ID_RE.fullmatch` is `True` for `T-01`,
             `T-1` and `none`, and `False` for `bogus`, `T-`, `t-01` and `''`. **And the trap:
             `isinstance(TASK_ID_RE, set)` is `False`, and it is not `bool`/`int`/`list`/`str`, so
             WITHOUT step (3) a `re.Pattern` falls through every existing branch of the per-field
             loop in silence and `task: bogus` is ACCEPTED.** Verified in the interpreter. That
             silent fall-through is precisely the "unknown key ignored" shape this feature exists to
             remove, so step (3) is not optional polish.
             Use `fullmatch`, not `match` or `search`: `search` would accept `task: not-T-01-really`.
             **AND the containment check that makes a `re.Pattern` safe to put in `SCHEMAS` at all,
             MEASURED rather than assumed:** `grep -n 'SCHEMAS\|\ballowed\b'` returns exactly three
             `SCHEMAS` sites — the definition (`:76`), `schema = SCHEMAS.get(persona)` (`:417`) and
             a KEY-membership test (`:700`, `norm(agent) not in SCHEMAS`) — and every use of
             `allowed` is inside the per-field loop (`:466-513`), with the only `sorted(allowed)`
             (`:503`) already guarded by `isinstance(allowed, set)`. So the per-field loop is the
             ONLY consumer of schema VALUES and there is no usage/help/`--hook` site that would do
             `sorted()` or `join()` over one. This matters because an uncaught `TypeError` in
             `--hook` mode exits 1, and only exit 2 blocks (DEC-100/DEC-122) — the gate would go
             DARK with no signal, which is the fail-open this file's own comment at `:486-492`
             records having been bitten by.
    (3) THE REGEX BRANCH, in the per-field type chain (`:486-521`). Add, as a new `elif` alongside
        `isinstance(allowed, set)` and before the `allowed is str` branch:
        `elif isinstance(allowed, re.Pattern):` -> if `val` is not a string that `fullmatch`es,
        append: "task=<val> is not a task id — write your task's `T-NN` id exactly as your dispatch
        carries it (T-05), or `none` if this dispatch carries no PLAN task." Comment it with the
        measured fall-through above, so the next reader knows the branch is load-bearing rather than
        stylistic.
    (4) `GATE_FIELDS` (`:73`): the target literal is
        `{"dev": {"suite","task_verify"}, "qa": {"suite","matrix_ok"}, "dev-ops": {"task_verify"}}`.
        The `"dev-ops"` key is NEW and carries `task_verify` ONLY — it must not gain `"suite"` (D-03).
        Update the comment block at `:57-72` so it states BOTH axes the exemption now varies along.
        Per FIELD: for `dev-ops`, `suite: n/a` + PASS stays ALLOWED while `task_verify: n/a` + PASS is
        REJECTED. Per MECHANISM: this dict gates only the "declined to report" value; "reported a
        failure" is the separate `GATE_FAIL_VALUES` table below, and `dev-ops` is absent from `suite`
        in BOTH — so `dev-ops` `suite: fail` + PASS stays accepted, deliberately (D-03). Say that in
        the comment rather than leaving it to be rediscovered.
    (5) A NEW TABLE for the fail-value gate, placed immediately after `GATE_FIELDS` (`:73`). The
        existing `GATE_FIELDS` check at `:481` fires only inside the
        `field in NULLABLE and val in PLACEHOLDER_UNSET` branch (`:477`), so it catches `n/a` and never
        `fail` (D-01). Keyed by persona, then by field, to the value that counts as FAILURE for that
        field — NOT a set of field names, because the failing values differ in TYPE (D-05):
        `GATE_FAIL_VALUES = {"dev": {"suite": "fail", "task_verify": "fail"},
        "qa": {"suite": "fail", "matrix_ok": False}, "dev-ops": {"task_verify": "fail"}}`.
        The `dev-ops` entry carries `task_verify` ONLY and must NOT gain `suite` (D-03) — the
        consequence, that `dev-ops` `suite: fail` + `PASS` stays accepted, is deliberate and is
        recorded in BRIEF `## Verification gaps`, not fixed here. Comment the table with the measured
        four-row pre-state and with the reason the values are per-field rather than a shared literal.
    (6) THE FAIL-GATE CHECK, in the same per-field loop. **INSERTION POINT, stated so a literal reading cannot
        get it wrong: immediately AFTER the `continue` at `:485`, and BEFORE the
        `if isinstance(allowed, set):` at `:486`.** Re-measured: `:485` IS that `continue` — it closes
        the `field in NULLABLE and val in PLACEHOLDER_UNSET` branch opened at `:477` — and `:486` is
        the enum branch. An earlier draft of this task said "before the enum branch at `:485`", which
        read literally puts the new check INSIDE the placeholder branch, i.e. inside the very nesting
        that causes the fail-open. There it would be dead code for the string-valued fields (a real
        `fail` never reaches the placeholder branch) and clauses (ii)/(iii) of this task's `verify:`
        would stay at exit 0. It is ADDITIVE: it
        appends an error and must NOT `continue`, so a value that is both a gate failure and a schema
        violation still reports both. Logic: let `expected = GATE_FAIL_VALUES.get(persona, {})` and
        proceed only when `field in expected`, `m` is truthy and `m.group(1) == "PASS"`. The
        comparison must be TYPE-STRICT — `val == expected[field] and isinstance(val, type(expected[field]))`
        — and the reason must be in the comment: `0 == False` is `True` in Python, so a bare
        `val == expected[field]` would fire on `matrix_ok: 0`; `isinstance(0, bool)` is `False`, which
        is what makes the added clause correct (both verified in the interpreter at `4091b36`).
        Do NOT write `val == False` or key the gate on the string `fail` alone: `parse_scalar` renders
        `false` as the BOOLEAN `False` (verified — `parse_scalar("false")` returns `False`), so a
        string-keyed gate silently never fires on `matrix_ok` and SC-14's second half would pass by
        accident while proving nothing. Error message, in the same voice as the existing one:
        "<field>=<val> reports a gate as FAILED, but VERDICT is PASS — a gate that failed cannot have
        passed. Fix until it passes, or return FAIL or BLOCKED."
    (7) THE CONDITIONAL-REQUIREMENT MECHANISM (D-07, D-08). `SCHEMAS` has no conditional machinery
        today; this adds the smallest thing that does the job, and it is the edit the DEC-174 human
        reader must look hardest at.
        (7a) Next to `GATE_FIELDS`, add `CONDITIONAL = {"task_verify": "task"}` — field -> the field
             that GOVERNS its obligation. Comment it: a dispatch carrying no PLAN task has no
             `verify:` command, so `task_verify` cannot be required of it; `task` is what declares
             which case this return is.
        (7b) A one-line helper, `_unbound(field, seen)`, returning True when
             `str(seen.get(CONDITIONAL[field], "")).strip().lower() == "none"` for a field that has a
             governor, and False otherwise. **The `""` default is LOAD-BEARING and must carry its own
             comment: `str(None).lower()` is `"none"` in Python, so `seen.get(gov)` written without
             a default would make a MISSING `task` switch the requirement off — the conditional
             mechanism failing open in its own first line.** Verified in the interpreter. Fail
             closed: no governor value, or any value other than `none`, means the requirement BINDS.
        (7c) In the missing-field branch (`:466-470`), before the hint is built:
             `if field not in seen:` -> `if _unbound(field, seen): continue`. This is D-08(a): with
             `task: none`, omitting `task_verify` is accepted.
        (7d) In the present-field branch, **immediately BEFORE the `field in NULLABLE and val in
             PLACEHOLDER_UNSET` branch at `:477`** — the position matters and a literal reading must
             not get it wrong, because being after it would make D-08(b) unreachable:
             `if _unbound(field, seen):` -> if `val` is a string in `harness_yaml.PLACEHOLDER_UNSET`,
             `continue` (D-08(b): `task: none` + `task_verify: n/a` is the honest DEC-121 spelling and
             the `n/a`-with-PASS gate does NOT bind — there was no gate to decline); otherwise append
             "task_verify=<val> but task=none — a dispatch carrying no PLAN task has no verify:
             command to report on. Omit task_verify or write `n/a`, or name the task's T-NN id in
             `task`." and `continue`.
             The `continue` is deliberate and is D-08(c) made determinate: it short-circuits both the
             enum check and the fail gate, so `task: none` + `task_verify: fail` + PASS produces
             exactly ONE error, and that error names `task` — the actionable field — rather than two
             errors that disagree about what is wrong.
    (8) THE MISSING-FIELD HINT (REQ-11). At `:467-470` a missing field's error is built with
        `hint = "\`none\` if genuinely not applicable" if field in NULLABLE else "\`[]\` if there are
        none"`. After steps (1) and (4), `task_verify` is in BOTH `NULLABLE` and the gate tables, so
        that hint tells an agent to write `none` — which is in `PLACEHOLDER_UNSET`
        (`harness_yaml.py:302`) — and `none` + `VERDICT: PASS` is then rejected by step (4)'s gate.
        And `task` is in NEITHER, so it would inherit "write `[]`", which is a value its own regex
        rejects. FOUR branches, in this order, after step (7c)'s `continue`:
        (8a) `isinstance(allowed, re.Pattern)` -> the hint names a task id and the escape: "your
             task's `T-NN` id exactly as your dispatch carries it, or `none` if this dispatch carries
             no PLAN task". This is `task`'s branch and it is required by REQ-11 exactly as
             `task_verify`'s is.
        (8b) `field in GATE_FIELDS.get(persona, ()) and isinstance(allowed, set)` -> the hint names
             the field's REAL allowed values, derived from the schema rather than hardcoded —
             `sorted(a for a in allowed if isinstance(a, str))` — AND states that what gets rejected
             is a placeholder ALONGSIDE `VERDICT: PASS`. The `isinstance(allowed, set)` guard is not
             decoration: qa's `matrix_ok` is in `GATE_FIELDS` with `allowed is bool`, and `sorted()`
             over a type raises.
             **AND, for a field that is also in `CONDITIONAL`, the hint must name the escape too:**
             "…or omit this field entirely if this dispatch carries no PLAN task and you wrote
             `task: none`". **This clause is what makes the two hints JOINTLY followable and it is
             the defect the redirect introduced, so it is specified rather than left to voice.** A
             digest omitting BOTH new fields emits both hints; hint (8a) offers `none` for `task`
             while hint (8b) demands a real `task_verify` value. An agent following both literally
             gets `task: none` + `task_verify: pass`, which step (7d) then REJECTS — a hint routing
             an agent into a second rejection, which is REQ-11's own defect class re-created by
             REQ-11's fix, and the second round trip is not re-validated (`:691-692`). With the
             escape named, both repair routes validate: `task: none` + omit, or `task: T-NN` +
             `pass`. SC-18(c) and fixture (11)(j2) check it.
        (8c) `field in NULLABLE` -> the existing `none` wording, unchanged.
        (8d) otherwise -> the existing `[]` wording, unchanged.
        **WORDING CONSTRAINT on (8b), and it is not stylistic.** Do NOT write that a placeholder is
        disallowed or is not an allowed value. This branch also fires on a missing `suite` for `dev`
        (`suite` is in `GATE_FIELDS["dev"]`), and `suite: n/a` with `VERDICT: BLOCKED` is LEGAL —
        SC-06 and REQ-03 exist to protect exactly that honest refusal. A hint forbidding placeholders
        outright would be true of a PASS return and false of a BLOCKED one, which is the same defect
        class as F1b in the validator's own guidance. The gate is on the PAIRING, so the hint says so.
        `persona` and `allowed` are both already in scope at `:466-470`.
        Comment it with the loop it closes and with its HONEST LIMIT, in these terms: a re-prompted
        return is NOT re-validated — `:691-692` is `if d.get("stop_hook_active"): return 0` — so a
        hint that names a rejectable value ships the second attempt unvalidated. That passthrough is
        pre-existing and deliberate (`:663-664`, BUILD task 22); this edit stops the hint POINTING at
        it and does not close it. Do not write a comment claiming otherwise.
    Then the fixtures in `test-validate-digest.py`, steps (9)-(12), in the SAME change:
    (9) Add **`task: T-01` AND `task_verify: pass`** to each of the SEVEN dev-persona fixture cases —
        two lines each, not one, because `task` is required of the same schemas. **Anchors
        RE-MEASURED against `test-validate-digest.py` at `4091b36`, because an earlier draft of this
        list and the grilling artifact's list disagreed and neither was right (the file is
        byte-identical between `3bfedc9` and `4091b36` — `git diff --stat` on it is empty — so the
        anchors carry, but they were re-run rather than assumed):** `case()` heads at `:187`, `:290`,
        `:582`, `:717`, `:951` and `:954`, plus the inline digest STRING at `:561-564` inside the
        DEC-156 file-shape test. `:558` is the `_dec156_case(` CALL line, not the digest text — do not
        edit there. `DEV_NA` is defined at `:939` (not `:943`) and is the fixture used by both `:951`
        and `:954`; those two assert the refusal shape, so `DEV_NA` takes `task: T-01` +
        `task_verify: n/a`, NOT `pass` and NOT `task: none` — a refusal is a return that HAD a task
        (REQ-03/SC-06), and writing `task: none` there would silently move it onto the `task: none` branch
        and leave REQ-03 unproven. The count of seven is correct. The grilling artifact's set
        (`:191/:294/:562/:586/:721/:943`) is uniformly +4 and reproduces none of these lines — do NOT
        use it as a cross-check.
        **CONCRETE NUMERIC IDS ONLY, in every fixture and every piped example: `task: T-01`, never
        `task: T-NN`.** `TASK_ID_RE` is `T-\d+|none`, so the placeholder spelling `T-NN` is REJECTED
        — verified in the interpreter. That is correct behaviour (it is the same zero-placeholder
        discipline `harness-tdd-enforcement` already enforces on task ids), and it is stated here
        because every one of these fixtures is piped through the validator and would otherwise go red
        for a reason that has nothing to do with what it tests. Template blocks in T-02/T-03/T-06 are
        NOT piped through anything, so `task: T-NN|none` is the right spelling there and only there.
    (10) Add `task: T-01` and `task_verify: pass` to the dev-ops fixture at `:1043-1044`
        ("dev-ops suite: n/a still accepted"). **It is the ONLY dev-ops fixture in the file, and that
        was ENUMERATED, not assumed:** `grep -n 'dev-ops' test-validate-digest.py` at `4091b36`
        returns exactly two lines, `:1043` (the `case()` name) and `:1044` (its `"harness-dev-ops"`
        persona argument) — one case. A second dev-ops fixture would go red on T-01 for a missing
        required field and nothing else in this plan would catch it, which is the enumeration class
        that already produced two wrong anchor lists in this feature. It must keep passing — SC-04, a
        REGRESSION clause.
        It guards the `n/a` gate, which the widening does not touch, so it does not by itself show the
        widening left dev-ops alone; step (12)(i) is the case that does.
    (11) Add TEN new cases, each named for what it proves:
        Every one of these carries `task: T-01` unless the case is ABOUT `task`. All ten are measured
        ACCEPTED, `digest ok`, exit 0 at `4091b36` — run, not assumed — so each is a detector except
        where labelled otherwise:
        (a) dev `task: T-01` + missing `task_verify` entirely -> REJECTED, message names
            `task_verify`. The `task: T-01` is what makes the requirement bind (SC-01, SC-17a);
        (b) dev `task: T-01` + `task_verify: fail` + `VERDICT: PASS` -> REJECTED;
        (c) dev `task: T-01` + `task_verify: n/a` + `VERDICT: PASS` -> REJECTED;
        (d) dev-ops `task: T-01` + `task_verify: n/a` + `VERDICT: PASS` -> REJECTED (the
            no-carve-out proof);
        (e) dev `task: T-01` + `task_verify: n/a` + `VERDICT: BLOCKED` -> ACCEPTED (the
            honest-refusal shape, SC-06 — a task that EXISTED and was refused);
        (f) a `harness-qa` digest with NEITHER `task` nor `task_verify` -> ACCEPTED, and the same for
            a reviewer digest. **REGRESSION guard, not a detector, and labelled as such:** it is
            green at `4091b36` too (measured: `digest ok`, exit 0). It is the only thing that would
            catch either new field leaking into a persona schema it does not belong to — SC-05's leak
            check, one field wider than before, and a leak nothing else would notice because an extra
            required field only ever makes returns FAIL;
        and FOUR more from D-07, D-08 and REQ-11 — (h2), (i2) and (j2) discriminate, (g2) is honestly
        labelled the regression half:
        (g2) dev `task: none` + `task_verify` OMITTED + `VERDICT: PASS` -> ACCEPTED, and the same for
             dev-ops. REGRESSION half of SC-17(b): it is green today too, because `task` is in no
             schema yet and unknown keys are ignored. It is here to stay green, not to flip. This is
             D-08(a), and the branch REQ-10 exists for;
        (h2) dev `task: bogus` + `VERDICT: PASS` -> REJECTED, message naming `task`; AND dev with
             `task` OMITTED entirely -> REJECTED, message naming `task`. Two cases, not one — the
             first shows `task` is a CONSTRAINED field, the second shows it is a REQUIRED one, and a
             field that is required but unconstrained is exactly the "unknown key ignored" shape that
             made the superseded SC-17's acceptance half vacuous. **This is the CHANGE DETECTOR pair
             for SC-17(d)** (both measured `digest ok`, exit 0 at `4091b36`);
        (i2) dev `task: T-01` + omitting `task_verify` AND omitting no other NULLABLE field ->
             REJECTED, and the message for `task_verify` does NOT contain the substring `genuinely
             not applicable` while it DOES name `pass` and `fail` (SC-18a, step 8b). The "no other
             NULLABLE field omitted" condition is load-bearing, not decoration: another missing
             NULLABLE field emits the old hint in the same error list and the absence assertion would
             false-red. **Plus the second surface the redirect added:** dev omitting `task` ->
             REJECTED, and the message for `task` does NOT contain `if there are none` while it DOES
             name `T-NN` and `none` (SC-18b, step 8a);
        (j2) **THE CONDITIONAL'S BOTH-BRANCH CASE, and the one this whole mechanism most needs.**
             Two halves, both required:
             (j2-i) dev `task: none` + `task_verify: fail` + `VERDICT: PASS` -> REJECTED, message
                    naming `task`. D-08(c), the contradiction gate; measured ACCEPTED, exit 0 at
                    `4091b36`, so it discriminates. Also assert dev `task: none` + `task_verify: n/a`
                    + `VERDICT: PASS` -> ACCEPTED, which is D-08(b) and is what proves the rejection
                    above is about the CONTRADICTION and not about `task: none` refusing all values;
             (j2-ii) JOINT HINT FOLLOWABILITY (SC-18c, step 8b): a dev digest omitting BOTH `task`
                    and `task_verify` is rejected; take the two emitted hints and apply BOTH literally
                    by each of the two routes they license — `task: none` with `task_verify` omitted,
                    and `task: T-01` with `task_verify: pass` — and assert BOTH repairs validate. A
                    conditional requirement whose two hints contradict each other ships the second
                    attempt unvalidated through `:691-692`, and no other fixture would catch it.
    (12) Add THREE more cases for the fail-value gate (D-01, D-05), likewise named for what they prove.
        All three are measured ACCEPTED, exit 0, at `4091b36`, so all three discriminate.
        **THE dev AND dev-ops CASES HERE CARRY `task: T-01` AND `task_verify: pass` TOO, and this is
        NOT a detail — it is the redirect's sharpest trap.** Without them (g) would be rejected by
        the missing-`task` check ALONE and would pass even if step (6)'s fail gate were never
        written, which makes SC-13's proof satisfied by the required-field check rather than by the
        gate it names — the vacuous shape this feature exists to remove; and (i), which asserts
        ACCEPTED, would go RED for a reason that has nothing to do with the residue it pins, taking
        SC-15's guard down with it. Measured at `4091b36` with both fields present: (g) and (i) each
        still return `digest ok`, exit 0, so each is green today for the right reason and flips (or
        stays) for the right reason after T-01. (h) is qa and carries neither field — qa gains
        neither (SC-05).
        (g) dev `task: T-01` + `task_verify: pass` + `suite: fail` + `VERDICT: PASS` -> REJECTED,
            **and the digest must not be rejectable for any reason other than the fail gate, or the
            case proves nothing** (SC-13);
        (h) qa `suite: fail` + `VERDICT: PASS` -> REJECTED, AND qa `matrix_ok: false` +
            `VERDICT: PASS` -> REJECTED. Two cases, not one — they exercise different value TYPES and
            a string-keyed gate would pass the first while silently missing the second (SC-14);
        (i) dev-ops `task: T-01` + `task_verify: pass` + `suite: fail` + `VERDICT: PASS` -> ACCEPTED.
            Name it for the residue it pins, e.g.
            "dev-ops suite: fail + PASS stays accepted — D-03 ruling, NOT a claim it is correct", and
            comment it with a pointer to BRIEF `## Verification gaps`. This is the guard that goes red
            if a later edit tidies `dev-ops` into symmetry with `dev` (SC-15).
    NO EXISTING FIXTURE ASSERTS A CASE THE WIDENED GATE WOULD FLIP — checked, not assumed:
    `grep -n "suite: fail" test-validate-digest.py` returns exactly `:814` and `:831`, and both sit in
    `harness-qa` digests carrying `VERDICT: FAIL`, not `PASS`. `grep -n "matrix_ok: false"` returns
    nothing. So step (6) turns no currently-green fixture red. Re-checked at `4091b36`, where the
    file is byte-identical to `3bfedc9` (`git diff --stat 3bfedc9 4091b36 -- <file>` is empty).
    Run `.claude/skills/harness/bin/run-unit-tests.sh` from the repo root (issue #36: it aborts from
    anywhere else) and read the diff before committing. Validator and fixtures land in one commit —
    SC-11.
  change_type: logic
  verify: >
    From the repo root, all TEN clauses must hold. Each digest below is piped into
    `python3 .claude/skills/harness/bin/validate-digest.py <persona>`; every one is built with
    `printf` so the `\n` escapes are interpreted, and every one carries the full field set for its
    persona plus `open_questions: []`, `files_touched: []`, `expertise_update: []` and
    `artifact: a.md`. **EVERY ONE OF THE TEN was EXECUTED against `4091b36` on this revision, not
    reasoned about.** Labelled per clause, because two of them carry a detector half AND a
    regression half and a blanket label would misdescribe both:
      - CHANGE DETECTORS — (i), (ii), (iii), (v), (vi), (vii), the REJECTION half of (ix), and the
        REJECTION half of (x). Each returned `digest ok`, exit 0 at `4091b36`, so each can only go
        green once the change lands.
      - REGRESSION CLAUSES, not detectors — (iv); (viii); the ACCEPTANCE half of (ix)
        (`task: none` + `n/a` + PASS, which must STAY exit 0 and is what shows (ix)'s rejection half
        is about the contradiction rather than about `task: none` refusing every value); and both
        REPAIR halves of (x), which must stay exit 0.
    Every dev/dev-ops digest carries `task:` with a CONCRETE id (`T-01`), never the placeholder
    `T-NN`, which `TASK_ID_RE` rejects.
    (i) dev-ops, `change_type: config`, `applied: []`, `suite: n/a`, `task: T-01`,
        `task_verify: n/a`, `VERDICT: PASS` -> must exit 1, reason naming `task_verify`. Proves the
        no-carve-out ruling. `task: T-01` is what makes the gate bind at all after D-07.
    (ii) dev (`harness-backend-dev`), `tests_added: 1`, `suite: fail`, `blocked_on: none`,
        `task: T-01`, `task_verify: pass`, `VERDICT: PASS` -> must exit 1, reason naming `suite`.
        This is the Q2 fold (D-01); it is the clause that goes green only if step (6) actually
        widened the gate.
    (iii) qa (`harness-qa`), `suite: pass`, `failures: 0`, `coverage_gaps: []`, `matrix_ok: false`,
        `VERDICT: PASS` -> must exit 1, reason naming `matrix_ok`. The BOOLEAN half (D-05); a gate
        keyed on the string `fail` leaves this at exit 0, so this clause is what catches that error.
        Carries NEITHER new field — qa gains neither (SC-05).
    (iv) `.claude/skills/harness/bin/run-unit-tests.sh` exits 0. Regression clause only — RE-RUN on
        this revision and green at `4091b36` (`10/10 checks passed`, `PASS test-team-catalog.py`,
        exit 0), and it must be green after.
    (v) dev, `tests_added: 1`, `suite: pass`, `blocked_on: none`, `task_verify: pass`,
        `VERDICT: PASS`, and **`task` OMITTED entirely** -> must exit 1, reason naming `task`, AND
        the message for `task` must NOT contain `if there are none` while it DOES name `T-NN` and
        `none`. This is what proves `task` is REQUIRED, plus SC-18(b)'s hint branch (step 8a).
    (vi) dev, same fields but `task: bogus`, `VERDICT: PASS` -> must exit 1, reason naming `task`.
        This is the change detector for D-07's field being CONSTRAINED rather than a free string.
        Without it `task` is precisely the "unknown key ignored" shape that made the superseded
        SC-17's acceptance half vacuous — verified in the interpreter, a `re.Pattern` falls through
        every existing branch of the per-field loop in silence, so this clause is what proves step
        (3) landed.
    (vii) dev, `tests_added: 1`, `suite: pass`, `blocked_on: none`, `task: T-01`, `VERDICT: PASS`,
        and `task_verify` OMITTED — with every other NULLABLE field present, which is a required
        property of the fixture and not a detail: another missing NULLABLE field would emit the old
        hint into the same error list and make the absence assertion below false-red. Must exit 1,
        AND the emitted message must NOT contain `genuinely not applicable`, AND it must name `pass`
        and `fail`. This is SC-01's rejection and SC-18(a)'s hint fix in one run (step 8b), and
        `task: T-01` is what makes the requirement bind.
    (viii) dev, `tests_added: 0`, `suite: pass`, `blocked_on: none`, `task: none`, `task_verify`
        OMITTED, `VERDICT: PASS` -> must exit 0, AND the same shape for dev-ops (`change_type:
        config`, `applied: []`, `suite: n/a`, `task: none`, no `task_verify`, `PASS`) -> exit 0.
        D-07's escape hatch and D-08(a). **A REGRESSION clause by construction, stated so it is not
        mis-sold:** both exit 0 at `4091b36` already, because `task` is in no schema yet and an
        unknown key is ignored. This clause cannot show the field was ADDED; (v) and (vi) are the
        clauses that can. Keep all three — an acceptance clause with no rejection partner is exactly
        the vacuous shape this feature exists to remove.
    (ix) THE CONDITIONAL, BOTH BRANCHES, in one clause because neither half means anything alone:
        dev, `task: none` + `task_verify: fail` + `VERDICT: PASS` -> must exit 1, reason naming
        `task` (D-08(c), the contradiction gate); AND dev, `task: none` + `task_verify: n/a` +
        `VERDICT: PASS` -> must exit 0 (D-08(b)). The second is what shows the first rejects the
        CONTRADICTION rather than rejecting every value under `task: none`, which is the difference
        between a conditional that binds and one that just fails closed on everything.
    (x) JOINT HINT FOLLOWABILITY (SC-18c, step 8b). dev omitting BOTH `task` and `task_verify` ->
        must exit 1; then BOTH repairs the emitted hints license must exit 0 — `task: none` with
        `task_verify` still omitted, and `task: T-01` with `task_verify: pass`. A REGRESSION clause
        in form (both repairs exit 0 at `4091b36` too, since neither field is in a schema yet) but
        the ONLY clause that would catch two individually-correct hints being jointly contradictory,
        which is REQ-11's defect class re-created by REQ-11's fix. It goes red if step (8b) omits the
        `task: none` escape from `task_verify`'s hint.
  traces: REQ-01, REQ-02, REQ-03, REQ-09, REQ-10, REQ-11, D-01, D-02, D-03, D-05, D-07, D-08
  feature: FEAT-07
  status: pending

- T-02: Add `task_verify` and the PLAN cross-check to the canonical dev return contract
  execution_mode: main-session-direct — reason: domain-ungranted (nothing in
    `team-config.yaml` grants this path), issue #20
  files: `.claude/skills/harness-digest-dev/SKILL.md`, `.claude/skills/harness-tdd-enforcement/SKILL.md`
  intent: >
    This is the single canonical copy for the four eng specialists (DEC-126). In the fenced digest
    block, after `suite:` (`:19-20`), add TWO fields, in this order:
    `task: T-NN|none              # the PLAN task id your dispatch carried, verbatim; none ONLY if`
    `                             # this dispatch carries no PLAN task at all`
    `task_verify: pass|fail|n/a   # your TASK's declared verify: command. n/a ONLY if you refused or`
    `                             # were blocked. fail or n/a with VERDICT: PASS is rejected.`
    `                             # Omit this field entirely when task: none — there is no command.`
    Both spellings are D-07's and must match the schema exactly. State in one clause what separates
    the two "nothing ran" cases, because getting it wrong is the whole hazard: `task: T-NN` with
    `task_verify: n/a` means there WAS a task and you did not run its verify — refused or blocked,
    and `VERDICT: PASS` is rejected; `task: none` means there was no task and so no `verify:` command
    exists — a review, a distillation, a research pass, a lead-issued investigation — and it IS
    accepted with `VERDICT: PASS`. State also, in the same clause, why `task` must be verbatim: your
    dispatch carries the task's `T-NN` id (T-05), so what you write here is checkable against it
    after the fact, which is exactly why `task: none` must not be used to mean "I skipped it".
    The `T-NN|none` spelling is the TEMPLATE form and is correct here; a real return writes a
    concrete id such as `T-03`, because the validator rejects the literal `T-NN`.
    Then add a short prose paragraph under the block, in the skill's existing rule-plus-one-clause-of-why
    voice (DEC-158): run your task's `verify:` command before you return; your dispatch prompt carries
    the task id and the command verbatim; cross-check it against that task in
    `.harness/features/<FEAT>/PLAN.md` (you hold repo-wide read — `team-config.yaml:147,161,174,187,202`)
    and return `BLOCKED` naming both strings if the dispatch and PLAN disagree, rather than choosing
    one. The words `BLOCKED` and `PLAN.md` must appear on the SAME line of that clause — the verify
    below asserts it, because `BLOCKED` alone already appears at `:15` and is not discriminating.
    State plainly that `suite` is your own test suite and `task_verify` is the task's declared
    check — they are different questions and a passing suite does not substitute.
    ALSO in this file, the fold's own propagation (same axis as T-10, found the same way): `:20`
    annotates `suite:` with "n/a with VERDICT: PASS is rejected — DEC-173" and says nothing about
    `fail`. After T-01 that understates what the validator enforces for the dev persona (REQ-07).
    Extend that comment so it states that BOTH `n/a` and `fail` with `VERDICT: PASS` are rejected.
    Measured at `4091b36`: `grep -c 'VERDICT: PASS is rejected'` on this file returns exactly 1, so
    the verify clause below keys on it going to >= 2.
    SECOND FILE — `.claude/skills/harness-tdd-enforcement/SKILL.md`, the REQ-08 receipt clause. It
    goes HERE and not in `harness-digest-dev` because that skill reaches only four of the five
    specialists (D-06). APPEND it as a new short section at the END of the file (94 lines at
    `4091b36`), after `## Exemptions` — appending, not inserting, so the worked example at `:66-79`
    that T-04 edits does not shift. It must state, in the skill's rule-plus-one-clause-of-why voice
    (DEC-158): your verification receipt at
    `.harness/features/<FEAT>/notes/receipt-<your-agent-name>-<runid>.md` (the path is defined in
    `harness-handoff/SKILL.md` and the write is already granted to you —
    `team-config.yaml:144,158,171,184,199`) must carry your task's `verify:` command as a copyable
    string AND that command's verbatim output, not a paraphrase and not a summary. **SCOPE, and it is
    part of the clause rather than a footnote (F1b/D-07): this applies WHEN YOU DECLARE
    `task: T-NN`.** A return declaring `task: none` has no `verify:` command to record; its receipt
    carries whatever it did measure. Written without that scope, the clause would demand a command
    that does not exist — the same defect as F1, one surface over. One clause of why:
    `task_verify:` is a self-report, and a scalar cannot be checked by the qa gate or the code
    reviewer, whereas a command and its output can be re-run by anyone who doubts it. NO new artifact,
    NO new grant and NO new reader — the receipt already exists and is already read.
    Do NOT write, in either file, that this makes skipping impossible: output can be fabricated. The
    honest claim, and the one the user signed off on, is that skipping now leaves evidence in a file
    qa, the code reviewer and the user already open. BRIEF `## Verification gaps` states the residue.
    HARD CONSTRAINT ON THE APPEND (F6): the appended section must NOT introduce a second line matching
    `^VERDICT:` into `harness-tdd-enforcement/SKILL.md`. T-04's `verify:` extracts the worked example
    with `awk '/^VERDICT: BLOCKED$/,/^artifact: none$/'`, and `validate()` tail-anchors on the LAST
    `VERDICT:` match, so a second such line makes that range extract the wrong span and report a pass
    or a failure that is about nothing. Measured at `4091b36`: `grep -c '^VERDICT:'` on this file
    returns exactly 1, and it must still return 1 after T-02. This is precisely the hazard the switch
    from a `sed` line range to a text-anchored `awk` range was made to dodge, so do not re-create it
    in the same file. If the receipt clause needs to SHOW a digest, indent it or fence it so no line
    begins with `VERDICT:`.
  change_type: docs
  verify: >
    `grep -c 'task_verify' .claude/skills/harness-digest-dev/SKILL.md` returns >= 3 (measured 0 at
    `4091b36`), AND `grep -q 'PLAN.md' .claude/skills/harness-digest-dev/SKILL.md` exits 0 (measured
    exit 1), AND the cross-check clause names both strings on one line —
    `grep -Eq 'BLOCKED.*PLAN\.md|PLAN\.md.*BLOCKED' .claude/skills/harness-digest-dev/SKILL.md`
    exits 0 (measured exit 1). NOTE: a bare `grep -q 'BLOCKED'` is NOT usable here — `:15` already
    carries `VERDICT: PASS | FAIL | BLOCKED | ESCALATE`, so it exits 0 today and proves nothing.
    SECOND FILE, the receipt clause: on `.claude/skills/harness-tdd-enforcement/SKILL.md`,
    `grep -ci receipt` returns >= 1 AND `grep -ci verbatim` returns >= 1 AND the two ideas are bound
    on one line rather than merely co-present in the file —
    `grep -Eqi 'receipt.*verbatim|verbatim.*receipt' .claude/skills/harness-tdd-enforcement/SKILL.md`
    exits 0. All four counts are 0 at `4091b36` (measured: `receipt` 0, `verbatim` 0, and the paired
    regex 0), so every clause discriminates. The paired regex is the load-bearing one — a file that
    mentions receipts in one place and verbatim in another satisfies the two count clauses while
    leaving the actual requirement unstated.
    FOLD PROPAGATION on the first file: `grep -c 'VERDICT: PASS is rejected'
    .claude/skills/harness-digest-dev/SKILL.md` returns >= 2 (measured exactly 1 at `4091b36`).
    F6 GUARD on the second file: `grep -c '^VERDICT:'
    .claude/skills/harness-tdd-enforcement/SKILL.md` still returns exactly 1. Measured 1 at
    `4091b36`, so this is a REGRESSION clause, not a change detector — it is here because T-04's awk
    range in the same file breaks silently if it becomes 2, and a silent break is what this feature
    exists to catch.
    D-07 FIELD on the first file, RE-WRITTEN for the ruling — the field, not a fourth enum value:
    `grep -q 'task: T-NN|none' .claude/skills/harness-digest-dev/SKILL.md` exits 0 (measured exit 1
    at `4091b36` — `grep -c task_verify` on this file is 0 and `grep -c 'task: T-NN|none'` is 0, so
    neither field is present yet), AND the three-member enum is the one that ships:
    `grep -q 'task_verify: pass|fail|n/a' …` exits 0 while `grep -qi 'no-task' …` exits 1. That last
    clause exits 1 at `4091b36` too, so it is a SCOPE GUARD paired per DEC-169, not evidence on its
    own — it exists because the SUPERSEDED draft of this task instructed writing exactly that
    spelling, and a residual `no-task` on this surface would be a rule file contradicting the schema.
  traces: REQ-01, REQ-04, REQ-07, REQ-08, REQ-09, REQ-10, D-06, D-07, D-08
  feature: FEAT-07
  depends_on: T-01, T-04
  status: pending

- T-03: Add `task_verify` to the dev-ops inline digest block
  execution_mode: main-session-direct — reason: domain-ungranted (nothing in
    `team-config.yaml` grants this path), issue #20
  files: `.claude/agents/harness-dev-ops.md`
  intent: >
    `harness-dev-ops` keeps its digest template inline (DEC-126: a schema with exactly one agent stays
    inline), so it is a propagation site the handed list did not name. In the DIGEST block at `:69-75`,
    after `suite:` (`:73`), add BOTH `task: T-NN|none` and `task_verify: pass|fail|n/a`, with a
    comment stating the asymmetry that is easy to get wrong: `suite: n/a` is legitimate for
    TDD-exempt work and accepted with `VERDICT: PASS`, but `task_verify: n/a` is NOT — it means
    refused or blocked, and with `VERDICT: PASS` it is rejected.
    **CORRECTED after the architecture review (F1b), and the correction is required under the user's
    D-07 ruling exactly as it was under the superseded recommendation — only the spelling changed.**
    An earlier draft of this task instructed writing that "no verify applies" is NEVER the honest
    answer for dev-ops. That sentence is true of a PLAN task and FALSE of a dispatch that carries no
    PLAN task, and dev-ops takes those — a distillation, a research pass, a lead-issued
    investigation. Shipping it would put a false statement into an agent file. Write instead, with
    the boundary explicit: every PLAN task carries a `verify:` with no placeholders, so ON A PLAN
    TASK (`task: T-NN`) there is always a command and `task_verify: n/a` means you refused or were
    blocked; a dispatch carrying NO PLAN task writes `task: none`, OMITS `task_verify` entirely, and
    IS accepted with `VERDICT: PASS`. Name the two `task` values and the three `task_verify` values
    and what separates them, in one clause each, and state the one combination that is a
    contradiction: `task: none` with `task_verify: pass` or `fail` is rejected (D-08), because a
    return cannot both declare no task and report that task's command.
  change_type: docs
  verify: >
    `grep -q 'task_verify: pass|fail|n/a' .claude/agents/harness-dev-ops.md` exits 0 AND
    `grep -q 'task: T-NN|none' .claude/agents/harness-dev-ops.md` exits 0 — BOTH fields, because a
    file naming one without the other documents a schema that does not exist. Both measured exit 1 at
    `4091b36` (and so does the superseded four-member form `task_verify: pass|fail|n/a|no-task`, so
    no spelling of either field is present today). AND the surrounding comment contains the string
    `suite` — `grep -A4 'task_verify' .claude/agents/harness-dev-ops.md | grep -q suite` exits 0
    (measured exit 1 at `4091b36`; the window is 4 lines rather than 2 because the corrected comment
    is longer than the superseded one). AND two SCOPE GUARDS, both exiting 1 at `4091b36` too and
    therefore paired with the presence checks per DEC-169 rather than offered as evidence:
    `grep -qi 'never the honest answer' …` must exit 1 (the superseded draft of this very task
    instructed writing that false sentence) and `grep -qi 'no-task' …` must exit 1 (the superseded
    draft's rejected enum spelling — a residue here would be an agent file contradicting the schema).
  traces: REQ-02, REQ-07, REQ-10, D-03, D-07, D-08
  feature: FEAT-07
  depends_on: T-01
  status: pending

- T-04: Correct the refusal-shaped dev digest in the TDD skill
  execution_mode: main-session-direct — reason: domain-ungranted (nothing in
    `team-config.yaml` grants this path), issue #20
  files: `.claude/skills/harness-tdd-enforcement/SKILL.md`
  intent: >
    The worked example at `:70-72` is a dev digest for a refused, under-specified task
    (`tests_added: 0`, `suite: n/a`, `blocked_on: "T-NN contains a placeholder…"`). Once `task` and
    `task_verify` are required, that example is an invalid digest as printed. Add BOTH
    `task: T-12` and `task_verify: n/a` to the block, and extend the prose at `:80-83` — which
    already explains why `suite: n/a` rather than `suite: pass` is the truthful value — with the same
    point for `task_verify`: you ran no verify because you refused the task, `n/a` is its spelling,
    `task` still names the task because there WAS one, and the accompanying VERDICT is `BLOCKED`,
    never `PASS`. This is the refusal branch, not the `task: none` branch — writing `task: none` here
    would make the example teach the wrong case.
    **A CONCRETE ID IS FORCED, and this is a consequential edit the D-07 redirect caused rather than
    a tidy-up:** this task's `verify:` pipes the example through `validate-digest.py`, and
    `TASK_ID_RE` is `T-\d+|none`, so the literal placeholder `T-NN` is REJECTED (verified in the
    interpreter). Replace the two `T-NN` occurrences INSIDE the fenced digest — the `headline` and
    the `blocked_on` string — with `T-12` as well, so the example reads coherently and is a valid
    digest as printed. `T-NN` outside the fence, in the surrounding prose about placeholder task ids,
    is generic and stays. The irony is worth one clause in the edit: a skill whose subject is
    rejecting placeholder task ids should not print one in its own digest.
    ORDERING: T-02 also writes this file (the REQ-08 receipt clause, D-06). T-04 runs FIRST and edits
    the worked example in place; T-02 then APPENDS its section at the end of the file. Both are
    main-session-direct so they are serialized anyway, but the dependency is declared rather than
    left to luck, and T-04's verify is text-anchored so T-02's append cannot invalidate it.
  change_type: docs
  verify: >
    `grep -q 'task_verify: n/a' .claude/skills/harness-tdd-enforcement/SKILL.md` exits 0 AND
    `grep -q 'task: T-1' .claude/skills/harness-tdd-enforcement/SKILL.md` exits 0 — the second is new
    under the redirect and asserts a CONCRETE id, so a re-introduced `task: T-NN` fails it (both
    measured exit 1 at `4091b36`), AND
    `awk '/^VERDICT: BLOCKED$/,/^artifact: none$/' .claude/skills/harness-tdd-enforcement/SKILL.md | python3 .claude/skills/harness/bin/validate-digest.py harness-backend-dev`
    exits 0. ANCHORED ON TEXT, NOT LINE NUMBERS, deliberately: the earlier drafting of this clause was
    `sed -n '66,79p'`, and T-02 now also writes this file, so any line-number range is one insertion
    away from extracting the wrong block and reporting a pass or a failure that is about nothing. The
    awk form was run at `4091b36` and prints `digest ok`, exit 0 — identical to the sed form it
    replaces, on the same block. The clause is a REGRESSION check, not a change detector: it is
    already green, goes red the moment T-01 lands, and must return to green when T-04 lands. Run it
    AFTER T-01; running it before proves nothing.
  traces: REQ-03, REQ-07, D-07
  feature: FEAT-07
  depends_on: T-01
  status: pending

- T-05: Require the dispatch prompt to carry the task id and the `verify:` command verbatim
  execution_mode: main-session-direct — reason: domain-ungranted (nothing in
    `team-config.yaml` grants this path), issue #20
  files: `.claude/skills/harness-zero-micro-management/SKILL.md`
  intent: >
    Step 2 of "Your loop" (`:19`) currently reads "Spawn that member and delegate — the task, the
    inputs, the paths, the goal." Extend it so the dispatch also carries, verbatim: the task's `T-NN`
    id and the task's `verify:` command exactly as written in `PLAN.md`. One clause of why, in the
    skill's existing voice: `verify:` is not preloaded anywhere in a member's context, so an unquoted
    command is one the member cannot run (the DEC-158 pattern — the dispatch quotes what the member is
    not preloaded with). Add one row to the Red flags table: "I'll paraphrase the verify command" ->
    "The member cross-checks the verbatim string against PLAN and returns BLOCKED on mismatch. A
    paraphrase reads as a mismatch and stops the task." This is the only home for the rule (D-04) —
    all three leads load this skill.
  change_type: docs
  verify: >
    `grep -q 'verify:' .claude/skills/harness-zero-micro-management/SKILL.md` exits 0 (it returns
    nothing at `4091b36`, which is the defect issue #19 names) and
    `grep -q 'verbatim' .claude/skills/harness-zero-micro-management/SKILL.md` exits 0.
  traces: REQ-04, D-04
  feature: FEAT-07
  depends_on: none
  status: pending

- T-06: Update SPEC §8.1 — BOTH the eng-devs bullet and the dev-ops bullet
  execution_mode: squad-dispatched — product squad, `harness-documentor` (`docs/**`,
    `team-config.yaml:116`)
  files: `docs/harness/SPEC.md`
  intent: >
    §8.1 declares the DIGEST schemas NORMATIVE. Two bullets go stale, not one — the handed site list
    named only the first.
    (1) `:1054-1055` (eng devs): add BOTH `task: T-NN|none` and `task_verify: pass|fail|n/a` to the
        field list.
    (2) `:1062-1063` (dev-ops): add the same two fields and, in the same parenthetical style already
        used for `suite`, record the asymmetry — TDD-exempt work reports `suite: n/a`, but
        `task_verify: n/a` means refused or blocked and is rejected alongside `VERDICT: PASS`, while
        `task: none` (this dispatch carries no PLAN task) omits `task_verify` and IS accepted with it.
    The spelling of BOTH fields in BOTH bullets is D-07's and must match the schema exactly, and the
    `task_verify` enum has THREE members, not four — `no-task` is D-07's REJECTED alternative and must
    not appear. §8.1 is NORMATIVE, so a spelling that drifts from `SCHEMAS` is a normative document
    contradicting the validator.
    Change nothing else in §8.1; the qa, reviewer, visual-designer, documentor, lead and orchestrator
    bullets are unaffected and must stay byte-identical.
  change_type: docs
  verify: >
    Each bullet is checked separately, so a correct edit that spills onto an extra line is not
    reddened by an exact-count assertion.
    `awk '/^- \*\*eng devs\*\*/,/^- \*\*qa:/' docs/harness/SPEC.md | grep -c task_verify` returns >= 1,
    AND `awk '/^- \*\*dev-ops:/,/^- \*\*leads:/' docs/harness/SPEC.md | grep -c task_verify` returns
    >= 1, AND `grep -c 'task_verify' docs/harness/SPEC.md` returns >= 2. All three measured 0 at
    `4091b36`. PLUS the same three for the second field, added under the redirect because a bullet
    naming one field and not the other is the stale-field-set defect REQ-07 exists to close: the two
    per-bullet awk ranges piped to ``grep -c '`task:'`` each return >= 1 and the whole-file
    ``grep -c '`task:' docs/harness/SPEC.md`` returns >= 2 — all three also measured 0 at `4091b36`.
    The backtick in the pattern is load-bearing: SPEC lists fields in backticks, and a bare
    `grep -c 'task:'` would match prose. It does NOT match `task_verify:`, which has no colon after
    `task` — verified, the per-bullet `task_verify` and `` `task: `` counts are independent.
  traces: REQ-07, REQ-10, D-07, D-08
  feature: FEAT-07
  depends_on: T-01
  status: pending

- T-07: Batch the user's change requests at the signature gate
  execution_mode: main-session-direct — reason: domain-ungranted (nothing in
    `team-config.yaml` grants this path), issue #20
  files: `.claude/commands/harness.md`
  intent: >
    In §2 "Approvals are yours" (`:39-43`), add the batching rule. It must say, in the file's existing
    imperative voice: when presenting BRIEF.md or PLAN.md for signature, read to exhaustion FIRST —
    collect every change request the user raises in that one review pass, write them all into one
    answers file, and dispatch exactly ONE consolidated fix. Do not send a fix out while the user is
    still reading. Name the cost the user accepted: the first fix goes out later than it otherwise
    would. Name the evidence in one clause (DEC-158 voice, detail stays in DECISIONS): seven serialized
    plan-phase runs at ~$95 on FEAT-03, none of them triggered by a reviewer finding. Add one Red flags
    row: "They've given me one change, I'll start the fix now" -> "A second request while a fix is in
    flight is a second run. Collect the set, then dispatch once." Do NOT add an escape hatch for an
    urgent independent request — see BRIEF ## Constraints; its shape cannot be stated sharply yet.
  change_type: docs
  verify: >
    `grep -q 'consolidated fix' .claude/commands/harness.md` exits 0 and
    `awk '/^## 2\./,/^## 3\./' .claude/commands/harness.md | grep -qi 'one review pass'` exits 0 — the
    rule is inside §2, not appended elsewhere. Both fail at `4091b36`.
  traces: REQ-05
  feature: FEAT-07
  depends_on: none
  status: pending

- T-08: Add the probe-don't-infer rule to the two tiers that relay claims to the user
  execution_mode: main-session-direct — reason: domain-ungranted (nothing in
    `team-config.yaml` grants this path), issue #20
  files: `.claude/commands/harness.md`, `.claude/skills/harness/SKILL.md`
  intent: >
    The same rule, sized to each surface, and to these two files ONLY — explicitly not
    `.claude/skills/harness-handoff/SKILL.md`, whose lines are paid by all 16 agents at every spawn.
    (1) `.claude/commands/harness.md`: a short rule in §4 "Relay on return", before the routing table
        or immediately after it — when a claim you are about to relay rests on how the runtime
        environment RESOLVES something (which copy of a file executes, which cwd a hook sees, which
        binary is on PATH) and a probe is bounded — a single additive line, a byte-identical revert,
        one suite re-run — run the probe BEFORE relaying. A file-difference check cannot answer a
        resolution question. Add one Red flags row: "The evidence points one way, I'll relay it" ->
        "Adjacent evidence is not a measurement. If a five-minute probe settles it, it is not optional."
    (2) `.claude/skills/harness/SKILL.md`: the same rule for the orchestrator, placed in "The question
        round-trip" (`:115-121`) — before returning `awaiting_user` with an environment-resolution
        question, or answering one from context you hold, probe it if the probe is bounded. A question
        a measurement can close is not a question for the user.
    Both carry one clause of why, not the incident (DEC-158): inferring one such question cost a
    working day and two retracted claims, and the measurement disproved the inference.
    BOTH rules must contain the literal string `before any claim` — the verify below keys on it,
    because the word "probe" alone already appears in `harness/SKILL.md:156` in an unrelated sense
    and would make the check non-discriminating.
  change_type: docs
  verify: >
    A bare `grep -i probe` is NOT usable on `harness/SKILL.md` — `:156` already reads "Probe edits you
    make while…", so it exits 0 today (measured: `grep -ci probe` returns 1). Use the discriminating
    phrase. Whatever wording lands MUST contain the literal string `before any claim`, then:
    `grep -qi 'before any claim' .claude/commands/harness.md` exits 0 AND
    `grep -qi 'before any claim' .claude/skills/harness/SKILL.md` exits 0 — both measured 0 matches at
    `4091b36` — AND `grep -ci 'before any claim' .claude/skills/harness-handoff/SKILL.md` returns 0.
    That last clause returns 0 today as well, so it is a scope guard, not evidence; SC-10 says so.
  traces: REQ-06
  feature: FEAT-07
  depends_on: T-07
  status: pending

- T-09: Record the three decisions and regenerate the index
  execution_mode: squad-dispatched — product squad, `harness-documentor` (`docs/**`,
    `team-config.yaml:116`)
  files: `docs/harness/DECISIONS.md`, `docs/harness/DECISIONS-INDEX.md`
  intent: >
    Append three entries to `docs/harness/DECISIONS.md` in its existing entry format, taking the next
    free numbers — confirm them against the file's tail rather than trusting the index; at `4091b36`
    the last entry is `## DEC-174` at `:4680` (`DECISIONS.md` is byte-identical to `3bfedc9`), so they
    are expected to be DEC-175, DEC-176, DEC-177.
    (1) The gated `task_verify` field, the `task` field that governs it, AND the fail-value gate they
        arrived with — one entry, because they ship in one commit and each is unintelligible without
        the others. It must record:
        **the `task: T-NN|none` field and the conditional (D-07, D-08), with the load-bearing reason
        a future scan does not re-litigate it:** a fourth `task_verify` value `no-task` was the
        cheaper option, was recommended, and was REJECTED by the user because it reinstates a
        self-declared bypass with NO receipt obligation — REQ-08 makes a `pass` show its command and
        verbatim output while `no-task` obliges nothing, so it was cheaper to abuse than lying.
        `task: none` is still self-declared, and the entry must say so; what it buys is a
        task-id-shaped string in the same vocabulary the dispatch already carries (T-05/DEC-176's
        neighbourhood), so the audit is a string equality between two artifacts rather than a
        presence question with nothing on the other side. Record D-08's three sub-rulings and their
        reasons — omission legal, placeholder legal and the `n/a` gate not binding (DEC-121 makes
        `n/a` the honest spelling an agent is preloaded to write), `pass`/`fail` rejected as a
        contradiction — and the interpreter fact that makes the mechanism fail closed:
        `str(None).lower()` is `"none"`, so a missing governor must not release the requirement.
        Then: what `task_verify` is and that it binds all five specialists with no dev-ops carve-out; the
        measured fact that `GATE_FIELDS` is consulted only inside the NULLABLE placeholder branch and
        so gates "did not run" but never "ran and failed"; that the new gate is therefore a SECOND
        structure distinguished by mechanism, not by field, and covers `suite` for `dev` and `qa` and
        `matrix_ok` for `qa` (D-01, D-05); that its table is keyed to a per-field failing VALUE
        because `matrix_ok` fails as boolean `False` while the others fail as the string `fail`, and
        that the comparison is type-strict because `0 == False`; and, as the load-bearing reason a
        future scan does not re-litigate it, that `dev-ops` was deliberately EXCLUDED from both gate
        structures for `suite` (D-03, DEC-100) with the acknowledged consequence that `dev-ops`
        `suite: fail` + PASS remains accepted — residue, recorded in FEAT-07's BRIEF, not an oversight.
        Also record the behaviour change plainly: three persona/field combinations that returned
        `digest ok` at `4091b36` now fail closed.
        This entry ALSO carries the D-06 placement rationale, because a per-feature PLAN is not a
        durable record and this is a textbook re-litigation target — a future scan will ask why the
        receipt rule is not in `harness-digest-dev` with the rest of the dev contract. The
        load-bearing answer, and the only part that must survive: `harness-digest-dev` is preloaded by
        FOUR specialists, `harness-tdd-enforcement` by exactly the FIVE, so the obvious home would
        have silently missed `harness-dev-ops`. Record it as a rule about preload coverage, not as
        this feature's story. Kept inside entry (1) rather than made a fourth entry so the count stays
        THREE, matching SC-12 and T-09's own `DEC-17[5-7]` grep.
    (2) The signature-gate batching rule: the main session collects all change requests from one
        review pass and dispatches one consolidated fix, with the FEAT-03 cost as the evidence and
        "no escape hatch yet, because nobody has hit the case" recorded as a deliberate omission.
    (3) The probe rule: bounded runtime-environment questions are measured before any claim is relayed,
        scoped to `.claude/commands/harness.md` and `harness/SKILL.md`, and explicitly NOT
        `harness-handoff` — record the 16-spawn preload cost as the load-bearing reason so a future
        scan does not re-suggest it.
    PRECONDITION — RUN THIS FIRST, BEFORE EDITING ANYTHING, AND RECORD ITS EXIT CODE IN YOUR RECEIPT:
    `python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - docs/harness/DECISIONS-INDEX.md; echo $?`
    **The precondition is now KNOWN-CLEAN, not conditional, and the branching wording an earlier
    draft carried is dead weight and has been removed.** The drift was committed on its own at
    `4091b36`, BEFORE any feature branch, with the measurement in the commit message: 57 of 174 rows,
    all `@NNNN` anchors, all delta exactly +6, run beginning at DEC-118, `DECISIONS.md` unchanged.
    RE-MEASURED here rather than relayed: at `4091b36` the command above exits 0, and
    `git status --short` shows `docs/harness/DECISIONS-INDEX.md` clean. Run it anyway and record
    "precondition exit 0" in your receipt — that is what SC-12's reporting half checks, and a
    receipt that asserts a state it did not measure is the defect this whole feature is about.
    If it unexpectedly exits 1, it is PRE-EXISTING drift, NOT yours and NOT a defect in this task:
    record the exit code, the number of differing rows and one differing row in full, then proceed.
    You cannot regenerate the index and leave drift unabsorbed — the generator rewrites every anchor
    row, so there is no such variant; what is required is not absorbing it SILENTLY.
    Then regenerate the index — `python3 .claude/skills/harness/bin/gen-decisions-index.py`. The index
    is GENERATED except the ruling text after ` :: ` (its header, `:2-3`), so authoring rows by hand is
    a hand-edit of a generated file. Write the ruling text, run the generator, in the same commit as
    the entries (`DECISIONS-INDEX.md:14`).
  change_type: docs
  verify: >
    `python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - docs/harness/DECISIONS-INDEX.md`
    exits 0 (the index on disk IS the generator's own output), and
    `grep -c '^- DEC-17[5-7] ' docs/harness/DECISIONS-INDEX.md` returns 3 (RE-MEASURED at `4091b36`:
    0. The earlier two-base wording is gone with the drift — at `4091b36` there is ONE base, the
    committed tree, and `git status --short` is clean of this file).
    DIAGNOSTIC: the first clause exits 0 at `4091b36` BEFORE any edit, so it is a REGRESSION clause,
    not a change detector — only the second discriminates. A red FIRST clause after T-09 therefore
    means exactly one thing, and it does not name a cause it cannot know: **the index on disk is not
    the generator's current output.** The two ways that happens are a hand edit and a `DECISIONS.md`
    edit made after the generator was last run — re-run the generator and re-diff to tell them apart.
    HISTORICAL NOTE, kept because the correction cost a retraction: an earlier draft of this clause
    asserted exit 0 at `3bfedc9`; re-measured, it exits 1 there. The row was true only of a working
    tree in which the generator had already been re-run undeclared. That drift is now committed at
    `4091b36` and the ambiguity with it.
  traces: REQ-01, REQ-05, REQ-06, REQ-09, D-07, D-08
  feature: FEAT-07
  depends_on: T-01, T-07, T-08
  status: pending

- T-10: State the widened fail gate on the two `qa` return-contract surfaces
  execution_mode: main-session-direct — reason: domain-ungranted (nothing in
    `team-config.yaml` grants these paths), issue #20
  files: `.claude/agents/harness-qa.md`, `.claude/skills/harness-verification-rules/SKILL.md`
  intent: >
    Found by re-deriving propagation against the FOLD rather than against the new field — a different
    axis, and the reason this task was not in the first-pass plan. Both files were correctly ruled OUT
    as `task_verify` sites (qa never gets that field) and both are IN as fail-gate sites, because both
    document qa's `suite` and `matrix_ok` and both now understate what the validator enforces (REQ-07).
    Each carries the identical comment today — `harness-qa.md:71` and
    `harness-verification-rules/SKILL.md:90`: "n/a ONLY if the matrix could not be evaluated; n/a with
    VERDICT: PASS is rejected — DEC-173". That says the `n/a` half and nothing about the `fail` half,
    which is exactly the superseded-field-set defect REQ-07 names, one axis over.
    In BOTH files, in the fenced qa DIGEST block, extend the annotations so they state the fail rule
    as well, in each file's existing comment voice:
    (1) on `matrix_ok` — after the existing `n/a with VERDICT: PASS is rejected — DEC-173` line, add
        that `false` with `VERDICT: PASS` is ALSO rejected. It is the project's only blocking gate.
    (2) on `suite` (`harness-qa.md:69`, `verification-rules/SKILL.md:87`) — these carry NO gate note
        at all today, only "n/a ONLY if the suite could not be run at all". Add that both `n/a` and
        `fail` with `VERDICT: PASS` are rejected.
    Change nothing else in either block; qa's field SET is unaffected by this feature — qa does not
    gain `task_verify` (SC-05), and adding it here would be the leak SC-05 exists to catch.
    NOT a site, checked rather than assumed: `docs/harness/SPEC.md`'s §8.1 qa bullet (`:1055`) lists
    field NAMES only and states no gate rule, so it does not go stale and T-06's instruction to leave
    it byte-identical stands. `SPEC.md:1075` ("qa `suite: fail` -> loop back to the dev") is routing,
    not a digest example, and is unaffected.
    NO documented worked example anywhere prints `suite: fail` or `matrix_ok: false` alongside
    `VERDICT: PASS`, so unlike T-04 the fold invalidates no printed example — verified by
    `grep -rn "suite: fail\|matrix_ok: false" docs/ .claude/agents/ .claude/skills/ .harness/`, whose
    only rule-surface hit is that SPEC routing line.
  change_type: docs
  verify: >
    On BOTH `.claude/agents/harness-qa.md` and
    `.claude/skills/harness-verification-rules/SKILL.md`, within the fenced qa DIGEST block:
    `grep -c 'VERDICT: PASS is rejected' <file>` returns >= 2 (measured EXACTLY 1 in each file at
    `4091b36` — the single `matrix_ok` `n/a` line — so >= 2 discriminates and a bare `>= 1` would
    not), AND `grep -Eqi 'fail.*(with )?VERDICT: PASS is rejected|false.*VERDICT: PASS' <file>` exits
    0 (measured exit 1 in both files, since neither mentions a fail value with PASS today).
  traces: REQ-07, REQ-09, D-01, D-05
  feature: FEAT-07
  depends_on: T-01
  status: pending

## Propagation — the site list I re-derived, not the one I was handed

Discriminating grep run at `4091b36` (`task_verify` does not exist yet, so the siblings are the
signal):

```
grep -rn -e tests_added -e blocked_on -e "suite:" -e "applied:" -e "change_type:" docs/ .claude/ .harness/team-config.yaml
```

Handed: `SPEC.md:1054-1055`, `test-validate-digest.py` (7 dev fixtures),
`harness-tdd-enforcement/SKILL.md:70-72`. **Three sites the handed list did not name, each a real
propagation site under the no-dev-ops-carve-out ruling:**

1. `.claude/agents/harness-dev-ops.md:69-75` — dev-ops's inline DIGEST block (T-03).
2. `docs/harness/SPEC.md:1062-1063` — §8.1's **dev-ops** bullet, distinct from the eng-devs bullet at
   `:1054-1055` (T-06).
3. `.claude/skills/harness/bin/test-validate-digest.py:1043-1044` — the dev-ops fixture, which is the
   only thing that proves D-03 survived (T-01, step 10).

Checked and ruled OUT **as `task_verify` sites, and SINCE PUT BACK IN on a different axis**:
`.claude/agents/harness-qa.md:65-71` and `harness-verification-rules/SKILL.md:85-90`. Correct then —
qa never gains `task_verify` (SC-05) — and wrong now: the Q2 fold changes qa's GATE BEHAVIOUR, and
both files annotate `suite` and `matrix_ok` with only the DEC-173 `n/a` rule, so both understate what
the validator enforces (REQ-07). That is T-10, and it is the propagation site this revision found.
**The lesson, recorded because it generalises: a site list derived against a new FIELD does not cover
a change to accepted VALUES.** The two questions have different answer sets and the second was not
asked on the first pass. Re-derived here against the fold: `grep -rn "suite: fail\|matrix_ok: false"`
over `docs/`, `.claude/agents/`, `.claude/skills/` and `.harness/` returns no printed worked example
carrying `VERDICT: PASS`, so unlike the `task_verify` change the fold invalidates no example
as-printed — there is no second T-04. Also ruled out: `.claude/skills/harness/SKILL.md`,
`docs/harness/BUILD.md`, `bin/check-state.sh`, `bin/test-gh-sync.py`, `templates/harness.json`,
`templates/PLAN.md`, `harness-spec-driven/SKILL.md` and `agents/harness-pm.md` (matched only on
`change_type:`/`applied:`, never on a dev digest field — `grep -n "suite:\|tests_added\|blocked_on"`
over the first three returns nothing). `docs/harness/DECISIONS.md` is history and is not rewritten.
`teams/build.yaml` is config, not a schema site — D-04.

**Re-derived on the Q1/Q2 revision — the preload map, which is a different question from the schema
site list.** The receipt clause is a RULE, not a digest field, so it propagates by who PRELOADS it,
not by who has a `suite:` in their template. Measured at `4091b36`:

```
grep -ln harness-tdd-enforcement .claude/agents/*.md   # -> exactly 5: ai-dev, backend-dev,
                                                       #    data-engineer, dev-ops, frontend-dev
grep -c harness-digest-dev .claude/agents/harness-dev-ops.md   # -> 0
grep -rn tdd-enforcement .harness/team-config.yaml .claude/settings.json .claude/skills/harness/bin/  # -> no output
```

So `harness-digest-dev` reaches FOUR specialists and `harness-tdd-enforcement` reaches exactly the
FIVE, loaded only through agent frontmatter. That is the whole basis of D-06, and it is the reason a
clause placed in `harness-digest-dev` alone would have left `harness-dev-ops` uncovered — silently,
since nothing checks preload coverage.

## Verify receipts — every `verify:` above was EXECUTED, with its BASE named, including on this revision

Not reasoned about. Run, with the result recorded. This is the precedent from FEAT-06, where a signed
`verify:` crashed on two keys in succession inside the plan of the feature whose charter was removing
checks that appear to exist and do nothing (`.harness/logs/2026-08-04.md`).

**BASE RE-STATED FOR THIS REVISION: `4091b36`, not `3bfedc9`.** HEAD moved when the index drift was
committed on its own, so every row's base was re-checked for staleness rather than only T-09's.
Measured, not assumed: `git diff --stat 3bfedc9 4091b36` shows ONE file,
`docs/harness/DECISIONS-INDEX.md` (57 insertions, 57 deletions), and no `verify:` command in this
table reads that file except T-09's two — which is exactly why T-09's row used to need two bases and
no longer does. Every row below was RE-EXECUTED at `4091b36` on this revision.

| Task | Command run now | Result at `4091b36` | Discriminates? |
|---|---|---|---|
| T-01(i) | **RE-RUN, shape changed** dev-ops digest, `task: T-01` + `suite: n/a` + `task_verify: n/a` + `PASS` -> `validate-digest.py harness-dev-ops` | `digest ok`, exit 0 | yes — must become exit 1 |
| T-01(ii) | **RE-RUN, shape changed** dev digest, `task: T-01` + `suite: fail` + `task_verify: pass` + `PASS` -> `harness-backend-dev` | `digest ok`, **exit 0** | yes — the Q2 fold |
| T-01(iii) | **RE-RUN** qa digest, `suite: pass` + `matrix_ok: false` + `PASS` -> `harness-qa` | `digest ok`, **exit 0** | yes — the boolean half. Carries neither new field (SC-05) |
| T-01(iv) | **RE-RUN THIS REVISION** `run-unit-tests.sh` from the repo root | `10/10 checks passed`, `PASS test-team-catalog.py`, **exit 0** | no — regression clause. **This row was NOT re-run on the previous revision and cited a prior green; it is a fresh run now, so nothing in this table is carried over** |
| T-01(v) | **NEW (D-07 redirect)** dev, `task` OMITTED + `task_verify: pass` + `PASS` -> `harness-backend-dev` | `digest ok`, **exit 0** | yes — proves `task` is REQUIRED, plus SC-18(b)'s hint branch |
| T-01(vi) | **NEW (D-07 redirect)** dev, `task: bogus` + `PASS` -> `harness-backend-dev` | `digest ok`, **exit 0** | yes — proves `task` is CONSTRAINED. Verified in the interpreter that a `re.Pattern` falls through every existing branch silently, so without step (3) this stays exit 0 |
| T-01(vii) | **RE-RUN, shape changed** dev, `task: T-01` + omitting ONLY `task_verify` + `PASS` | `digest ok`, **exit 0** | yes — SC-01's rejection and SC-18(a)'s hint assertion in one run |
| T-01(viii) | **NEW (D-07 redirect)** dev `task: none` + no `task_verify` + `PASS`; dev-ops same | `digest ok`, exit 0 / `digest ok`, exit 0 | **no — regression clause.** `task` is in no schema yet, so an unknown key is ignored; labelled, not sold as a detector |
| T-01(ix) | **NEW (D-08)** dev `task: none` + `task_verify: fail` + `PASS`; and dev `task: none` + `task_verify: n/a` + `PASS` | `digest ok`, exit 0 / `digest ok`, exit 0 | first: **yes** — the contradiction gate, must become exit 1. Second: no — regression clause, must STAY exit 0, and it is what proves the first rejects the contradiction rather than every value |
| T-01(x) | **NEW (SC-18c)** dev omitting BOTH new fields; then each of the two hint-licensed repairs | `digest ok`, exit 0 / exit 0 / exit 0 | rejection half **yes**; the two repairs are regression clauses. The only clause that would catch two jointly-contradictory hints |
| T-01 (scope) | qa digest, `suite: fail` + `PASS` -> `harness-qa` | `digest ok`, exit 0 | in scope; covered by fixture (12)(h). Carries neither new field — qa gains neither |
| T-01 (scope) | **RE-RUN, shape changed** **dev-ops** digest, `task: T-01` + `task_verify: pass` + `suite: fail` + `PASS` -> `harness-dev-ops` | `digest ok`, exit 0 | **out of scope by D-03** — stays exit 0, pinned by (12)(i). Re-run WITH both fields: without them the fixture would go red post-T-01 on a missing required field and take SC-15's residue guard down with it |
| T-01 (scope) | **NEW** dev digest, `task: T-01` + `task_verify: pass` + `suite: fail` + `PASS` -> `harness-backend-dev` | `digest ok`, exit 0 | yes — this is (12)(g)'s real shape. Without the two fields it would be rejected by the missing-field check alone and SC-13 would be satisfied without the fail gate existing |
| T-01 (fixtures) | `grep -n 'suite: fail' test-validate-digest.py` / `grep -n 'matrix_ok: false'` | `:814`, `:831` (both `VERDICT: FAIL`) / no match | no existing fixture flips. The file is byte-identical between the two bases (`git diff --stat` on it is empty), so the anchors carry — re-checked, not assumed |
| T-02 | `grep -c task_verify` on `harness-digest-dev/SKILL.md` | 0 | yes |
| T-02 | `grep -q 'PLAN.md'` | exit 1 | yes |
| T-02 | `grep -Eq 'BLOCKED.*PLAN\.md\|PLAN\.md.*BLOCKED'` | exit 1 | yes |
| T-02 | ~~`grep -q BLOCKED`~~ | **exit 0 — REJECTED as non-discriminating** (`:15` carries the VERDICT enum) | no |
| T-02 | `grep -ci receipt` / `grep -ci verbatim` on `harness-tdd-enforcement/SKILL.md` | 0 / 0 | yes |
| T-02 | `grep -Eqi 'receipt.*verbatim\|verbatim.*receipt'` on the same file | exit 1 | yes — the binding clause |
| T-02 | **(F6)** `grep -c '^VERDICT:'` on `harness-tdd-enforcement/SKILL.md` | **1** | no — regression clause; must still be 1 after T-02's append, or T-04's awk range breaks silently |
| T-02 | **RE-WRITTEN (D-07 redirect)** `grep -q 'task: T-NN\|none'` on `harness-digest-dev/SKILL.md` — the FIELD, replacing the withdrawn `grep -q 'no-task'` | exit 1 | yes |
| T-02 | **NEW (D-07 redirect)** `grep -q 'task_verify: pass\|fail\|n/a'` (three-member) / `grep -qi 'no-task'` on the same file | exit 1 / exit 1 | first yes; second **no — scope guard** against the rejected spelling, paired per DEC-169 |
| T-03 | **RE-WRITTEN (D-07 redirect)** `grep -q 'task_verify: pass\|fail\|n/a'` — THREE-member, replacing the withdrawn four-member form (which also measures exit 1 here) | exit 1 | yes |
| T-03 | **NEW (D-07 redirect)** `grep -q 'task: T-NN\|none'` on `harness-dev-ops.md` | exit 1 | yes — the second field; a file naming one and not the other documents a schema that does not exist |
| T-03 | **RE-RUN** `grep -A4 'task_verify' … \| grep -q suite` (window widened from -A2 for the longer corrected comment) | exit 1 | yes |
| T-03 | **(F1b)** `grep -qi 'never the honest answer'` / **NEW** `grep -qi 'no-task'` on `harness-dev-ops.md` | exit 1 / exit 1 | no — two scope guards against the superseded draft's false sentence and its rejected enum spelling, paired per DEC-169 |
| T-04 | `grep -q 'task_verify: n/a'` | exit 1 | yes |
| T-04 | **NEW (D-07 redirect)** `grep -q 'task: T-1'` on `harness-tdd-enforcement/SKILL.md` — a CONCRETE id, so a re-introduced `task: T-NN` fails it | exit 1 | yes |
| T-04 | ~~`sed -n '66,79p' … \| validate-digest.py`~~ | **REJECTED — line-number range, and T-02 now writes this file** | replaced |
| T-04 | **RE-RUN this revision** `awk '/^VERDICT: BLOCKED$/,/^artifact: none$/' … \| validate-digest.py harness-backend-dev` | `digest ok`, exit 0 — same block, text-anchored | regression clause; red between T-01 and T-04. Re-run because T-04's body changed this revision (the concrete-id edit) |
| T-05 | `grep -q 'verify:'` / `grep -q verbatim` on `harness-zero-micro-management/SKILL.md` | exit 1 / exit 1 | yes |
| T-06 | **RE-RUN** per-bullet `awk … \| grep -c task_verify` (eng-devs, dev-ops) and whole-file `grep -c 'task_verify' docs/harness/SPEC.md` | 0 / 0 / 0 | yes |
| T-06 | **NEW (D-07 redirect)** the same three shapes for the second field — ``grep -c '`task:'`` per bullet and whole-file | 0 / 0 / 0 | yes. The backtick is load-bearing (SPEC lists fields in backticks) and does NOT match `task_verify:` — verified, the two counts are independent |
| T-07 | `grep -q 'consolidated fix'` / §2-scoped `grep -ci 'one review pass'` | exit 1 / 0 | yes |
| T-08 | `grep -ci 'before any claim'` on `commands/harness.md`, `harness/SKILL.md` | 0 / 0 | yes |
| T-08 | ~~`grep -qi probe` on `harness/SKILL.md`~~ | **1 match at `:156` — REJECTED as non-discriminating** | no |
| T-08 | `grep -ci 'before any claim'` on `harness-handoff/SKILL.md` | 0 | no — scope guard, paired per DEC-169 |
| T-09 | `grep -c '^- DEC-17[5-7] '` on the index | 0 | yes |
| T-09 | **RE-BASED — the two-row split is GONE** `gen-decisions-index.py --stdout \| diff - docs/harness/DECISIONS-INDEX.md` | **exit 0** | no — REGRESSION clause. Only the row above discriminates. At `3bfedc9` this exited 1 and the working tree exited 0, so the row needed two bases; at `4091b36` the drift is committed, `git status` is clean of the file, and there is ONE base |
| T-10 | `grep -c 'VERDICT: PASS is rejected'` on `harness-qa.md` / `verification-rules/SKILL.md` | 1 / 1 | yes — must become >= 2 |
| T-10 | `grep -Eqi 'fail.*VERDICT: PASS is rejected\|false.*VERDICT: PASS'` on both | exit 1 / exit 1 | yes |
| T-02 | `grep -c 'VERDICT: PASS is rejected'` on `harness-digest-dev/SKILL.md` | 1 | yes — must become >= 2 |
| T-10 (scope) | `grep -rn 'suite: fail\|matrix_ok: false'` over `docs/`, `.claude/agents/`, `.claude/skills/` | only `SPEC.md:1075`, a routing line — **no printed example flips** | rules out a T-04-shaped task. (Widening the sweep to `.harness/` also returns two FEAT-05 qa artifacts, which are feature records, not rule surfaces — stated so the narrower path is not read as a hidden result) |

THREE commands have now been rewritten as a direct result of running them — the three struck rows.
Two on the first pass (`grep -q BLOCKED`, which already exited 0; `grep -qi probe`, which already
matched), and one on the Q1/Q2 revision: T-04's `sed -n '66,79p'` was replaced by a text-anchored
`awk` range, because T-02 now writes that same file and a line-number range is one insertion away
from extracting the wrong block — a `verify:` that passes while testing nothing.

**A FOURTH was rewritten on the previous revision, and it is the most important one, because it was
not merely non-discriminating — it was FALSE.** T-09's `gen-decisions-index.py --stdout | diff -` row
read "exit 0 — no pre-existing drift, clean on arrival". Re-run against `3bfedc9` it exits 1. The
row was true only of the DIRTY WORKING TREE, where the generator had already been re-run, and
re-running it there reproduces the falsehood exactly. That drift is now committed at `4091b36` and
the ambiguity with it, but the lesson stands and is why every row above names its BASE alongside its
command, exit code and interpretation: a receipt that names three of the four is a receipt that
cannot be checked, and this is the feature whose charter is removing checks that look real and do
nothing.

**A FIFTH and SIXTH were rewritten on THIS revision, by the D-07 redirect rather than by running
them.** T-02's and T-03's `no-task` enum clauses asserted a value the user rejected: left standing
they would have been `verify:` commands demanding that a rule surface contradict the schema. Each is
replaced by its `task: T-NN|none` counterpart and the withdrawn spelling is re-purposed as a labelled
scope guard rather than deleted, so a re-introduction goes red instead of going unnoticed.

**Absence clauses, all of them, labelled rather than counted as evidence.** There are now SIX, not
four: T-08's `harness-handoff` guard (paired per DEC-169, SC-10); SC-16's `receipt`/`verbatim` scope
guard; T-03's `never the honest answer` guard against the superseded draft's own false sentence;
the `genuinely not applicable` half of T-01(vii); and **two added by the D-07 redirect** — T-02's
and T-03's `grep -qi 'no-task'` guards against the REJECTED enum spelling, which exits 1 at
`4091b36` and therefore proves nothing on its own but is what keeps a withdrawn value from surviving
into a normative surface. Each is paired with at least one presence check in the same clause and
none is offered as proof on its own. T-01(viii) and T-01(x)'s repair halves are likewise labelled
regression clauses, not detectors: `task: none` is accepted at `4091b36` too, because `task` is in
no schema yet and an unknown key is ignored.

**On this revision specifically — everything was re-run, and there is nothing left un-re-run.**
The D-07 redirect changed the bodies of T-01, T-02, T-03, T-04, T-06 and T-09, and HEAD moved from
`3bfedc9` to `4091b36`, so BOTH reasons to re-execute applied and every row in the table above was
run afresh at `4091b36` rather than carried over. Three consequences worth naming rather than
leaving to be inferred:
1. **T-01(iv) is now a fresh green.** The previous revision recorded it as NOT re-run and cited the
   architecture reviewer's observed green instead. It was run here — `10/10 checks passed`, exit 0 —
   so the "one clause not re-run" caveat that stood in this section has no referent any more and is
   deleted rather than softened.
2. **T-09's two-row base split has collapsed to one row.** It existed only because
   `gen-decisions-index.py --stdout | diff -` exited 1 against `3bfedc9` and 0 against a working
   tree in which the generator had been re-run undeclared. Re-measured at `4091b36`: it exits 0, and
   `git status --short` shows `docs/harness/DECISIONS-INDEX.md` clean. One base, one row.
3. **The working-tree statement is re-measured, not patched.** `git status --short` at this revision
   shows ONE modified tracked file, `.harness/logs/2026-08-04.md`, plus two untracked paths — this
   feature's own folder and `.harness/notes/grilling-perf-batch-1-2026-08-04.md`. No `verify:`
   command in this table reads any of the three, and `docs/harness/SPEC.md`, `.claude/**` and
   `.claude/skills/harness/bin/**` are byte-identical to `4091b36`. The earlier paragraph asserting
   "for every command except T-09's the two bases are the same tree" described a tree that no longer
   exists; its conclusion happens to survive, which is exactly why it was re-measured rather than
   left standing.

## A note on the folded `>` blocks

`intent:` and `verify:` are folded YAML scalars, matching the shipped exemplar
`.harness/features/FEAT-06-team-layer-inv6/PLAN.md`. Checked, because a line-oriented extractor would
truncate them: `gh-sync.py`'s `parse_tasks` (`:151-167`) reads task fields with a
single-line regex, but it only reads `change_type`, `traces` and `absorbs` — all single-line here —
and passes `body` through whole. `check-state.sh` INV-4 (`:90-101`) does a substring test for
`change_type:` over the whole task body. Neither touches `verify:` or `intent:`. The lead reads
`PLAN.md` as text.
