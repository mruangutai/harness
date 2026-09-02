#!/usr/bin/env python3
"""FEAT-45 — the adversarial plan panel's WIRING, asserted mechanically.

This grades the doctrine files T-02/T-03/T-04/T-06/T-09/T-11 wrote and committed: the
panel's team definition (`plan-panel.yaml`), its playbook wiring (`SKILL.md`,
`harness-plan.md`), its domain grants (`team-config.yaml`), its roster census
(`.omp/agents/`, `.claude/agents/`), and its spawn allowlists
(`harness-validator-lead.md` frontmatter, `sync-agent-adapters.py`). It runs no agent
and asserts nothing about finding quality — that is qa's job at review time, not this
file's.

Case 8 is the one thing no other case can catch: without it the panel's first failure
would arrive at the first live /harness-plan, with every other case here green, because
the host enforces `spawns:` as a hard preflight allowlist that only a live dispatch
attempt would otherwise exercise.
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
        print("test-plan-panel: PyYAML is not importable from this interpreter "
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
VALIDATOR_LEAD_MD = os.path.join(AGENTS_OMP, "harness-validator-lead.md")
SYNC_ADAPTERS = os.path.join(BIN, "sync-agent-adapters.py")
CHECK_DOMAIN = os.path.join(BIN, "check-domain.sh")
PLAN_PANEL_YAML = os.path.join(TEAMS, "plan-panel.yaml")

FEAT = "FEAT-45-adversarial-plan-panel"

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
    literal needle spanning a source line break (G-09: bold markup breaks
    contiguity) still matches the prose it renders as."""
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


team = None
try:
    team = harness_yaml.load_file(PLAN_PANEL_YAML)
    steps = team["steps"]
    steps_by_id = {s["id"]: s for s in steps}
    should_not_exist = steps_by_id["should-not-exist"]
    scope = steps_by_id["scope"]
except Exception as e:
    print(f"test-plan-panel: cannot load {PLAN_PANEL_YAML}: {e}", file=sys.stderr)
    sys.exit(1)

# --- 1. three readers, three separate assertions — never a file-global match --------
try:
    check("(1a) should-not-exist step's prompt asks what should not be built at all",
          "what here should not be built at all" in should_not_exist.get("prompt", ""),
          should_not_exist.get("prompt"))
except Exception as e:
    check("(1a) should-not-exist step's prompt asks what should not be built at all", False, e)

try:
    check("(1b) scope step's prompt asks which tasks serve no live requirement",
          "which tasks serve no live requirement" in scope.get("prompt", ""),
          scope.get("prompt"))
except Exception as e:
    check("(1b) scope step's prompt asks which tasks serve no live requirement", False, e)

try:
    skill_text = read(SKILL_MD)
    check("(1c) SKILL.md asks does this plan deliver the operator's stated intent",
          "does this plan deliver the operator's stated intent" in _normalize_prose(skill_text))
except Exception as e:
    check("(1c) SKILL.md asks does this plan deliver the operator's stated intent", False, e)

# --- 2. every non-empty outputs entry resolves to its own persona -------------------
for step in steps:
    sid = step["id"]
    outputs = step.get("outputs") or []
    persona = step["persona"]
    if not outputs:
        check(f"(2) {sid} outputs list is empty (its correct state — skipped, not counted)",
              True)
        continue
    for out in outputs:
        rendered = out.replace("{{feat}}", FEAT).replace("{{cycle}}", "0")
        try:
            r = _resolve(rendered)
        except Exception as e:
            check(f"(2) {sid} output {rendered} resolves to persona {persona}", False, e)
            continue
        names = r.stdout.split()
        ok = r.returncode == 0 and any(_agrees(persona, n) for n in names)
        check(f"(2) {sid} output {rendered} resolves to persona {persona}", ok,
              f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")

try:
    goalcheck_path = f".harness/harness/features/{FEAT}/notes/research-{FEAT}-goalcheck-plan-c0.md"
    r = _resolve(goalcheck_path)
    names = r.stdout.split()
    check("(2) the playbook's goal-check note path resolves to harness-pm",
          r.returncode == 0 and "harness-pm" in names,
          f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")
except Exception as e:
    check("(2) the playbook's goal-check note path resolves to harness-pm", False, e)

# --- 3. every loop_back step's outputs carry {{cycle}}, and the note path does too --
for step in steps:
    sid = step["id"]
    on_fail = step.get("on_fail") or {}
    loop_back = on_fail.get("loop_back") if isinstance(on_fail, dict) else None
    if loop_back is None:
        continue
    outputs = step.get("outputs") or []
    try:
        ok = (not outputs) or all("{{cycle}}" in o for o in outputs)
        check(f"(3) {sid}'s loop_back outputs are empty or carry the literal {{{{cycle}}}}",
              ok, outputs)
    except Exception as e:
        check(f"(3) {sid}'s loop_back outputs are empty or carry the literal {{{{cycle}}}}",
              False, e)

try:
    check("(3) the playbook names a c<cycle> suffix on the goal-check note path",
          "c<cycle>" in skill_text)
except Exception as e:
    check("(3) the playbook names a c<cycle> suffix on the goal-check note path", False, e)

# --- 4. should-not-exist is outside the canonical roster; every other step is Validation
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
    validation_members = set()
    for t in tc["teams"]:
        if t.get("team-name") == "Validation":
            validation_members = {m["name"] for m in t["members"]}
            break
    check("(4c) scope persona is a Validation squad member",
          any(_agrees(scope["persona"], m) for m in validation_members),
          f"persona={scope['persona']!r} Validation={sorted(validation_members)}")
    for step in steps:
        if step["id"] == "should-not-exist":
            continue
        ok = any(_agrees(step["persona"], m) for m in validation_members)
        check(f"(4d) {step['id']}'s persona {step['persona']} is a Validation squad member",
              ok, sorted(validation_members))
except Exception as e:
    check("(4c) scope persona is a Validation squad member", False, e)

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
try:
    plan_panel_raw = read(PLAN_PANEL_YAML)
    check("(6) plan-panel.yaml carries no literal `then: halt`",
          "then: halt" not in plan_panel_raw)
except Exception as e:
    check("(6) plan-panel.yaml carries no literal `then: halt`", False, e)

for step in steps:
    sid = step["id"]
    on_fail = step.get("on_fail") or {}
    loop_back = on_fail.get("loop_back") if isinstance(on_fail, dict) else None
    if loop_back is None:
        continue
    try:
        ok = loop_back.get("then") == "escalate" and "max_cycles" in loop_back
        check(f"(6) {sid}'s loop_back carries then: escalate and a max_cycles", ok, loop_back)
    except Exception as e:
        check(f"(6) {sid}'s loop_back carries then: escalate and a max_cycles", False, e)

# --- 7. the Target state bullet in harness-plan.md, sliced by its own label ---------
try:
    plan_md_text = read(PLAN_MD)
    m = re.search(r"- \*\*Target state:\*\*.*?(?=\n- \*\*)", plan_md_text, re.S)
    check("(7a) harness-plan.md has a Target state bullet", m is not None)
    slice_text = m.group(0) if m else ""
    check("(7b) the Target state bullet names plan-panel",
          "plan-panel" in slice_text, slice_text)
    check("(7c) the Target state bullet still names the simplify pass "
          "(added to the sequence, not replacing a step)",
          "simplify" in slice_text, slice_text)
except Exception as e:
    check("(7a) harness-plan.md has a Target state bullet", False, e)

# --- 8. the panel is SPAWNABLE — the one thing no other case here can catch --------
# The persona is READ FROM THE TEAM FILE, never hardcoded (D-14 already renamed it once).
panel_persona = should_not_exist["persona"]

try:
    frontmatter_text = read(VALIDATOR_LEAD_MD).split("---")[1]
    frontmatter = yaml.safe_load(frontmatter_text)
    spawns_list = frontmatter.get("spawns") or []
    check("(8a) the panel persona is in harness-validator-lead.md's frontmatter spawns: "
          "allowlist (the host's preflight enforces this as a hard gate)",
          panel_persona in spawns_list, spawns_list)
except Exception as e:
    check("(8a) the panel persona is in harness-validator-lead.md's frontmatter spawns: "
          "allowlist", False, e)

try:
    spec = importlib.util.spec_from_file_location("sync_agent_adapters_under_test",
                                                    SYNC_ADAPTERS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    spawns_map = getattr(mod, "SPAWNS")
    validator_spawns = spawns_map.get("harness-validator-lead", [])
    check("(8b) the panel persona is in SPAWNS[\"harness-validator-lead\"] in "
          "sync-agent-adapters.py",
          panel_persona in validator_spawns, validator_spawns)
except Exception as e:
    check("(8b) the panel persona is in SPAWNS[\"harness-validator-lead\"] in "
          "sync-agent-adapters.py", False, e)

# --- 9. a superseded run's record survives the re-run (SC-03 direction 2): rendering
#        the same outputs entry at cycle 0 and cycle 1 must not collapse onto one path,
#        and both cycles' rendered paths must still resolve to the step's own persona --
for step in steps:
    sid = step["id"]
    outputs = step.get("outputs") or []
    persona = step["persona"]
    if not outputs:
        check(f"(9) {sid} outputs list is empty (its correct state — skipped, not counted)",
              True)
        continue
    for out in outputs:
        rendered_c0 = out.replace("{{feat}}", FEAT).replace("{{cycle}}", "0")
        rendered_c1 = out.replace("{{feat}}", FEAT).replace("{{cycle}}", "1")
        check(f"(9) {sid} output does not overwrite/supersede a prior cycle's record: "
              f"c0 path differs from c1 path",
              rendered_c0 != rendered_c1,
              f"c0={rendered_c0!r} c1={rendered_c1!r}")
        for cycle_label, rendered in (("c0", rendered_c0), ("c1", rendered_c1)):
            try:
                r = _resolve(rendered)
            except Exception as e:
                check(f"(9) {sid} {cycle_label} output {rendered} resolves to persona "
                      f"{persona} (superseded-run record survives)", False, e)
                continue
            names = r.stdout.split()
            ok = r.returncode == 0 and any(_agrees(persona, n) for n in names)
            check(f"(9) {sid} {cycle_label} output {rendered} resolves to persona "
                  f"{persona} (superseded-run record survives)", ok,
                  f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}")

print(f"\n{ran - fails}/{ran} checks passed." if fails == 0 else f"\n{fails} of {ran} FAILING.")
sys.exit(1 if fails else 0)
