schema: plan/1
feature: BUG-2565-digest-frontmatter-contract
source_issues: [2565, 2482]
lanes:
  resolved_at: cf7b422b2e55ae4c9129a8009e240b56c6e25035
  rows:
  - surface: .omp/extensions/**
    lane: main-session-direct
    reason: NOBODY owns the OMP hook surface; DEC-174 keeps the yield gate and task hook change out of team execution.
  - surface: .omp/agents/**
    lane: main-session-direct
    reason: NOBODY owns agent definitions (DEC-233); the main session runs the generator.
  - surface: .omp/config.yml
    lane: main-session-direct
    reason: NOBODY owns the OMP config; it changes with the port check that grades it.
  - surface: .claude/skills/harness/bin/**
    lane: main-session-direct
    reason: Granted to harness-backend-dev and harness-dev-ops, but check-omp-port.py and the projection it calls are gate code under DEC-174.
  - surface: tests/unit/omp-hooks.test.ts
    lane: main-session-direct
    reason: Granted to harness-backend-dev and harness-dev-ops; DEC-174 keeps a gate's test with its gate.
  - surface: tests/unit/test-digest-projection.py
    lane: main-session-direct
    reason: Granted to harness-backend-dev and harness-dev-ops; DEC-174 keeps a gate's test with its gate.
  - surface: tests/integration/test-check-omp-port.py
    lane: main-session-direct
    reason: Granted to harness-backend-dev and harness-dev-ops; DEC-174 keeps a gate's test with its gate.
  - surface: tests/integration/test-typescript-typecheck.py
    lane: main-session-direct
    reason: Granted to harness-backend-dev and harness-dev-ops; it changes because the hook task deletes a settled source.
  - surface: .harness/README.md
    lane: main-session-direct
    reason: Owner harness-documentor; the operator routed every task of this feature main-session-direct under DEC-174.
  - surface: .harness/harness/docs/**
    lane: main-session-direct
    reason: Owner harness-documentor; the operator routed every task of this feature main-session-direct under DEC-174.
  - surface: .claude/skills/harness-team/SKILL.md
    lane: main-session-direct
    reason: NOBODY owns this skill file; one sentence states the retired hook injection.
  - surface: .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/**
    lane: main-session-direct
    reason: The live probes run in the main session, which records their receipts.
decisions:
- id: D-01
  choice: The digest provider projection moves to Python in digest_projection.py, gen-agent-output.py writes it into each harness agent's frontmatter output, check-omp-port.py compares each agent's output to the projection, and .omp/extensions/digest-schema.ts is deleted.
  because: One language then holds the contract's validator, projection and port check with no mirrored persona table; rejected were keeping the TypeScript loader with check-omp-port.py shelling out to bun, and hand-maintained output blocks.
  dec: DEC-237
- id: D-02
  choice: A yield refused because validate-digest could not run carries a fixed reason distinct from every contract refusal; it names the validator failure, says the object was not checked and the fault is Harness's, and tells the child to yield the same object once more and, if refused again for the same cause, to stop yielding and end its turn naming the cause.
  because: A child cannot repair a Harness fault and every yield, BLOCKED included, is refused while the validator is down; rejected was telling the child to yield BLOCKED, which the same broken validator also refuses.
  dec: DEC-100
- id: D-03
  choice: T-01's live probe gates the build; if any hook-refused yield's payload reaches the parent's task result, the build stops before T-02 and the design returns to the operator.
  because: Failing closed is real only if OMP never surfaces a refused payload, and that is host behaviour no unit test can show; rejected was discovering it after the route is cut over.
  dec: none
- id: D-04
  choice: The yield hook refuses a yield that carries no data whatever its type, including a data-less type result, instead of leaving it to OMP.
  because: The pass-through relied on strict terminal yields rejecting it natively, and agent frontmatter cannot set strict mode.
  dec: DEC-237
- id: D-05
  choice: validate-digest.py keeps reporting its own failure as an unavailable line at exit 0 and stays in BROAD_GATES; the OMP yield phase alone turns an unavailable validator outcome, declared or synthesized, into a refusal, and the other three broad gates keep failing open visibly.
  because: Only the extension sees the declared line and also crashes, spawn failures and budget kills, so one place decides; rejected was exit 2 inside validate-digest.py, which cannot cover a failure before its guard loads.
  dec: DEC-100
decisions_affected:
- dec: DEC-100
  disposition: amend
  clause: "`check-domain.py`, `bash-write-guard.py`, `dispatch-guard.py` and `validate-digest.py` an own"
  successor: D-05
  reason: validate-digest.py still reports its own failure as unavailable, but the yield is now refused on it; the three write, Bash and dispatch gates keep failing open visibly.
- dec: DEC-126
  disposition: amend
  clause: "Python, while the OMP adapter resolves and projects them into the strict provider bundle injected"
  successor: D-01
  reason: The projection is now Python and is generated into agent frontmatter, not injected at dispatch.
- dec: DEC-127
  disposition: amend
  clause: "call so an own exception returns 0 — fail OPEN, on our own"
  successor: D-05
  reason: The script's own exit stays 0 with the unavailable line, but the yield that carried it is refused, so the outcome is no longer fail open.
- dec: DEC-206
  disposition: amend
  clause: "the task hook injects strict schemas only for `harness-*` personas"
  successor: D-01
  reason: The schema now reaches only harness agents through their frontmatter; the task hook injects nothing.
- dec: DEC-208
  disposition: amend
  clause: "Failing closed on our own gap was rejected in one clause: it would wedge"
  successor: D-05
  reason: The operator reversed that rejection for the yield; an unchecked return reaching a dispatcher is worse than one child that stops naming the cause.
- dec: DEC-237
  disposition: amend
  clause: "**Dispatch owns schema delivery.** Before any claim side effect, the OMP task hook refuses"
  successor: D-01
  reason: Agent definitions now own schema delivery, global task.structured is off, the hook neither injects nor refuses schema controls, and the BUG-2305 exact-copy exception goes with it (D-04 adds the data-less yield refusal).
- dec: DEC-174
  disposition: keep
  clause: the cutover that makes a gate use it is main-session-direct
  successor: none
  reason: Every task here changes or measures the yield gate, task hook or port check, so all six run main-session-direct.
- dec: DEC-179
  disposition: keep
  clause: an ungranted surface becomes a DECLARED main-session step
  successor: none
  reason: Every NOBODY and documentor surface is declared in lanes before signature.
- dec: DEC-233
  disposition: keep
  clause: "`.omp/agents/**` stays unowned by every agent."
  successor: none
  reason: The generated frontmatter is written by the main session running gen-agent-output.py, never by an agent.
- dec: DEC-188
  disposition: keep
  clause: "Anything softer than that — a decision that is merely dated, narrowed, or partly\novertaken — is amended"
  successor: none
  reason: Each affected decision is partly overtaken and amended in place; none is struck.
- dec: DEC-254
  disposition: keep
  clause: "Each row has exactly five fields:"
  successor: none
  reason: The six amend rows are owned by T-06, which lists DECISIONS.md and its index.
tasks:
- id: T-01
  title: Measure on OMP 19.2.1 what a hook-refused yield does to OMP's retries and to the parent's result
  traces: [SC-11]
  change_type: docs
  execution_mode: main-session-direct
  execution_reason: DEC-174 - a live probe of the yield gate's host behaviour, run before the gate changes; the main session holds the omp binary and credentials.
  depends_on: []
  status: ready
  files:
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-yield-refusal-probe.md
  verify: |
    set -eu
    python3 - <<'PY'
    import re, subprocess, sys
    path = ".harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-yield-refusal-probe.md"
    text = subprocess.run(["git", "show", "HEAD:" + path], capture_output=True, text=True, check=True).stdout
    want = {
        "omp_version": "19[.]2[.]1",
        "model": "[^ ].*",
        "hook_refusal_consumes_schema_retry": "yes|no",
        "refused_attempts_before_end": "[0-9]+",
        "parent_task_status": "[a-z_]+",
        "parent_receives_refused_payload": "no",
        "dataless_result_yield_without_hook": "rejected|accepted",
    }
    bad = [k for k, v in want.items() if not re.search("(?m)^" + k + ": (" + v + ")$", text)]
    print("probe receipt ok" if not bad else "MISSING OR WRONG: " + ", ".join(bad))
    sys.exit(1 if bad else 0)
    PY
  intent: |
    Work directly in PRODUCT checkout /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2565-digest-frontmatter-contract; every relative-path edit stays inside it. Main owns this task under DEC-174 and DEC-179, with no engineering-lead dispatch. Source issue 2565. Read this feature's BRIEF.md and notes/research-digest-frontmatter-contract.md first. PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md are absent in this checkout; do not invent or substitute them. Change no code in this task.
    Purpose: answer, by measurement on the installed omp (confirm omp --version prints 19.2.1), the two questions the grilling left open, before any gate changes. Build a throwaway OMP project in a fresh mktemp -d directory outside every checkout. In it create .omp/agents/probe-child.md with frontmatter name probe-child, a one-line description, tools [read], spawns [], blocking true, structured true, and output set to the closed object schema: type object, properties VERDICT (type string, enum PASS and BLOCKED) and note (type string), required [VERDICT, note], additionalProperties false. Create one extension file refuse-yield.ts exporting a default function that registers pi.on tool_call; for toolName yield it appends one JSON line holding the call input to the file named by environment variable PROBE_LOG and, while a per-process counter of yield calls is below environment variable PROBE_REFUSE (an integer; unset means refuse every yield), returns block true with this reason, verbatim: Harness refused this yield: validate-digest exited 1: probe. Your object was not checked, and Harness never passes an unchecked return. This is a Harness fault, not a violation found in your object: do not change a valid object to get past it. Yield the same object once more; if it is refused again for this same cause, stop yielding and end your turn with one line naming this cause, because no yield can pass until validate-digest runs.
    Run every probe from the throwaway directory with omp -p --no-extensions -e followed by the path of refuse-yield.ts, so only that extension loads, and record the model omp used. The parent prompt in each run is: dispatch the task tool once with agent probe-child and the run's child task text, then report verbatim the task result's status, any data and any warning.
    Run A (refuse every yield, PROBE_REFUSE unset): child task text tells it to yield data VERDICT PASS, note probe, and to follow any refusal's instruction exactly. Record the number of yield calls logged (refused_attempts_before_end), the parent's task status word (parent_task_status), whether the child stopped on its own, and whether the parent's result carries any data equal to a logged refused input (parent_receives_refused_payload yes or no).
    Run C (PROBE_REFUSE=3): child task text gives an exact sequence: yield attempts 1 to 3 send VERDICT PASS, note probe; attempt 4 sends the object wrong true; attempt 5 sends VERDICT PASS, note probe. If the parent receives data wrong true with OMP's schema-invalid warning, hook refusals consumed OMP's schema-retry budget (hook_refusal_consumes_schema_retry yes); if attempt 4 is rejected by OMP with field violations and attempt 5 completes, they did not (no). If the child did not follow the sequence, repeat Run C once; if it still deviates, record the observed sequence and set the key to what the log and result show, stating the reasoning.
    Run B (PROBE_REFUSE=0, so the extension logs but refuses nothing): child task text tells it to call yield first with type result and no data, then with VERDICT PASS, note probe. Record whether OMP itself rejected the data-less result yield (dataless_result_yield_without_hook rejected or accepted).
    Write .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-yield-refusal-probe.md with a Result section holding exactly these lines, one key per line, key colon space value: omp_version, model, hook_refusal_consumes_schema_retry, refused_attempts_before_end, parent_task_status, parent_receives_refused_payload, dataless_result_yield_without_hook; then a Method section (the agent file, extension source and prompts) and an Evidence section (each run's parent result verbatim and the log line counts). No credentials or tokens in the note. Commit the note, then run the literal verify.
    D-03 gate: if parent_receives_refused_payload is yes, the verify fails by design; stop the build, do not start T-02, and report the evidence to the operator as a design defect. Expected result otherwise: verify prints probe receipt ok and exits 0.
- id: T-02
  title: Refuse a yield the validator cannot check or that carries no data, and delete per-call schema injection
  traces: [SC-01, SC-02, SC-03, SC-04]
  change_type: bugfix
  execution_mode: main-session-direct
  execution_reason: DEC-174 - changes the yield gate and the task hook in harness-hooks.ts with their tests.
  depends_on: [T-01]
  status: ready
  files:
  - .omp/extensions/harness-hooks.ts
  - .omp/extensions/digest-schema.ts
  - tests/unit/omp-hooks.test.ts
  - tests/integration/test-typescript-typecheck.py
  verify: |
    set -eu
    bun install --frozen-lockfile
    bun test tests/unit/omp-hooks.test.ts
    python3 tests/integration/test-typescript-typecheck.py
    test ! -e .omp/extensions/digest-schema.ts
    test "$(grep -cE 'SCHEMA_CONTROLS|isInjectedCopy|schemaControlRefusal|withDigestSchemas|loadDigestSchemaBundle|outputSchema|schemaMode|digest-schema' .omp/extensions/harness-hooks.ts)" = 0
  intent: |
    Work directly in PRODUCT checkout /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2565-digest-frontmatter-contract; every relative-path edit stays inside it. Main owns this task under DEC-174 and DEC-179, with no engineering-lead dispatch. Source issue 2565. Read this feature's BRIEF.md, notes/research-digest-frontmatter-contract.md and notes/research-yield-refusal-probe.md first; do not start unless T-01's verify passed. PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md are absent in this checkout; do not invent or substitute them.
    Tests first. In tests/unit/omp-hooks.test.ts write the new and rewritten cases below, run bun test tests/unit/omp-hooks.test.ts against the unchanged hook, and record in your build receipt which fail; expected failing: every validator-cannot-run yield case, the data-less result case and the schema-control pass-through case. Then change production code.
    Yield phase in .omp/extensions/harness-hooks.ts (D-02, D-04, D-05). Add exported function validatorUnavailableRefusal(detail: string): string returning exactly: Harness refused this yield: DETAIL. Your object was not checked, and Harness never passes an unchecked return. This is a Harness fault, not a violation found in your object: do not change a valid object to get past it. Yield the same object once more; if it is refused again for this same cause, stop yielding and end your turn with one line naming this cause, because no yield can pass until validate-digest runs. (DETAIL is the detail argument, which is the PolicyResult unavailable string, already prefixed with validate-digest.) In the yield branch, call validate-digest.py --hook through policyRunner directly rather than reportingRunner, so its own failure is not also queued as a passive notice, and set reason to result.reason when result.blocked, else to validatorUnavailableRefusal(result.unavailable) when result.unavailable is set, else undefined. Replace the early return for data == null with type result, and its comment, by a refusal with RETURN_THE_OBJECT for any yield whose data is null or absent whatever its type; the comment says agent frontmatter cannot set strict mode, so OMP's native rejection is not guaranteed (BUG-2565 D-04). Keep validate-digest.py in BROAD_GATES so classifyPolicyRun still reports its failure as unavailable, and reword the BROAD_GATES comment: the four gates report their own failure as unavailable; the yield phase alone refuses on validate-digest's (BUG-2565). classifyPolicyRun and classifyAnswer are otherwise unchanged.
    Task phase. Delete SCHEMA_CONTROLS, DIGEST_SCHEMA_DIR, isInjectedCopy, schemaControlRefusal, withDigestSchemas and the FEAT-1928 and BUG-2305 comment block above them; delete the schemaControlRefusal and withDigestSchemas block in the task branch and its comment, keeping the sentence that a per-call model is native policy and forwarded untouched; the task branch then runs dispatch-guard.py for each normalizeTaskDispatches(input) entry with the input unrevised. Delete the import from ./digest-schema.ts and the node:util isDeepStrictEqual import if nothing else uses it. Delete the file .omp/extensions/digest-schema.ts. Afterwards no text in harness-hooks.ts names outputSchema, schemaMode, digest-schema or any deleted symbol, comments included.
    Tests in tests/unit/omp-hooks.test.ts. Delete the cases refuses outputSchema or schemaMode at the top level and in any item; injects every one of the 16 personas' own strict bundle; the three BUG-2305 cases; refuses a harness dispatch whose schema cannot load; a schema-refused dispatch records no claim; the whole loadDigestSchemaBundle describe block; and the imports and helpers only they used. Rewrite FEAT-2274 an unavailable dispatch-guard keeps the schema injection, one notice per target, to assert one notice per target and no input key in the hook result. Replace FEAT-2274 an unavailable digest validator lets the yield through with BUG-2565 cases driving the registered tool_call handler with a governed lead context and a policy runner whose validate-digest.py answer is classifyPolicyRun over real process ends: a declared unavailable stdout line at exit 0, exit 1, exit 3, SIGKILL, a spawn error and a timedOut process; one expect per class that the result is block true with reason starting with validatorUnavailableRefusal of that class's unavailable string. Keep FEAT-2274 an unavailable check-domain lets the write proceed and says so unchanged as the control that other broad gates still pass. Add: a validator exit 2 with stderr reason X blocks with a reason that contains X and does not contain was not checked; a yield with type result and no data is blocked with RETURN_THE_OBJECT and validate-digest.py is never invoked; for Main and for a governed lead, a flat harness-pm dispatch carrying outputSchema and schemaMode strict, a tasks[] batch whose harness-qa item carries outputSchema and whose harness-pm item carries schemaMode permissive, and a non-harness scout target carrying outputSchema each return no block and no input key, and dispatch-guard.py receives agent, task and name for every target.
    In tests/integration/test-typescript-typecheck.py remove .omp/extensions/digest-schema.ts from SETTLED, rename the check the four settled sources are tracked to the settled sources are tracked, and set POISONED to .omp/extensions/harness-hooks.ts.
    Run the literal verify from the PRODUCT checkout root; expected: every bun test passes, the typecheck script prints PASS test-typescript-typecheck.py, digest-schema.ts is absent and the grep count is 0, exit 0.
- id: T-03
  title: Port the digest provider projection to Python and add the agent output generator
  traces: [SC-07, SC-08]
  change_type: logic
  execution_mode: main-session-direct
  execution_reason: DEC-174 - the projection becomes part of check-omp-port.py, a gate.
  depends_on: [T-01]
  status: ready
  files:
  - .claude/skills/harness/bin/digest_projection.py
  - .claude/skills/harness/bin/gen-agent-output.py
  - tests/unit/test-digest-projection.py
  verify: |
    set -eu
    python3 tests/unit/test-digest-projection.py
    python3 - <<'PY'
    import json, os, subprocess, sys, tempfile
    sys.path.insert(0, ".claude/skills/harness/bin")
    import digest_projection, digest_schema
    src = subprocess.run(["git", "show", "104252db:.omp/extensions/digest-schema.ts"], capture_output=True, text=True, check=True).stdout
    scratch = tempfile.mkdtemp(prefix="bug2565-parity-")
    with open(os.path.join(scratch, "digest-schema.ts"), "w", encoding="utf-8") as handle:
        handle.write(src)
    schemas = os.path.abspath(".claude/skills/harness/schemas/digest")
    js = ("import { loadDigestSchemaBundle } from " + json.dumps(os.path.join(scratch, "digest-schema.ts")) + ";"
          " const out = {}; for (const p of " + json.dumps(list(digest_schema.PERSONAS)) + ")"
          " out[p] = loadDigestSchemaBundle(" + json.dumps(schemas) + ", p); console.log(JSON.stringify(out));")
    ts = json.loads(subprocess.run(["bun", "-e", js], capture_output=True, text=True, check=True).stdout)
    bad = [p for p in digest_schema.PERSONAS if digest_projection.provider_bundle(p) != ts[p]]
    for p in digest_schema.PERSONAS:
        print(p, "parity ok" if p not in bad else "PARITY DIFFERS")
    sys.exit(1 if bad else 0)
    PY
  intent: |
    Work directly in PRODUCT checkout /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2565-digest-frontmatter-contract; every relative-path edit stays inside it. Main owns this task under DEC-174 and DEC-179, with no engineering-lead dispatch. Source issue 2565. Read this feature's BRIEF.md and notes/research-digest-frontmatter-contract.md first; do not start unless T-01's verify passed. PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md are absent in this checkout; do not invent or substitute them.
    Create .claude/skills/harness/bin/digest_projection.py (D-01). It defines class ProjectionError(Exception) and provider_bundle(persona, directory=digest_schema.SCHEMA_DIR) returning a plain dict: the ref-free provider schema for the persona, read from disk on every call with no cross-call cache. The persona is canonicalised with digest_schema.canonical_persona, so the four aliases resolve; an unknown persona raises ProjectionError. The projection reproduces, rule for rule, BundleLoader.document, resolveRef and project and loadDigestSchemaBundle in git show 104252db:.omp/extensions/digest-schema.ts: the directory is real-path resolved and a referenced or real-pathed file outside it is refused; files load with artifact_accessors.load_json_mapping; a ref is a relative file part plus an optional fragment that must be a JSON pointer, URI schemes and absolute paths refused, pointer tokens percent-decoded then ~1 and ~0 unescaped; a $ref node allows only annotation siblings; a cycle is detected on the stack of file#pointer keys; annotations ($schema, $id, $comment, $defs, title, description, examples, default, deprecated, readOnly, writeOnly), bounds (pattern, format, minLength, maxLength, minimum, maximum, exclusiveMinimum, exclusiveMaximum, multipleOf, minItems, maxItems, uniqueItems, minProperties, maxProperties) and conditionals (if, then, else) are dropped; type must name only object, array, string, integer, number, boolean or null; properties children and items must project to a node carrying type, enum or anyOf; required must be a list of strings; additionalProperties projects only false; enum must be a non-empty list and never sit beside const; const becomes a one-value enum at const's position; allOf is dropped only when every branch holds only conditional or annotation keys; anyOf must be a non-empty list, is refused at the schema root, is dropped when every projected branch holds only required, and otherwise every branch must carry type or enum; an array type without items is refused; any other keyword is refused. Every refusal raises ProjectionError with message digest schema RELPATH#POINTER: REASON, RELPATH relative to the schema directory. Output keys keep source order.
    Create .claude/skills/harness/bin/gen-agent-output.py with usage gen-agent-output.py [--check] [ROOT]; ROOT defaults to Path(__file__).resolve().parents[4]. For each persona in digest_schema.PERSONAS it reads ROOT/.omp/agents/PERSONA.md (missing file: message on stderr, exit 2) and renders the bundle from digest_projection.provider_bundle(persona, ROOT/.claude/skills/harness/schemas/digest) as two frontmatter keys: the line structured: true, then the line output: followed by yaml.safe_dump(bundle, sort_keys=False, default_flow_style=False, allow_unicode=True, width=4096) with every line indented two spaces. The frontmatter is the text between the opening line --- and the next line equal to ---. Remove an existing top-level structured line, and an existing top-level output line with every following line that starts with a space, then insert the two rendered keys immediately before the closing ---; the body and every other frontmatter line stay byte-identical. Without --check, write a file only when its bytes change, print wrote RELPATH for each, exit 0. With --check, write nothing, print DRIFT RELPATH for each agent whose rendered bytes differ and exit 1, or print agent output: ok and exit 0. A ProjectionError prints on stderr and exits 2.
    Create tests/unit/test-digest-projection.py in the style of tests/unit/test-digest-schemas.py (script with main, one PASS or FAIL line per case, exit 1 on any failure). Cases, each its own assertion: all 16 personas project; each of the four aliases equals its target's bundle; no projected node contains $ref and every key is one of type, properties, required, additionalProperties, items, enum, anyOf; in a temp copy of the schema directory, each of malformed JSON, an unresolved reference, a reference cycle, a reference escaping the directory, an unsupported keyword, a property with no type, enum or anyOf, an array without items, and an anyOf at the schema root raises ProjectionError whose message names the file and the JSON pointer; a schema file changed on disk between two calls changes the second result. Generator, on a temp root holding copies of .omp/agents and the schema directory: a first run then a second run leave identical bytes; --check exits 0 after generation; a hand-edited output value makes --check exit 1 printing DRIFT with that agent's path; each agent body and each non-structured, non-output frontmatter line is byte-identical to the pre-generation copy; a file that already had structured and output keys ends with exactly one of each.
    Parity: the verify compares provider_bundle against the TypeScript loader at 104252db for all 16 personas over the current schema files; it needs bun on PATH. If a persona differs, fix the port, never the comparison.
    Run the literal verify from the PRODUCT checkout root; expected: every test case PASS, sixteen parity ok lines, exit 0.
- id: T-04
  title: Generate digest output into the 16 agent definitions, turn global task.structured off, and make check-omp-port.py catch drift
  traces: [SC-06]
  change_type: config
  execution_mode: main-session-direct
  execution_reason: DEC-174 - check-omp-port.py is the port gate; agent definitions and config are NOBODY surfaces.
  depends_on: [T-02, T-03]
  status: ready
  files:
  - .omp/agents/harness-ai-dev.md
  - .omp/agents/harness-backend-dev.md
  - .omp/agents/harness-code-reviewer.md
  - .omp/agents/harness-data-engineer.md
  - .omp/agents/harness-dev-ops.md
  - .omp/agents/harness-documentor.md
  - .omp/agents/harness-eng-lead.md
  - .omp/agents/harness-frontend-dev.md
  - .omp/agents/harness-orchestrator.md
  - .omp/agents/harness-pm.md
  - .omp/agents/harness-product-lead.md
  - .omp/agents/harness-qa.md
  - .omp/agents/harness-security-reviewer.md
  - .omp/agents/harness-ui-reviewer.md
  - .omp/agents/harness-validator-lead.md
  - .omp/agents/harness-visual-designer.md
  - .omp/config.yml
  - .claude/skills/harness/bin/check-omp-port.py
  - tests/integration/test-check-omp-port.py
  verify: |
    set -eu
    python3 .claude/skills/harness/bin/gen-agent-output.py --check
    python3 .claude/skills/harness/bin/check-omp-port.py
    python3 tests/integration/test-check-omp-port.py
    python3 .claude/skills/harness/bin/check-skill-weight.py
  intent: |
    Work directly in PRODUCT checkout /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2565-digest-frontmatter-contract; every relative-path edit stays inside it. Main owns this task under DEC-174, DEC-179 and DEC-233, with no engineering-lead dispatch. Source issue 2565. Read this feature's BRIEF.md and notes/research-digest-frontmatter-contract.md first; T-02 (fail-closed yield) must already have landed, because OMP's own check is permissive under frontmatter. PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md are absent in this checkout; do not invent or substitute them.
    Tests first. In tests/integration/test-check-omp-port.py replace case_task_structured_required with case_task_structured_off: task.structured absent passes, boolean false passes, and boolean true, the string true and the integer 1 each exit 1 with task.structured in stderr. Add case_agent_output_drift with three independent fixtures, each exiting 1 with stderr naming the file: add a property probe_field of type string to the DIGEST properties of the fixture's .claude/skills/harness/schemas/digest/harness-qa.json without regenerating (stderr names .omp/agents/harness-qa.md); in .omp/agents/harness-pm.md replace the first additionalProperties: false under output with additionalProperties: true; delete the structured: true line from .omp/agents/harness-ui-reviewer.md. Run the first drift fixture against the pre-change check-omp-port.py and record in your build receipt that it passes there. Keep case_live_tree_passes.
    Run python3 .claude/skills/harness/bin/gen-agent-output.py from the checkout root to write structured: true and output into all sixteen .omp/agents/harness-*.md files; never hand-edit those keys.
    In .omp/config.yml delete the structured: true line under task and the BUG-2171 comment above it, and put in their place a comment saying: BUG-2565, task.structured stays at OMP's default (off); each harness agent's frontmatter carries structured true and an output generated from schemas/digest by gen-agent-output.py, so the task tool exposes no schema parameter to any dispatcher; non-harness children get no yield tool, accepted by the operator.
    In .claude/skills/harness/bin/check-omp-port.py: import digest_projection; in config_errors replace the rule requiring task.structured true with an error when the task mapping holds a structured value that is anything other than absent or boolean False, worded .omp/config.yml task.structured must stay unset or false: each harness agent's frontmatter carries its digest schema. Add agent_output_errors(root, path, meta, name), called from agent_file_errors: meta structured not exactly True gives RELPATH must set structured: true so its yield is bound to its digest schema; digest_projection.provider_bundle(name, root/.claude/skills/harness/schemas/digest) raising ProjectionError gives RELPATH: digest schema for NAME cannot be projected: ERROR; meta output not equal to that bundle gives RELPATH output differs from schemas/digest/NAME.json; run .claude/skills/harness/bin/gen-agent-output.py. Errors keep the CHECKS order.
    Run the literal verify from the PRODUCT checkout root; expected: agent output: ok, OMP port surface: ok, every check-omp-port case passed, check-skill-weight exits 0, exit 0.
- id: T-05
  title: Prove on OMP 19.2.1 that the generated frontmatter binds a child's yield and hides the schema parameters
  traces: [SC-05]
  change_type: docs
  execution_mode: main-session-direct
  execution_reason: DEC-174 - a live probe of the cutover result, run by the main session that holds the omp binary and credentials.
  depends_on: [T-04]
  status: ready
  files:
  - .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-frontmatter-binding-probe.md
  verify: |
    set -eu
    python3 - <<'PY'
    import re, subprocess, sys
    note = ".harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-frontmatter-binding-probe.md"
    text = subprocess.run(["git", "show", "HEAD:" + note], capture_output=True, text=True, check=True).stdout
    blob = subprocess.run(["git", "rev-parse", "HEAD:.omp/agents/harness-documentor.md"], capture_output=True, text=True, check=True).stdout.strip()
    def field(key):
        found = re.search("(?m)^" + key + ": (.+)$", text)
        return found.group(1).strip() if found else ""
    keys = field("task_item_keys")
    checks = {
        "omp_version": field("omp_version") == "19.2.1",
        "agent_blob": field("agent_blob") == blob,
        "task_item_keys": bool(keys) and "outputSchema" not in keys and "schemaMode" not in keys,
        "off_schema_yield": field("off_schema_yield") == "rejected",
        "conforming_yield": field("conforming_yield") == "accepted",
    }
    bad = [k for k, ok in checks.items() if not ok]
    print("binding receipt ok" if not bad else "BAD: " + ", ".join(bad))
    sys.exit(1 if bad else 0)
    PY
  intent: |
    Work directly in PRODUCT checkout /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2565-digest-frontmatter-contract; every relative-path edit stays inside it. Main owns this task under DEC-174 and DEC-179, with no engineering-lead dispatch. Source issue 2565. Read this feature's BRIEF.md first; T-04 must have landed and been committed. PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md are absent in this checkout; do not invent or substitute them. Change no code in this task.
    Confirm omp --version prints 19.2.1. In a fresh mktemp -d directory outside every checkout, copy this checkout's .omp/config.yml verbatim to .omp/config.yml, and create .omp/agents/probe-documentor.md whose frontmatter is name probe-documentor, a one-line description, tools [read], spawns [], blocking true, followed by the structured and output lines copied byte-for-byte from .omp/agents/harness-documentor.md at HEAD. Build one conforming harness-documentor object and confirm digest_schema.validate_object of harness-documentor on it returns an empty list before using it. The body tells the child: first call yield with data wrong true; when that is rejected, call yield with the conforming object, given verbatim.
    Run omp -p --no-extensions from that directory with a parent prompt that first prints the item properties of the task tool's parameter schema exactly as its tool definition gives them, then dispatches probe-documentor once and reports the task result's status, data and warnings verbatim. Read the parent and child session transcripts OMP saved for that directory to confirm what the child's two yields received.
    Write .harness/harness/features/BUG-2565-digest-frontmatter-contract/notes/research-frontmatter-binding-probe.md with a Result section holding exactly these lines, key colon space value: omp_version, model, agent_file (.omp/agents/harness-documentor.md), agent_blob (the output of git rev-parse HEAD:.omp/agents/harness-documentor.md), task_item_keys (the item property names, comma separated), off_schema_yield (rejected or accepted), conforming_yield (accepted or rejected); then Method and Evidence sections with the prompts, the transcript excerpts of both yields and the parent's result. No credentials or tokens. Commit the note, then run the literal verify.
    If task_item_keys names outputSchema or schemaMode, or the off-schema yield is accepted, or the conforming one rejected, the verify fails by design: stop and report to the operator that the frontmatter route does not bind as the grilling measured. Expected result otherwise: binding receipt ok, exit 0.
- id: T-06
  title: State the frontmatter contract and the fail-closed yield in README, BUILD, SPEC, harness-team and the decision record
  traces: [SC-09, SC-10, SC-11]
  change_type: docs
  execution_mode: main-session-direct
  execution_reason: DEC-174 - the operator routed every task of this gate change main-session-direct; DEC-254 requires a task owning DECISIONS.md.
  depends_on: [T-01, T-02, T-04, T-05]
  status: ready
  files:
  - .harness/README.md
  - .harness/harness/docs/BUILD.md
  - .harness/harness/docs/SPEC.md
  - .claude/skills/harness-team/SKILL.md
  - .harness/harness/docs/DECISIONS.md
  - .harness/harness/docs/DECISIONS-INDEX.md
  verify: |
    set -eu
    python3 .agents/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md
    for f in .harness/README.md .harness/harness/docs/BUILD.md .harness/harness/docs/SPEC.md; do grep -q 'gen-agent-output.py' "$f"; grep -q 'refused, never passed' "$f"; done
    test "$(cat .harness/README.md .harness/harness/docs/BUILD.md .harness/harness/docs/SPEC.md .claude/skills/harness-team/SKILL.md | grep -cE 'outputSchema|schemaMode|hook injects')" = 0
    test "$(grep -c 'feature.yaml' .harness/README.md)" = 0
    python3 - <<'PY'
    import re, sys
    text = open(".harness/harness/docs/DECISIONS.md", encoding="utf-8").read()
    rows = {
        "DEC-100": "`check-domain.py`, `bash-write-guard.py`, `dispatch-guard.py` and `validate-digest.py` an own",
        "DEC-126": "Python, while the OMP adapter resolves and projects them into the strict provider bundle injected",
        "DEC-127": "call so an own exception returns 0 — fail OPEN, on our own",
        "DEC-206": "the task hook injects strict schemas only for `harness-*` personas",
        "DEC-208": "Failing closed on our own gap was rejected in one clause: it would wedge",
        "DEC-237": "**Dispatch owns schema delivery.** Before any claim side effect, the OMP task hook refuses",
    }
    bad = []
    for dec, clause in rows.items():
        found = re.search(r"(?ms)^## " + dec + r" .*?(?=^## DEC-|\Z)", text)
        if not found:
            bad.append(dec + " entry missing")
            continue
        if clause in found.group(0):
            bad.append(dec + " clause still present")
        if "BUG-2565" not in found.group(0):
            bad.append(dec + " names no BUG-2565")
    print("decisions ok" if not bad else "; ".join(bad))
    sys.exit(1 if bad else 0)
    PY
  intent: |
    Work directly in PRODUCT checkout /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2565-digest-frontmatter-contract; every relative-path edit stays inside it. Main owns this task under DEC-174 and DEC-179, with no documentor dispatch. Source issue 2565. Read this feature's BRIEF.md, plan.yaml decisions D-01 to D-05 and decisions_affected, notes/research-digest-frontmatter-contract.md, notes/research-yield-refusal-probe.md and notes/research-frontmatter-binding-probe.md first. PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md are absent in this checkout; do not invent or substitute them. Historical feature observation notes are not edited.
    The contract every document states: each harness agent definition carries structured true and an output generated from its persona schema plus common.json by .claude/skills/harness/bin/gen-agent-output.py, never hand-edited, and check-omp-port.py fails on drift; global task.structured stays at OMP's default (off), so the task tool exposes no schema parameter and a dispatcher has nothing to supply, copy or be refused for; agent frontmatter cannot set strict mode, so the yield hook is the barrier: a yield with no data is refused, and a yield the validator cannot check is refused, never passed; that refusal says the fault is Harness's, tells the child to yield the same object once more and then stop, and differs from a contract refusal, which carries the validator's own reason. Also state the measured behaviour from notes/research-yield-refusal-probe.md: whether a hook-refused yield consumes one of OMP's schema retries, and what the dispatcher's task result carries after repeated refusals.
    .harness/README.md: replace the paragraph beginning The task hook refuses dispatcher-supplied with that contract, including the literal file name gen-agent-output.py and the literal phrase refused, never passed, and the measured behaviour; confirm no feature.yaml remains in the file.
    .harness/harness/docs/BUILD.md: replace numbered steps 1 and 2 of the per-persona list with the frontmatter route; in the failure table delete the row for a dispatcher-supplied schema control, reword the schema load row to a projection failure reported by gen-agent-output.py or check-omp-port.py whose response is to repair the named schema and regenerate, and add a row for validate-digest.py could not run whose response says the yield is refused, never passed, the child yields once more then stops, and the operator repairs the validator; include gen-agent-output.py, and state the measured behaviour.
    .harness/harness/docs/SPEC.md: rewrite the Dispatch paragraph of section 8.3 to the frontmatter route citing symbols, not line numbers; in Refusal, unavailable, allow, state that validate-digest.py reports its own failure as unavailable like the other three broad gates but the yield phase refuses on it (refused, never passed), and that the other three still let the call proceed; include gen-agent-output.py.
    .claude/skills/harness-team/SKILL.md: replace the OMP hook injects your persona's strict schema with your persona's schema comes from your agent definition, keeping the rest of that sentence.
    .harness/harness/docs/DECISIONS.md: amend in place, never strike (DEC-188), each decisions_affected amend row, replacing its quoted clause and naming BUG-2565 in the entry. DEC-100: the every-call bullet becomes write, Bash and dispatch gates fail open visibly while validate-digest.py reports unavailable and the yield is refused (D-05, D-02), and the sentence Failing these gates closed stays refused is narrowed to those three. DEC-126: the projection is digest_projection.py, generated into agent frontmatter by gen-agent-output.py and drift-checked by check-omp-port.py (D-01). DEC-127: the script still returns 0 with the unavailable line; since BUG-2565 the yield carrying it is refused. DEC-206: only harness-* agent definitions carry a digest schema, in frontmatter. DEC-208: the script posture is unchanged but the yield is refused on it, and the rejected fail-closed clause is replaced by the operator's reversal for the yield and its reason. DEC-237: replace the Dispatch owns schema delivery paragraph with an Agent definitions own schema delivery paragraph stating the contract above, D-04, and that the BUG-2305 exact-copy exception is gone; add to Yield owns live validation that a validator that cannot run refuses the yield. Then run python3 .agents/skills/harness/bin/gen-decisions-index.py to regenerate the index, and hand-edit the text after the double colon on the DEC-100, DEC-127, DEC-208 and DEC-237 rows so none asserts hook injection or a passing yield on validator failure (the generator preserves that text and never writes it).
    Run the literal verify from the PRODUCT checkout root; expected: no index diff, every grep satisfied, decisions ok, exit 0.
