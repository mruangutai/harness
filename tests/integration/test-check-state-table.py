#!/usr/bin/env python3
"""FEAT-62: the invariant table and its four verbs.

Byte-identity of the eight sibling suites is the bar for the MOVE; this suite is the bar for
what the move ADDED — the ordered `INVARIANTS` table, `--list`, `--only`, `--feature`,
`--changed`, and their intersection. Every case here was proven RED against the baseline
checker (CHECK_STATE_BIN pointed at the pre-FEAT-62 copy): a file with no table has no
verbs, so each one either tracebacks, prints the full report, or exits with the baseline's
own contract instead of the verb's.

Fixtures are the two-feature tree below so that ORDER is observable: the baseline iterated
features in filesystem order, which on this machine is not sorted; the runner iterates
sorted, and a case asserts that rather than leaving it to the platform.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_sys.path.insert(0, _anchor_os.path.dirname(_anchor_os.path.abspath(__file__)))

import json
import os
import re
import subprocess
import sys
import tempfile

from check_state_support import SCRIPT, _root_env

FAILS = []


def check(name, ok, detail=""):
    print(f"{'ok' if ok else 'FAIL'} - {name}" + ("" if ok else f"\n      {detail}"))
    if not ok:
        FAILS.append(name)


def run(tmp, *args, env_extra=None):
    env = _root_env(tmp)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run([sys.executable, SCRIPT, *args], cwd=tmp, capture_output=True,
                       text=True, env=env)
    return r.returncode, r.stdout, r.stderr


PLAN_PENDING = """schema: plan/1
feature: {feat}
status: ready
approval:
  status: pending
tasks:
  - id: T-01
    title: t
    change_type: test
    execution_mode: main-session-direct
    files: [a.py]
    verify: true
    intent: x
"""


def two_feature_tree(tmp):
    """FEAT-B and FEAT-A, created in REVERSE name order so a filesystem-order walk and a
    sorted walk can disagree; each has a pending plan (INV-3 notes it) and a STATE.md naming
    a task the plan does not carry (INV-5 violation)."""
    h = os.path.join(tmp, ".harness")
    for feat in ("FEAT-B-second", "FEAT-A-first"):
        d = os.path.join(h, "harness", "features", feat)
        os.makedirs(d)
        with open(os.path.join(d, "plan.yaml"), "w") as f:
            f.write(PLAN_PENDING.format(feat=feat))
        with open(os.path.join(d, "STATE.md"), "w") as f:
            f.write("## Current\n\nT-09 is in flight.\n")
        with open(os.path.join(d, "BRIEF.md"), "w") as f:
            f.write(f"# {feat}\n\n## Approval\n\nstatus: approved\n")
        with open(os.path.join(d, "feature.json"), "w") as f:
            json.dump({"feature_id": feat, "branch": "none", "pr": None, "review_sha": "none",
                       "cycles_used": 0, "max_total_cycles": 10, "runs": [], "mission": "plan",
                       "judgements": [{"at": "2026-01-01T00:00:00+00:00", "by": "harness-pm",
                                       "kind": "mission", "decision": "plan", "reason": "r"}]},
                      f, indent=2)
    os.makedirs(os.path.join(h, "factory"))
    with open(os.path.join(h, "factory", "fleet.yaml"), "w") as f:
        f.write("schema: factory-fleet/1\nrepos:\n  - name: org/x\n    default_branch: main\nworkspace_root: /nonexistent\n")
    with open(os.path.join(h, "harness.json"), "w") as f:
        f.write('{"github": {"sync": false, "repo": null}, "budgets": {"max_total_cycles": 10, '
                '"max_total_runs": 20}, "panel_era_start": null, "seam_era_start": null}\n')
    return h


# --- --list ------------------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    two_feature_tree(tmp)
    code, out, err = run(tmp, "--list")
    rows = [l.split()[0] for l in out.splitlines() if re.match(r"^(INV-\d+|[A-Z-]+)\s", l)]
    check("--list exits 0 and executes nothing (no VIOLATION or note rows)",
          code == 0 and "VIOLATION" not in out and "note " not in out and not err.strip(),
          f"code={code} err={err[-200:]!r}")
    check("--list names every active row once, in table order, INV-35 first and INV-44 last",
          rows and rows[0] == "INV-35" and rows[-3] == "INV-44" and len(rows) == len(set(rows)),
          f"rows={rows}")
    check("--list carries the retired numbers, marked retired, never as runnable rows",
          rows[-2:] == ["INV-9", "INV-10"]
          and all("retired" in l for l in out.splitlines() if l.startswith(("INV-9 ", "INV-10 "))),
          out[-400:])
    check("--list shows each row's scope, reads and authority",
          re.search(r"^INV-26\s+repo\s+.*gh:board", out, re.M) is not None
          and re.search(r"^\s+DEC-203\s+the board agrees", out, re.M) is not None,
          out[:600])

# --- no arguments: the full ordered contract, features in SORTED order -------------------------
with tempfile.TemporaryDirectory() as tmp:
    two_feature_tree(tmp)
    code, out, err = run(tmp)
    inv5 = [l for l in out.splitlines() if "references T-09" in l]
    check("no arguments runs the full table: exit 1 with INV-5 violations for both features",
          code == 1 and len(inv5) == 2, f"code={code}\n{out}")
    check("features are iterated in SORTED order, not filesystem order",
          len(inv5) == 2 and "FEAT-A-first" in inv5[0] and "FEAT-B-second" in inv5[1], "\n".join(inv5))
    check("the report tail is unchanged: rows then exit, no verb-mode chatter",
          not err.strip() and "all state invariants hold" not in out, err[-200:])

# --- --only -------------------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    two_feature_tree(tmp)
    code, out, err = run(tmp, "--only", "INV-5")
    check("--only INV-5 runs exactly that invariant: its two violations and nothing else",
          code == 1 and out.count("VIOLATION") == 2 and "references T-09" in out
          and "approval is pending" not in out, out)
    code, out, err = run(tmp, "--only", "INV-3")
    check("--only INV-3 reports only notes and exits 0",
          code == 0 and "VIOLATION" not in out and out.count("approval is pending") == 2, out)
    code, out, err = run(tmp, "--only", "INV-3,INV-5")
    check("--only takes a comma list and keeps table order (INV-3's notes print after INV-5's violations, as the report always did)",
          code == 1 and out.count("VIOLATION") == 2 and out.count("note") == 2
          and out.index("VIOLATION") < out.index("note "), out)
    code, out, err = run(tmp, "--only", "INV-9")
    check("--only on a RETIRED number resolves deterministically: says so, runs nothing, exit 0",
          code == 0 and "INV-9 is retired" in out and "VIOLATION" not in out, f"code={code} {out}")
    code, out, err = run(tmp, "--only", "INV-99")
    check("--only on an unknown name is a command error: exit 2, names --list",
          code == 2 and "--list" in err and not out.strip(), f"code={code} out={out!r} err={err!r}")

# --- --feature ----------------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    two_feature_tree(tmp)
    code, out, err = run(tmp, "--feature", "FEAT-B-second")
    inv5 = [l for l in out.splitlines() if "references T-09" in l]
    check("--feature limits feature-scoped rows to that feature",
          code == 1 and len(inv5) == 1 and "FEAT-B-second" in inv5[0], out)
    code, out, err = run(tmp, "--feature", "FEAT-B-second", "--only", "INV-5")
    check("--feature and --only INTERSECT",
          code == 1 and out.count("VIOLATION") == 1 and "FEAT-B-second" in out and "note" not in out, out)
    code, out, err = run(tmp, "--feature", "FEAT-NOPE")
    check("--feature naming no feature runs no feature-scoped row (repo rows still speak)",
          "references T-09" not in out and "approval is pending" not in out, f"code={code} {out}")

# --- --changed ----------------------------------------------------------------------------------
def git(tmp, *args):
    return subprocess.run(["git", "-C", tmp, *args], capture_output=True, text=True)


def quiet_repo(tmp):
    """A git repo whose git-backed rows (INV-25/29/31) are silent, so what --changed
    selects by PATH is the only thing that prints."""
    git(tmp, "init", "-q", "-b", "main")
    git(tmp, "config", "user.email", "t@example.com")
    git(tmp, "config", "user.name", "t")
    hooks = os.path.join(tmp, ".claude", "skills", "harness", "hooks")
    os.makedirs(hooks)
    pm = os.path.join(hooks, "post-merge")
    with open(pm, "w") as f:
        f.write("#!/bin/sh\n")
    os.chmod(pm, 0o755)
    git(tmp, "config", "core.hooksPath", os.path.join(".claude", "skills", "harness", "hooks"))
    git(tmp, "add", "-A")
    git(tmp, "commit", "-qm", "fixture")


with tempfile.TemporaryDirectory() as tmp:
    two_feature_tree(tmp)
    quiet_repo(tmp)
    # Rows with git:/gh: inputs cannot be mapped to a path, so --changed always includes them;
    # on this fixture they are silent (no worktrees, no board), which is what makes the
    # path-mapped selection observable.
    code, out, err = run(tmp, "--changed")
    check("--changed on a clean tree runs nothing path-mapped and is SILENT (exit 0, no output)",
          code == 0 and out == "" and err == "", f"code={code} out={out!r} err={err!r}")
    with open(os.path.join(tmp, ".harness", "harness", "features", "FEAT-B-second", "STATE.md"), "a") as f:
        f.write("\nmore\n")
    code, out, err = run(tmp, "--changed")
    check("--changed maps a dirty STATE.md to the rows that read it, scoped to that feature",
          code == 1 and out.count("references T-09") == 1 and "FEAT-B-second" in out
          and "FEAT-A-first" not in out and "approval is pending" not in out, out)
    git(tmp, "add", "-A")
    git(tmp, "commit", "-qm", "state")
    new = os.path.join(tmp, ".harness", "harness", "features", "FEAT-A-first", "notes")
    os.makedirs(new)
    with open(os.path.join(new, "handoff-plan.md"), "w") as f:
        f.write("# Handoff — seq-1\n## Next\nx\n## Trust\nx\n## Dead ends\nx\n## Working set\nx\n## Done when\nx\n")
    code, out, err = run(tmp, "--changed")
    check("--changed sees an UNTRACKED file and selects the rows that read handoff notes, for that feature only",
          "FEAT-A-first" in out and "FEAT-B-second" not in out and "handoff-plan.md" in out
          and "references T-09" not in out, f"code={code} {out}")
    git(tmp, "add", "-A")
    git(tmp, "commit", "-qm", "note")
    git(tmp, "mv", os.path.join(".harness", "harness", "features", "FEAT-A-first", "STATE.md"),
        os.path.join(".harness", "harness", "features", "FEAT-A-first", "STATE.old.md"))
    code, out, err = run(tmp, "--changed", "--only", "INV-2")
    check("--changed handles a RENAME pair: both sides count as dirty, INV-2 runs for that feature and is clean",
          code == 0 and out == "" and err == "", f"code={code} out={out!r} err={err!r}")
    code, out, err = run(tmp, "--changed", "--only", "INV-19")
    check("--changed intersects with --only: a selected row that reads nothing dirty runs nothing (silent)",
          code == 0 and out == "", f"code={code} out={out!r}")

# --- repo rows still narrow through ctx.features -------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    two_feature_tree(tmp)
    for feat in ("FEAT-A-first", "FEAT-B-second"):
        fj = os.path.join(tmp, ".harness", "harness", "features", feat, "feature.json")
        doc = json.load(open(fj))
        doc["factory"] = {"repo": "org/undeclared", "issues": {"T-01": 7}}
        json.dump(doc, open(fj, "w"), indent=2)
    code, out, err = run(tmp, "--only", "INV-24")
    check("a repo-scoped row that loops features sees ALL of them without --feature (INV-24 undeclared-repo finding x2)",
          out.count("INV-24") == 2 and "FEAT-A-first" in out and "FEAT-B-second" in out, out)
    code, out, err = run(tmp, "--only", "INV-24", "--feature", "FEAT-A-first")
    check("...and is narrowed by --feature because it loops ctx.features",
          out.count("INV-24") == 1 and "FEAT-A-first" in out, out)

print(f"\n{'ALL PASSED' if not FAILS else f'{len(FAILS)} FAILING: ' + ', '.join(FAILS)}")
sys.exit(1 if FAILS else 0)
