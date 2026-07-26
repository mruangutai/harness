#!/usr/bin/env python3
"""Validate an agent's three-part return against the NORMATIVE DIGEST schema.

WHY: SPEC 8.1 declares the schemas normative and the runner routes on exact field
names and enum values — but nothing validated them except the consuming LLM.
SPEC 8.3 catches MISSING returns, not DRIFTED ones. `severity_max: medium` instead
of `med`, `must-fix` instead of `must_fix`, `matrix_ok: "mostly"` — an LLM reader
charitably normalizes all of those, so drift is invisible by construction and the
system behaves correctly right up until one routing decision doesn't.

Usage:  validate-digest.py <persona> [file]      (reads stdin if no file)
Exit 0 = valid.  Exit 1 = contract violation (reasons on stdout).

A violation routes into the BLOCKED (contract violation) path SPEC 8.3 already
defines. Never guess a verdict — silent misrouting is worse than a halt.
"""
import sys, re, json

VERDICTS = {"PASS", "FAIL", "BLOCKED", "ESCALATE"}
SEV      = ["info", "low", "med", "high", "critical"]

# field -> (allowed values | type). Enums are EXACT; near-misses are the whole point.
SCHEMAS = {
    "pm": {"feasibility": {"clear","risky","blocked"}, "surface": {"S","M","L"},
           "recommend": {"proceed","spike","reframe","halt"}, "risk": {"low","med","high"},
           "tasks": int, "decisions": int, "needs_approval": bool, "flags": list},
    "dev": {"tests_added": int, "suite": {"pass","fail"}, "blocked_on": str},
    "qa": {"suite": {"pass","fail"}, "failures": int, "coverage_gaps": list, "matrix_ok": bool},
    "reviewer": {"severity_max": set(SEV), "findings": int, "must_fix": list},
    "visual-designer": {"contract": {"written","updated"}, "mockups": list, "direction_choices": list},
    "documentor": {"docs_updated": list, "gaps": list},
    "dev-ops": {"change_type": {"config","scaffolding","infra","ci"},
                "applied": list, "suite": {"pass","fail","n/a"}},
    "lead": {"crew": str, "steps_run": int, "cycles_used": int,
             "members": list, "must_fix": list},
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

def parse_scalar(v):
    v = v.strip().strip('"\'')
    if v.lower() in ("true", "false"): return v.lower() == "true"
    if re.fullmatch(r"-?\d+", v): return int(v)
    if v.startswith("["): return [x.strip() for x in v[1:-1].split(",") if x.strip()]
    return v

def validate(persona, text):
    err, seen = [], {}
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

    # NOTE the hyphen in the class: a drifted key like `must-fix` must be PARSED
    # before it can be reported as drift. Omitting it made this validator blind to
    # exactly the defect class it exists to catch.
    for k, v in re.findall(r"^\s*([a-z_][a-z0-9_-]*):\s*(.*)$", text, re.M):
        seen[k] = parse_scalar(v)

    # --- catch DRIFTED key spellings before reporting them as merely missing.
    for k in list(seen):
        for want in schema:
            if k != want and k.replace("-", "_").lower() == want:
                err.append(f"key {k!r} is drifted spelling of {want!r} — the runner "
                           f"routes on the exact name and will not see it.")

    for field, allowed in schema.items():
        if field not in seen:
            continue                      # presence is the persona's business; shape is ours
        val = seen[field]
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
    oq = re.search(r"^\s*open_questions:\s*(.*)$", text, re.M)
    if oq and re.fullmatch(r"\d+", oq.group(1).strip()):
        err.append("open_questions is a COUNT; it must be a list of structured items — "
                   "it is an active routing signal, not a tally.")
    return err

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: validate-digest.py <persona> [file]"); sys.exit(2)
    text = open(sys.argv[2]).read() if len(sys.argv) > 2 else sys.stdin.read()
    errs = validate(sys.argv[1], text)
    if errs:
        print("VERDICT: BLOCKED (contract violation)")
        for e in errs: print(f"  - {e}")
        sys.exit(1)
    print("digest ok")
