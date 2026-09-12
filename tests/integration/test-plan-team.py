#!/usr/bin/env python3
"""FEAT-59 — the plan, validate and fix teams' WIRING, asserted mechanically.

Successor to FEAT-45's test-plan-panel.py. FEAT-59 (SC-04, SC-13, SC-14) folded the
adversarial plan panel into ONE product-lead run (`plan.yaml`), the reviewer panel and
pm's goal-check into ONE validator-lead run (`validate.yaml`), and the fix cycle into a
validator-lead run hosting the owning dev (`fix.yaml`). This grades the team definitions,
their playbook wiring (`SKILL.md`, `harness-plan.md`), their domain grants
(`team-config.yaml`), the roster census (`.omp/agents/`, `.claude/agents/`), and the spawn
allowlists (lead frontmatter `spawns:`, `sync-agent-adapters.py`). It runs no agent and
asserts nothing about finding quality — that is qa's job at review time, not this file's.

Case 8 is the one thing no other case can catch: without it a team's first failure
would arrive at the first live dispatch, with every other case here green, because the
host enforces `spawns:` as a hard preflight allowlist that only a live dispatch attempt
would otherwise exercise. Cross-squad hosting (DEC-118 as amended by FEAT-59) is exactly
the case where a lead's allowlist and its team file drift apart.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import importlib.util
import os
import re
import subprocess
import sys

try:
    import harness_yaml
except ModuleNotFoundError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        import harness_yaml
    except ModuleNotFoundError:
        print("test-plan-team: PyYAML is not importable from this interpreter "
              f"({sys.executable}).\n"
              "  install:  python3 -m pip install --user --break-system-packages pyyaml\n"
              "  This is REQUIRED, not optional (DEC-171 am.1).", file=sys.stderr)
        sys.exit(1)

import yaml  # noqa: E402  (harness_yaml import above establishes PyYAML is present)

REPO = (os.environ.get("HARNESS_PROJECT_DIR") or os.environ.get("CLAUDE_PROJECT_DIR")) or os.getcwd()
TEAMS = os.path.join(REPO, ".claude", "skills", "harness", "teams")
BIN = os.path.join(REPO, ".claude", "skills", "harness", "bin")
SKILL_MD = os.path.join(REPO, ".claude", "skills", "harness", "SKILL.md")
PLAN_MD = os.path.join(REPO, ".claude", "commands", "harness-plan.md")
TEAM_CONFIG = os.path.join(REPO, ".harness", "team-config.yaml")
AGENTS_OMP = os.path.join(REPO, ".omp", "agents")
AGENTS_CLAUDE = os.path.join(REPO, ".claude", "agents")
SYNC_ADAPTERS = os.path.join(BIN, "sync-agent-adapters.py")
CHECK_DOMAIN = os.path.join(BIN, "check-domain.sh")
PLAN_YAML = os.path.join(TEAMS, "plan.yaml")
VALIDATE_YAML = os.path.join(TEAMS, "validate.yaml")
FIX_YAML = os.path.join(TEAMS, "fix.yaml")

FEAT = "FEAT-59-proportional-flow"
LEADS = {"harness-product-lead", "harness-eng-lead", "harness-validator-lead"}
KINDS = ("substance", "form", "proportionality")

fails = 0
ran = 0


def check(name, ok, detail=""):
    # Counted, never a literal total: a frozen count reddens the moment a case is added.
    global fails, ran
    ran += 1
    if ok:
        print(f"ok    {name}")
    else:
        fails += 1
        print(f"FAIL  {name}")
        for line in str(detail).splitlines():
            print(f"      | {line}")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _normalize_prose(text):
    """Collapse the house-style ~95-col wrap and strip markdown bold markers so a
    verbatim phrase can be matched whether or not a line break falls inside it."""
    return re.sub(r"\s+", " ", text.replace("*", ""))


def _resolve(path):
    """`check-domain.sh --resolve <path>` — plan-time route resolution, stdin closed."""
    return subprocess.run(
        [CHECK_DOMAIN, "--resolve", path], capture_output=True, text=True,
        stdin=subprocess.DEVNULL, timeout=20, cwd=REPO,
        env=dict(os.environ, CLAUDE_PROJECT_DIR=REPO, HARNESS_PROJECT_DIR=REPO),
    )


def _agrees(persona, resolved_name):
    """Personas in the team file are bare (`code-reviewer`); the resolver prints
    `harness-`-prefixed names. Accept either spelling by comparing on the suffix."""
    return resolved_name == persona or resolved_name == f"harness-{persona}"


def _load_team(path):
    try:
        team = harness_yaml.load_file(path)
        return team, team["steps"], {s["id"]: s for s in team["steps"]}
    except Exception as e:
        print(f"test-plan-team: cannot load {path}: {e}", file=sys.stderr)
        sys.exit(1)


def _spawns_of(lead):
    frontmatter_text = read(os.path.join(AGENTS_OMP, f"{lead}.md")).split("---")[1]
    return yaml.safe_load(frontmatter_text).get("spawns") or []


def _rendered(out, cycle, persona="backend-dev"):
    return (out.replace("{{feat}}", FEAT).replace("{{cycle}}", str(cycle))
               .replace("{{persona}}", persona))


plan, steps, steps_by_id = _load_team(PLAN_YAML)
validate, v_steps, v_by_id = _load_team(VALIDATE_YAML)
fix, f_steps, f_by_id = _load_team(FIX_YAML)
should_not_exist = steps_by_id["should-not-exist"]
scope = steps_by_id["scope"]
READERS = ("scope", "should-not-exist", "design")

# --- 0. the shape SC-04 names: draft → readers in one wave → apply → goalcheck --------
try:
    check("(0a) plan.yaml is hosted by product-lead and its steps are exactly "
          "draft, scope, should-not-exist, design, apply, goalcheck",
          plan["lead"] == "product-lead"
          and set(steps_by_id) == {"draft", *READERS, "apply", "goalcheck"},
          f"lead={plan.get('lead')!r} steps={sorted(steps_by_id)}")
    check("(0b) every reader depends on draft and on nothing else, so the three dispatch "
          "in one turn",
          all(steps_by_id[r]["depends_on"] == ["draft"] for r in READERS),
          {r: steps_by_id[r]["depends_on"] for r in READERS})
    check("(0c) apply depends on every reader; goalcheck depends on apply",
          set(steps_by_id["apply"]["depends_on"]) == set(READERS)
          and steps_by_id["goalcheck"]["depends_on"] == ["apply"],
          f"apply={steps_by_id['apply']['depends_on']} "
          f"goalcheck={steps_by_id['goalcheck']['depends_on']}")
    check("(0d) the plan is drafted, applied and goal-checked by pm — one author",
          all(steps_by_id[s]["persona"] == "pm" for s in ("draft", "apply", "goalcheck")),
          {s: steps_by_id[s]["persona"] for s in ("draft", "apply", "goalcheck")})
except Exception as e:
    check("(0) plan.yaml has the SC-04 shape", False, e)

# --- 1. the readers' questions — separate assertions, never a file-global match ------
try:
    check("(1a) should-not-exist step's prompt asks what should not be built at all",
          "what here should not be built at all" in should_not_exist.get("prompt", ""),
          should_not_exist.get("prompt"))
except Exception as e:
    check("(1a) should-not-exist step's prompt asks what should not be built at all", False, e)

try:
    check("(1b) scope step's prompt asks which tasks serve no live requirement and hunts "
          "orphan SCs, not orphan REQs (SC-12)",
          "which tasks serve no live requirement" in scope.get("prompt", "")
          and "orphan SC" in scope.get("prompt", "")
          and "REQ" not in scope.get("prompt", ""),
          scope.get("prompt"))
except Exception as e:
    check("(1b) scope step's prompt asks which tasks serve no live requirement", False, e)

try:
    skill_text = read(SKILL_MD)
    check("(1c) SKILL.md asks does this plan deliver the operator's stated intent",
          "does this plan deliver the operator's stated intent" in _normalize_prose(skill_text))
    check("(1d) the goalcheck step asks the same question, verbatim",
          "does this plan deliver the operator's stated intent"
          in steps_by_id["goalcheck"].get("prompt", ""),
          steps_by_id["goalcheck"].get("prompt"))
except Exception as e:
    check("(1c) SKILL.md asks does this plan deliver the operator's stated intent", False, e)

# --- 1e. SC-06 / SC-17: every reader prompt carries the kind obligation; qa carries
#         fail_first. A reader that is never told returns unkinded findings that
#         validate-digest.py refuses — and the run is spent before anyone notices.
for team_name, team_steps, readers in (("plan", steps, READERS),
                                       ("validate", v_steps, ("qa", "code", "security", "ui")),
                                       ("fix", f_steps, ("qa", "code", "security", "ui"))):
    for step in team_steps:
        if step["id"] not in readers:
            continue
        prompt = step.get("prompt", "")
        check(f"(1e) {team_name}/{step['id']}'s prompt names `kind`",
              "kind" in prompt, prompt)
for team_name, by_id in (("validate", v_by_id), ("fix", f_by_id)):
    check(f"(1f) {team_name}/qa's prompt names `fail_first` and is gate-only",
          "fail_first" in by_id["qa"].get("prompt", "")
          and by_id["qa"]["mutates_repo"] is False,
          by_id["qa"].get("prompt"))

# --- 1g. SC-05: apply records the panel by verb, and checks the plan, in the same run --
try:
    apply_prompt = steps_by_id["apply"].get("prompt", "")
    check("(1g) apply runs plan-merge.py record-panel and plan-merge.py check",
          "record-panel" in apply_prompt and "plan-merge.py check" in apply_prompt,
          apply_prompt)
except Exception as e:
    check("(1g) apply runs plan-merge.py record-panel and plan-merge.py check", False, e)

# --- 2. every non-empty outputs entry resolves to its own persona -------------------
for team_name, team_steps in (("plan", steps), ("validate", v_steps), ("fix", f_steps)):
    for step in team_steps:
        sid = step["id"]
        outputs = step.get("outputs") or []
        persona = step["persona"]
        if not outputs:
            check(f"(2) {team_name}/{sid} outputs list is empty (its correct state — "
                  f"skipped, not counted)", True)
            continue
        # fix.yaml's dev step is templated; render it as one Engineering member.
        persona = "backend-dev" if persona == "{{persona}}" else persona
        for out in outputs:
            rendered = _rendered(out, 0)
            try:
                r = _resolve(rendered)
            except Exception as e:
                check(f"(2) {team_name}/{sid} output {rendered} resolves to persona "
                      f"{persona}", False, e)
                continue
            names = r.stdout.split()
            ok = r.returncode == 0 and any(_agrees(persona, n) for n in names)
            check(f"(2) {team_name}/{sid} output {rendered} resolves to persona {persona}",
                  ok, f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")

# --- 3. every loop_back step's outputs carry {{cycle}} ------------------------------
for team_name, team_steps in (("plan", steps), ("fix", f_steps)):
    for step in team_steps:
        sid = step["id"]
        on_fail = step.get("on_fail") or {}
        loop_back = on_fail.get("loop_back") if isinstance(on_fail, dict) else None
        if loop_back is None:
            continue
        outputs = step.get("outputs") or []
        try:
            ok = (not outputs) or all("{{cycle}}" in o for o in outputs)
            check(f"(3) {team_name}/{sid}'s loop_back outputs are empty or carry the "
                  f"literal {{{{cycle}}}}", ok, outputs)
        except Exception as e:
            check(f"(3) {team_name}/{sid}'s loop_back outputs are empty or carry the "
                  f"literal {{{{cycle}}}}", False, e)

# --- 4. should-not-exist is outside the canonical roster; the borrowed readers are
#        Validation squad; the fix dev is Engineering squad; nobody hosts a lead ------
try:
    omp_names = {os.path.splitext(f)[0] for f in os.listdir(AGENTS_OMP)
                 if re.match(r"^harness-.*\.md$", f)}
    check("(4a) should-not-exist persona is not a canonical .omp/agents/ role",
          should_not_exist["persona"] not in omp_names, should_not_exist["persona"])
except Exception as e:
    check("(4a) should-not-exist persona is not a canonical .omp/agents/ role", False, e)

try:
    check("(4b) should-not-exist step's outputs list is empty",
          (should_not_exist.get("outputs") or []) == [], should_not_exist.get("outputs"))
except Exception as e:
    check("(4b) should-not-exist step's outputs list is empty", False, e)

try:
    tc = harness_yaml.load_file(TEAM_CONFIG)
    squads = {t.get("team-name"): {m["name"] for m in t["members"]} for t in tc["teams"]}
    validation = squads["Validation"]
    engineering = squads["Engineering"]
    for sid in ("scope", "design"):
        p = steps_by_id[sid]["persona"]
        check(f"(4c) plan/{sid}'s persona {p} is a Validation squad member (borrowed "
              f"read-only under DEC-118 as amended)",
              any(_agrees(p, m) for m in validation), sorted(validation))
    for step in v_steps:
        p = step["persona"]
        ok = any(_agrees(p, m) for m in validation | squads["Product"])
        check(f"(4d) validate/{step['id']}'s persona {p} is a Validation or Product member",
              ok, p)
    check("(4e) fix/fix's persona is the dispatch-resolved `{{persona}}` (the owning dev, "
          "an Engineering member named by the orchestrator)",
          f_by_id["fix"]["persona"] == "{{persona}}", f_by_id["fix"]["persona"])
    for step in f_steps:
        if step["id"] == "fix":
            continue
        p = step["persona"]
        check(f"(4f) fix/{step['id']}'s persona {p} is a Validation squad member",
              any(_agrees(p, m) for m in validation), p)
    all_personas = {s["persona"] for s in steps + v_steps + f_steps}
    check("(4g) no team step names a lead — a lead never spawns a lead",
          not any(_agrees(p, lead) for p in all_personas for lead in LEADS),
          sorted(all_personas))
    check("(4h) the fix dev is never also a reader in the same run: author ≠ reviewer",
          not any(any(_agrees(s["persona"], m) for m in engineering)
                  for s in f_steps if s["id"] != "fix"),
          [s["persona"] for s in f_steps])
except Exception as e:
    check("(4c) squad membership of the borrowed personas", False, e)

# --- 5. the roster census is unchanged: sixteen and sixteen, by the same names ------
try:
    omp_files = sorted(f for f in os.listdir(AGENTS_OMP) if re.match(r"^harness-.*\.md$", f))
    claude_files = sorted(f for f in os.listdir(AGENTS_CLAUDE) if re.match(r"^harness-.*\.md$", f))
    check("(5) .omp/agents/ holds exactly sixteen harness-*.md files",
          len(omp_files) == 16, omp_files)
    check("(5) .claude/agents/ holds exactly sixteen harness-*.md files",
          len(claude_files) == 16, claude_files)
    check("(5) .omp/agents/ and .claude/agents/ name the same sixteen files",
          set(omp_files) == set(claude_files),
          f"omp={sorted(omp_files)} claude={sorted(claude_files)}")
except Exception as e:
    check("(5) the roster census is unchanged: sixteen and sixteen", False, e)

# --- 6. no halt at the cap; every loop_back escalates with a max_cycles -------------
for team_name, path, team_steps in (("plan", PLAN_YAML, steps), ("fix", FIX_YAML, f_steps)):
    try:
        raw = read(path)
        check(f"(6) {team_name}.yaml carries no literal `then: halt`", "then: halt" not in raw)
    except Exception as e:
        check(f"(6) {team_name}.yaml carries no literal `then: halt`", False, e)
    for step in team_steps:
        sid = step["id"]
        on_fail = step.get("on_fail") or {}
        loop_back = on_fail.get("loop_back") if isinstance(on_fail, dict) else None
        if loop_back is None:
            continue
        try:
            ok = loop_back.get("then") == "escalate" and "max_cycles" in loop_back
            check(f"(6) {team_name}/{sid}'s loop_back carries then: escalate and a max_cycles",
                  ok, loop_back)
        except Exception as e:
            check(f"(6) {team_name}/{sid}'s loop_back carries then: escalate and a max_cycles",
                  False, e)

# --- 7. the Target state bullet in harness-plan.md, sliced by its own label ---------
try:
    plan_md_text = read(PLAN_MD)
    m = re.search(r"- \*\*Target state:\*\*.*?(?=\n- \*\*)", plan_md_text, re.S)
    check("(7a) harness-plan.md has a Target state bullet", m is not None)
    slice_text = m.group(0) if m else ""
    check("(7b) the Target state bullet no longer names the retired plan-panel team",
          "plan-panel" not in slice_text, slice_text)
except Exception as e:
    check("(7a) harness-plan.md has a Target state bullet", False, e)

# --- 8. every team is SPAWNABLE — the one thing no other case here can catch --------
# Personas are READ FROM THE TEAM FILES, never hardcoded. The fix dev is templated, so
# every Engineering member must be on the validator lead's allowlist.
try:
    spec = importlib.util.spec_from_file_location("sync_agent_adapters_under_test",
                                                    SYNC_ADAPTERS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    spawns_map = getattr(mod, "SPAWNS")
except Exception as e:
    spawns_map = {}
    check("(8) SPAWNS is importable from sync-agent-adapters.py", False, e)

hosted = {
    "harness-product-lead": {s["persona"] for s in steps},
    "harness-validator-lead": ({s["persona"] for s in v_steps}
                               | {s["persona"] for s in f_steps if s["persona"] != "{{persona}}"}
                               | engineering),
}
for lead, personas in hosted.items():
    try:
        allow = _spawns_of(lead)
        for p in sorted(personas):
            check(f"(8a) {p} is in {lead}.md's frontmatter spawns: allowlist (the host's "
                  f"preflight enforces this as a hard gate)",
                  any(_agrees(p, a) for a in allow), allow)
        check(f"(8c) {lead}.md's spawns: names no lead",
              not (set(allow) & LEADS), allow)
    except Exception as e:
        check(f"(8a) {lead}.md's frontmatter spawns: allowlist is readable", False, e)
    try:
        const = spawns_map.get(lead, [])
        for p in sorted(personas):
            check(f"(8b) {p} is in SPAWNS[{lead!r}] in sync-agent-adapters.py",
                  any(_agrees(p, a) for a in const), const)
    except Exception as e:
        check(f"(8b) SPAWNS[{lead!r}] is readable", False, e)

# --- 9. a superseded run's record survives the re-run (DEC-117): rendering the same
#        cycle-bearing outputs entry at cycle 0 and cycle 1 must not collapse onto one
#        path, and both cycles' rendered paths must still resolve to the step's persona --
for team_name, team_steps in (("plan", steps), ("validate", v_steps), ("fix", f_steps)):
    for step in team_steps:
        sid = step["id"]
        outputs = [o for o in (step.get("outputs") or []) if "{{cycle}}" in o]
        persona = "backend-dev" if step["persona"] == "{{persona}}" else step["persona"]
        for out in outputs:
            rendered_c0 = _rendered(out, 0)
            rendered_c1 = _rendered(out, 1)
            check(f"(9) {team_name}/{sid} output does not overwrite a prior cycle's record: "
                  f"c0 path differs from c1 path",
                  rendered_c0 != rendered_c1, f"c0={rendered_c0!r} c1={rendered_c1!r}")
            for cycle_label, rendered in (("c0", rendered_c0), ("c1", rendered_c1)):
                try:
                    r = _resolve(rendered)
                except Exception as e:
                    check(f"(9) {team_name}/{sid} {cycle_label} output {rendered} resolves to "
                          f"persona {persona}", False, e)
                    continue
                names = r.stdout.split()
                ok = r.returncode == 0 and any(_agrees(persona, n) for n in names)
                check(f"(9) {team_name}/{sid} {cycle_label} output {rendered} resolves to "
                      f"persona {persona}", ok,
                      f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")

print(f"\n{ran - fails}/{ran} checks passed." if fails == 0 else f"\n{fails} of {ran} FAILING.")
sys.exit(1 if fails else 0)
