#!/usr/bin/env python3
"""Validate an agent's three-part return against the NORMATIVE DIGEST schema.

WHY: SPEC 8.1 declares the schemas normative and the runner routes on exact field
names and enum values — but nothing validated them except the consuming LLM.
SPEC 8.3 catches MISSING returns, not DRIFTED ones. `severity_max: medium` instead
of `med`, `must-fix` instead of `must_fix`, `matrix_ok: "mostly"` — an LLM reader
charitably normalizes all of those, so drift is invisible by construction and the
system behaves correctly right up until one routing decision doesn't.

EVERY FIELD IS REQUIRED. An absent field is a violation, not a shortcut: silence
is ambiguous ("none found" or "forgot to collate?") while an explicit `[]` is a
positive assertion that the agent looked. Lists say nothing with `[]`; scalars
that can be genuinely inapplicable say it with `none`. This is stricter than the
first version, which skipped absent fields and therefore let a lead digest ship
missing `members:` — the field SPEC calls load-bearing — while reporting "ok".

Usage:  validate-digest.py <persona> [file]      (reads stdin if no file)
        validate-digest.py --hook                 (SubagentStop hook; exit 2 rejects)
Exit 0 = valid.  Exit 1 = contract violation (reasons on stdout).

A violation routes into the BLOCKED (contract violation) path SPEC 8.3 already
defines. Never guess a verdict — silent misrouting is worse than a halt.
"""
import sys, re, json

VERDICTS = {"PASS", "FAIL", "BLOCKED", "ESCALATE"}
SEV      = ["info", "low", "med", "high", "critical"]

# Required of EVERY persona — the universal return contract (harness-handoff).
UNIVERSAL = {"open_questions": list, "files_touched": list, "expertise_update": list}

# Scalars where "not applicable" is a real answer. The key is still required; the
# value may be `none`/`null`, which asserts inapplicability rather than omitting it.
NULLABLE = {"branch", "blocked_on"}

# field -> (allowed values | type). Enums are EXACT; near-misses are the whole point.
SCHEMAS = {
    "pm": {"feasibility": {"clear","risky","blocked"}, "surface": {"S","M","L"},
           "recommend": {"proceed","spike","reframe","halt"}, "risk": {"low","med","high"},
           "tasks": int, "decisions": int, "needs_approval": bool, "flags": list,
           "sc_status": list},
    "dev": {"tests_added": int, "suite": {"pass","fail"}, "blocked_on": str},
    "qa": {"suite": {"pass","fail"}, "failures": int, "coverage_gaps": list, "matrix_ok": bool},
    "reviewer": {"severity_max": set(SEV), "findings": int, "must_fix": list},
    "visual-designer": {"contract": {"written","updated"}, "mockups": list, "direction_choices": list},
    "documentor": {"docs_updated": list, "gaps": list},
    "dev-ops": {"change_type": {"config","scaffolding","infra","ci"},
                "applied": list, "suite": {"pass","fail","n/a"}},
    # SPEC 10.4 in full. `sc_status` is pm's field (11.6) riding up as a passthrough,
    # surfaced at team level so the orchestrator can read goal-check status without
    # opening member entries; `[]` when this team ran no goal-check.
    "lead": {"team": str, "steps_run": int, "cycles_used": int,
             "members": list, "must_fix": list, "branch": str,
             "escalations": list, "sc_status": list},
}
ALIAS = {
    "harness-pm": "pm", "harness-qa": "qa", "harness-documentor": "documentor",
    "harness-dev-ops": "dev-ops", "harness-visual-designer": "visual-designer",
    "harness-frontend-dev": "dev", "harness-backend-dev": "dev",
    "harness-ai-dev": "dev", "harness-data-engineer": "dev",
    "harness-code-reviewer": "reviewer", "harness-security-reviewer": "reviewer",
    "harness-ui-reviewer": "reviewer",
    "harness-product-lead": "lead", "harness-eng-lead": "lead",
    "harness-validator-lead": "lead",
}

def norm(p):
    return ALIAS.get(p, ALIAS.get("harness-" + p, p))

def strip_comment(v):
    """Drop a trailing YAML `# comment`, respecting quotes and brackets.

    Not cosmetic. SPEC 10.4 and the runner both annotate their templates inline, so
    an agent copying either writes `steps_run: 3   # …`. Without this, that parsed as
    the STRING "3   # …" and failed "must be an integer", and worse — `members:   # …`
    parsed as a scalar, so the block list under it was never seen. The validator
    rejected its own documented format.

    A `#` inside quotes or brackets is content: `headline: "fixes #42"`.
    """
    out, q, depth = [], None, 0
    for i, c in enumerate(v):
        if q:
            out.append(c)
            if c == q:
                q = None
            continue
        if c in "\"'":
            q = c
        elif c in "[{":
            depth += 1
        elif c in "]}":
            depth = max(0, depth - 1)
        elif c == "#" and depth == 0 and (i == 0 or v[i - 1] in " \t"):
            break
        out.append(c)
    return "".join(out).strip()


def parse_scalar(v):
    v = v.strip().strip('"\'')
    if v.lower() in ("true", "false"): return v.lower() == "true"
    if re.fullmatch(r"-?\d+", v): return int(v)
    if v.startswith("["): return [x.strip() for x in v[1:-1].split(",") if x.strip()]
    return v

def parse_digest(text):
    """Read the DIGEST block into {field: value}, honouring BOTH YAML list styles.

    This replaced a one-line `re.findall(r"^\\s*(key):\\s*(.*)$")`, which had two
    defects that between them made a correct lead digest impossible to write:

    1. `\\s*` after the colon MATCHES NEWLINES. A key with a block-style value
       therefore swallowed the first line of that block as its own scalar, so
       `members:` parsed as the string "- { step: build, ... }" and was reported as
       "must be a list" — while `steps_run` and `cycles_used`, sitting on the same
       source line as `team:` in SPEC 10.4's own template, were never seen at all.
       The normative example in the spec could not pass the validator that enforces it.
    2. It harvested keys at EVERY depth. A `must_fix:` nested inside one member entry
       satisfied the top-level `must_fix` requirement — a false pass on exactly the
       roll-up field the lead digest exists to carry.

    So: values never cross a line, and only keys at the DIGEST block's own indent
    are digest fields. Deeper keys belong to a member entry and are that member's.
    """
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines)
                  if re.match(r"^\s*DIGEST:\s*$", l)), None)
    if start is None:
        return {}

    body = lines[start + 1:]
    # Base indent = the first real key under DIGEST:. Everything deeper is nested.
    base = next((len(l) - len(l.lstrip())
                 for l in body
                 if l.strip() and re.match(r"^\s*[a-z_][a-z0-9_-]*:", l)), None)
    if base is None:
        return {}

    out = {}
    for i, line in enumerate(body):
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        if indent < base:
            break                      # dedented out of the block (`artifact:`)
        if indent != base:
            continue                   # nested — belongs to a member, not to us
        # NOTE the hyphen in the class: a drifted key like `must-fix` must be PARSED
        # before it can be reported as drift. Omitting it made this validator blind
        # to exactly the defect class it exists to catch.
        m = re.match(r"^\s*([a-z_][a-z0-9_-]*):[ \t]*(.*)$", line)
        if not m:
            continue
        k, v = m.group(1), strip_comment(m.group(2))
        if v:
            out[k] = parse_scalar(v)
            continue
        # Empty value: a block list if the next non-blank deeper line is an item.
        items = []
        for nxt in body[i + 1:]:
            if not nxt.strip():
                continue
            nind = len(nxt) - len(nxt.lstrip())
            if nind <= base:
                break
            if nxt.lstrip().startswith("- "):
                items.append(strip_comment(nxt.lstrip()[2:]))
        # `key:` with nothing under it is an EMPTY LIST, not a missing field. Writing
        # a bare `escalations:` is the natural way to say "none" and must not read as
        # an omission — the point of requiring the key is that the agent asserted it.
        out[k] = items
    return out


def validate(persona, text):
    err = []
    persona = norm(persona)
    schema = SCHEMAS.get(persona)
    if schema is None:
        return [f"unknown persona {persona!r} — cannot validate; refusing to pass it."]

    # --- VERDICT: exact token, exact spelling.
    m = re.search(r"^\s*VERDICT:\s*(\S+)", text, re.M)
    if not m:
        err.append("no VERDICT: line — this is a contract violation, not a verdict of any kind.")
    elif m.group(1) not in VERDICTS:
        err.append(f"VERDICT is {m.group(1)!r}; must be exactly one of {sorted(VERDICTS)}.")

    if not re.search(r"^\s*DIGEST:", text, re.M):
        err.append("no DIGEST: block.")
    if not re.search(r"^\s*artifact:\s*\S+", text, re.M):
        err.append("no artifact: path.")
    if not re.search(r"^\s*headline:\s*\S+", text, re.M):
        err.append("DIGEST has no headline: — the orchestrator routes on this.")

    seen = parse_digest(text)

    # --- catch DRIFTED key spellings before reporting them as merely missing.
    for k in list(seen):
        for want in schema:
            if k != want and k.replace("-", "_").lower() == want:
                err.append(f"key {k!r} is drifted spelling of {want!r} — the runner "
                           f"routes on the exact name and will not see it.")

    for field, allowed in {**schema, **UNIVERSAL}.items():
        if field not in seen:
            hint = "`none` if genuinely not applicable" if field in NULLABLE else "`[]` if there are none"
            err.append(f"missing {field!r} — every field is required; write {hint}. "
                       f"An absent field is ambiguous; an explicit empty one asserts you looked.")
            continue
        val = seen[field]
        if field in NULLABLE and isinstance(val, str) and val.lower() in ("none", "null", "n/a"):
            continue
        if isinstance(allowed, set):
            if val not in allowed:
                extra = ""
                if isinstance(val, str):
                    near = [a for a in allowed if isinstance(a, str)
                            and (a.startswith(val[:3]) or val.startswith(a[:3]))]
                    if near: extra = f" (did you mean {near[0]!r}?)"
                err.append(f"{field}={val!r} is not in {sorted(allowed)}{extra}.")
        elif allowed is bool and not isinstance(val, bool):
            err.append(f"{field}={val!r} must be a bool, not {type(val).__name__} "
                       f"— a string like \"mostly\" silently soft-fails a hard gate.")
        elif allowed is int and not isinstance(val, int):
            err.append(f"{field}={val!r} must be an integer.")
        elif allowed is list and not isinstance(val, list):
            err.append(f"{field}={val!r} must be a list.")

    # --- open_questions is a LIST of structured items, never a count (SPEC 8).
    oq = re.search(r"^\s*open_questions:[ \t]*(.*)$", text, re.M)
    if oq and re.fullmatch(r"\d+", oq.group(1).strip()):
        err.append("open_questions is a COUNT; it must be a list of structured items — "
                   "it is an active routing signal, not a tally.")
    return err

def hook_mode():
    """SubagentStop hook: reject a malformed digest at source.

    Exit 2 "prevents the subagent from stopping", so the agent must fix its return
    before it can finish — enforcement rather than a request. This is the same
    answer DEC-19 reached for domain enforcement: prose guarding a contract is
    unenforceable, so a script guards it instead.

    THREE PASS-THROUGHS, each deliberate:

    1. No `agent_type`, or a non-harness one. `Explore`, `general-purpose` and any
       other agent share this hook and have no digest contract. Governing them
       would break every unrelated subagent in the project.
    2. `stop_hook_active`. Set when we are already re-running because a stop hook
       blocked. Blocking again is an infinite loop with no operator escape.
    3. Our own failure — unreadable payload, unknown persona, an exception. We
       fail OPEN and say so on stderr. check-domain.sh set this precedent for the
       same reason: a hook that blocks on its own bug wedges every agent in every
       project the moment a payload shape changes. Blocking is for THEIR contract
       violation, never ours.
    """
    try:
        d = json.load(sys.stdin)
    except Exception as e:
        print(f"check-digest: unreadable hook payload ({e}) — passing through.", file=sys.stderr)
        return 0

    agent = d.get("agent_type") or ""
    if not agent.startswith("harness-"):
        return 0
    if d.get("stop_hook_active"):
        return 0

    text = d.get("last_assistant_message") or ""
    if not text.strip():
        print(f"check-digest: {agent} returned no final message to validate — passing through.",
              file=sys.stderr)
        return 0

    if norm(agent) not in SCHEMAS:
        print(f"check-digest: no schema for {agent} — passing through rather than "
              f"blocking on our own gap.", file=sys.stderr)
        return 0

    errs = validate(agent, text)
    if not errs:
        return 0

    print(f"Your return does not satisfy the digest contract, so it cannot be accepted. "
          f"Fix these and return again — every field is required; say nothing with an "
          f"explicit `[]`, or `none` for a scalar that genuinely does not apply:",
          file=sys.stderr)
    for e in errs:
        print(f"  - {e}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    if "--hook" in sys.argv:
        sys.exit(hook_mode())
    if len(sys.argv) < 2:
        print("usage: validate-digest.py <persona> [file]   |   --hook  (SubagentStop)"); sys.exit(2)
    text = open(sys.argv[2]).read() if len(sys.argv) > 2 else sys.stdin.read()
    errs = validate(sys.argv[1], text)
    if errs:
        print("VERDICT: BLOCKED (contract violation)")
        for e in errs: print(f"  - {e}")
        sys.exit(1)
    print("digest ok")
