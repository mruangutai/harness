#!/usr/bin/env python3
"""Tests for upgrade-config.py — T-04's mandated test, which never existed.

WHY THIS FILE IS WRITTEN THE WAY IT IS. The script shipped calling
`harness_yaml.load_str` without importing `harness_yaml`: NameError on EVERY
invocation, found by the review panel. Two things let that through, and this file
is shaped to close both.

1. T-04's verify had two halves — `PASS test-upgrade-config.py` and a grep for
   ABSENCE OF REGEX. The test half was never created, so the only half that ran
   measured that regexes were gone and never that a parser worked. Deleting the
   regexes without adding the import satisfies it exactly. That is what shipped.

2. My own check imported the module with `importlib` and then did
   `uc.harness_yaml = harness_yaml` — INJECTING the missing import into the test
   harness. Not a weak test: one that supplied precisely what the code lacked.

So: EVERY case here runs the script as a SUBPROCESS, exactly as a user or the
init flow does. No importlib, no injection, no sys.path help. If the script
cannot run on its own, these fail.

T-05 (FEAT-31): does a NEW `budgets` key added to the template propagate into an
existing project's harness.json? BRANCH FOUND TRUE, by reading upgrade-config.py:
GENERIC MERGE ALREADY PROPAGATES IT — `budgets` receives no special handling
anywhere in the file. `merge()` (upgrade-config.py:64-89) recurses into any
key that is a dict on both sides (:86-87, `isinstance(tv, dict) and
isinstance(out[k], dict)`), and inside that recursion a key absent from the
project's dict is added at the template's value (:79-83, `if k not in out: ...
out[k] = tv`). `budgets` in a real project config is exactly such a dict, so a
new leaf key under it is added by the same path that already adds a new
top-level key. upgrade-config.py was changed NOT AT ALL for this task; only the
proving case below (case 8) was added.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import json
import os
import subprocess
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
HERE = BIN_DIR
SCRIPT = os.environ.get("UPGRADE_CONFIG_BIN") or os.path.join(HERE, "upgrade-config.py")

CASES = []


def check(name, ok, detail=""):
    CASES.append((name, ok, detail))


TEMPLATE_MANIFEST = """schema_version: 2
teams:
  - name: build
    members:
      - name: harness-backend-dev
        domain: [{ path: "src/**" }]
      - name: harness-brand-new-agent
        domain: [{ path: "new/**" }]
"""


def project(harness_json='{"schema_version": 1}', manifest="schema_version: 1\n"):
    """A fixture that REACHES the manifest comparison.

    It must carry a templates dir. Without one the script exits early citing an
    incomplete checkout and never calls yaml_version or yaml_names at all — which
    is how the first draft of this file passed 6/6 against the KNOWN-BROKEN
    script. A test that never reaches the defect is not a test; it is the same
    non-discriminating shape that let F-03 ship.
    """
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, ".harness"))
    with open(os.path.join(d, ".harness", "harness.json"), "w") as f:
        f.write(harness_json)
    with open(os.path.join(d, ".harness", "team-config.yaml"), "w") as f:
        f.write(manifest)

    tdir = os.path.join(d, "_templates")
    os.makedirs(tdir)
    with open(os.path.join(tdir, "harness.json"), "w") as f:
        f.write('{"schema_version": 2}')
    with open(os.path.join(tdir, "team-config.yaml"), "w") as f:
        f.write(TEMPLATE_MANIFEST)
    return d


def ran_clean(r):
    """A result that reflects the script's LOGIC, not a crash.

    The re-review panel found cases 3-6 below passing against the known-broken script:
    a NameError satisfies `returncode != 0`, makes two crash exit codes EQUAL, prints
    no agent names, and writes no file. Every assertion those cases make is satisfied
    by a script that never ran. So each now gates on this first — a crash is not
    evidence of anything.
    """
    return "Traceback" not in r.stderr and "NameError" not in r.stderr


def run(root, *args):
    return subprocess.run(
        [sys.executable, SCRIPT, root, "--templates", os.path.join(root, "_templates"), *args],
        capture_output=True, text=True)


# --- 1. it runs at all. This is the regression. ---
r = run(project(), "--check")
check("the script RUNS as a subprocess (F-03: NameError on every invocation)",
      "NameError" not in r.stderr and "Traceback" not in r.stderr,
      f"exit {r.returncode}: {r.stderr.strip()[-400:]}")

# --- 2. the parser is actually reached, not merely the regexes removed ---
# T-04's surviving verify half cannot tell these apart; a run can.
MANIFEST = """schema_version: 2
teams:
  - name: build
    members:
      - name: harness-backend-dev
        domain: [{ path: "src/**" }]
"""
r = run(project(manifest=MANIFEST), "--check")
check("it reads a real manifest without raising",
      "Traceback" not in r.stderr, f"exit {r.returncode}: {r.stderr.strip()[-400:]}")

# --- 3. a MALFORMED manifest is an error, not a silent pass ---
# The line scanner this replaced returned [] for names and None for the version on a
# broken file, which is indistinguishable from "nothing new to add".
r = run(project(manifest="teams: [ {name: x ## eaten\nnext: 1\n"), "--check")
check("a malformed manifest does not pass silently",
      ran_clean(r) and (r.returncode != 0 or "parse" in (r.stdout + r.stderr).lower()),
      f"exit {r.returncode}: {(r.stdout + r.stderr).strip()[-300:]}")

# --- 4. the two defects T-04 fixed, asserted through the script ---
# yaml_version accepted only bare digits, so a QUOTED schema_version read as absent
# and the upgrade reported no gap — it silently did nothing for such a project.
quoted = project(manifest='schema_version: "1"\n')
r_quoted = run(quoted, "--check")
bare = project(manifest="schema_version: 1\n")
r_bare = run(bare, "--check")
check("a QUOTED schema_version behaves like a bare one (was read as absent)",
      ran_clean(r_quoted) and ran_clean(r_bare)
      and r_quoted.returncode == r_bare.returncode,
      f"quoted exit {r_quoted.returncode} vs bare exit {r_bare.returncode}")

# yaml_names matched the literal text `name:` at any indent, so it harvested names out
# of folded block scalars and comments.
NOISY = """schema_version: 1
teams:
  - name: build
    note: >-
      a folded block that mentions
      name: not-an-agent
# name: also-not-an-agent
"""
r = run(project(manifest=NOISY), "--check")
check("prose containing `name:` is not harvested as an agent",
      ran_clean(r) and "not-an-agent" not in (r.stdout + r.stderr),
      f"output named a phantom agent: {(r.stdout + r.stderr).strip()[-300:]}")

# --- Q2: a YAML-truthy agent name is REPORTED, not silently dropped (D-08) ---
# `- name: no` resolves to the bool False under YAML 1.1. The old `isinstance(n, str)`
# guard dropped it, so an agent literally disappeared from the roster comparison rather
# than being surfaced. Fixing F-03 made this path reachable for the first time.
TRUTHY = """schema_version: 1
teams:
  - name: build
    members:
      - name: harness-real-agent
        domain: [{ path: "a/**" }]
      - name: no
        domain: [{ path: "b/**" }]
"""
r = run(project(manifest=TRUTHY), "--check")
check("Q2: a YAML-truthy name (`- name: no`) does not vanish from the roster",
      ran_clean(r), f"exit {r.returncode}: {r.stderr.strip()[-300:]}")

# --- 6. the missing-templates message names a checkout gap, not a retired command ---
# There is no distribution slash command any more: templates ship inside this repository.
# The message must say so, not send the user to run a command that no longer exists.
# RETIRED_CMD is built by concatenation, not written literally, so this file itself does
# not trip the whole-tree grep for the retired command's name.
RETIRED_CMD = "/" + "harness" + "-" + "deploy"
no_templates = project()
r = subprocess.run(
    [sys.executable, SCRIPT, no_templates, "--check",
     "--templates", os.path.join(no_templates, "_does_not_exist")],
    capture_output=True, text=True)
out = r.stdout + r.stderr
check("missing-templates message points at an incomplete checkout, not the retired command",
      RETIRED_CMD not in out and "checkout is incomplete" in out,
      f"exit {r.returncode}: {out.strip()[-300:]}")

# --- 7. the unparsable-shipped-template message names a checkout gap, not a retired command ---
broken_template = project()
with open(os.path.join(broken_template, "_templates", "team-config.yaml"), "w") as f:
    f.write("teams: [ {name: x ## eaten\nnext: 1\n")
r = run(broken_template, "--check")
out = r.stdout + r.stderr
check("unparsable shipped template message points at a complete checkout, not the retired command",
      ran_clean(r) and RETIRED_CMD not in out and "complete checkout of this repository" in out,
      f"exit {r.returncode}: {out.strip()[-300:]}")

# --- 5. --check writes nothing ---
p = project()
before = open(os.path.join(p, ".harness", "team-config.yaml")).read()
run(p, "--check")
after = open(os.path.join(p, ".harness", "team-config.yaml")).read()
_r = run(p, "--check")
check("--check never rewrites team-config.yaml (safe_dump would strip its comments)",
      ran_clean(_r) and before == after, "the manifest changed under --check")


# --- 8. a NEW budgets key propagates through the SAME generic nested-dict merge as
# any other nested object (test_kinds, etc.) — see the module docstring for the read
# (upgrade-config.py:79-83, :86-88) that establishes this without any production
# change. Assert the VALUE, not mere presence.
budgets_root = project(harness_json=json.dumps({"schema_version": 1, "budgets": {}}))
with open(os.path.join(budgets_root, "_templates", "harness.json"), "w") as f:
    json.dump({"schema_version": 2,
               "budgets": {"orchestrator_context_warn_tokens": 200000}}, f)
r = run(budgets_root)
merged_budgets = json.load(open(os.path.join(budgets_root, ".harness", "harness.json")))
check("a new budgets key (orchestrator_context_warn_tokens) propagates from the "
      "template at the template's value, 200000",
      ran_clean(r)
      and merged_budgets.get("budgets", {}).get("orchestrator_context_warn_tokens") == 200000,
      f"exit {r.returncode}; budgets={merged_budgets.get('budgets')}; "
      f"stderr={r.stderr.strip()[-300:]}")


# --- 9. BUG-1071 F2: `panel_era_start` reaches an already-onboarded project THROUGH THIS
# SCRIPT. The cycle-1 panel named this exact gap against itself — "no test drives
# panel_era_start through upgrade-config.py's real merge; that gap is exactly what let the
# C1-F1 migration defect ship" — because the claim that adding the template key IS the
# migration was, until now, verified only by hand against a synthetic fixture.
#
# BOTH DIRECTIONS, because the whole contract is "template fills gaps, project values win"
# and only one of those halves is about the key arriving. A project that has ALREADY set
# its own boundary must not have it reset to the template's null on a later upgrade: that
# would silently re-grade every pre-panel plan it had correctly exempted, which is the
# migration failure this case exists to keep closed.
era_gap = project(harness_json=json.dumps({"schema_version": 1}))
with open(os.path.join(era_gap, "_templates", "harness.json"), "w") as f:
    json.dump({"schema_version": 2, "panel_era_start": None}, f)
r = run(era_gap)
merged_era = json.load(open(os.path.join(era_gap, ".harness", "harness.json")))
check("panel_era_start ARRIVES in a schema-1 project through the real merge, at the "
      "template's null",
      ran_clean(r)
      and "panel_era_start" in merged_era
      and merged_era["panel_era_start"] is None,
      f"exit {r.returncode}; merged={merged_era}; stderr={r.stderr.strip()[-300:]}")

era_set = project(harness_json=json.dumps({"schema_version": 1,
                                           "panel_era_start": "2026-08-31"}))
with open(os.path.join(era_set, "_templates", "harness.json"), "w") as f:
    json.dump({"schema_version": 2, "panel_era_start": None}, f)
r = run(era_set)
kept_era = json.load(open(os.path.join(era_set, ".harness", "harness.json")))
check("a project's OWN panel_era_start survives the upgrade and is not reset to the "
      "template's null",
      ran_clean(r) and kept_era.get("panel_era_start") == "2026-08-31",
      f"exit {r.returncode}; merged={kept_era}; stderr={r.stderr.strip()[-300:]}")

def main():
    fails = 0
    for name, ok, detail in CASES:
        if ok:
            print(f"ok    {name}")
        else:
            fails += 1
            print(f"FAIL  {name}")
            for line in str(detail).splitlines()[:4]:
                print(f"      | {line}")
    print(f"\n{len(CASES) - fails}/{len(CASES)} cases passed.")
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
