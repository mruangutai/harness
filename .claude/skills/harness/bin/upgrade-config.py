#!/usr/bin/env python3
"""`/harness-init --upgrade`: merge newer template entries without clobbering the project.

  upgrade-config.py <project-root> [--check] [--templates <dir>]

  (default)  merge harness.json and REPORT on team-config.yaml. Idempotent.
  --check    report the schema_version gap and what would change. Writes nothing.

THE ASYMMETRY IS DELIBERATE:

  harness.json    is JSON -> merged deterministically, here.
  team-config.yaml is YAML -> REPORTED ONLY, never rewritten.

Every script in bin/ runs with zero third-party dependencies on any machine, so
there is no YAML library available. Hand-rolling a YAML *writer* to edit a file
whose `domain` globs must never be clobbered would put the harness's only
write-scope guarantee behind a line-based regex. So this prints the specific new
entries and the user adds them — a manual step is an acceptable price for not
silently corrupting the manifest.

THE PROJECT ALWAYS WINS on a value it already has. `test_kinds.*.cmd` above all:
those are commands dev-ops verified by running, and re-imposing the template's
`null` would turn a working gate back into a soft skip. New template keys are
added; existing project keys are left exactly as they are.

Exit 0 = up to date, or merged. Exit 1 = --check found a gap, or an error.
"""
import json
import os
import re
import shutil
import sys

# Keys whose value is per-project by nature. Never overwritten once set, even if the
# template's value changes. `cmd` above all: dev-ops verified it by running it, and
# re-imposing the template's null would turn a working gate back into a soft skip.
PRESERVE_ALWAYS = ("cmd", "_reason", "detect", "exclude")

# Keys never ADDED where the project omits them — their absence is itself a decision.
# `_reason` explains why a `cmd` is null; pasting the template's "unset — dev-ops has
# not run detection yet" next to a command dev-ops has since verified states a
# falsehood about the project's own config.
NEVER_ADD = ("_reason",)

# Template-only bookkeeping that must never be copied into project state.
TEMPLATE_ONLY = ("_template",)


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def merge(project, template, path=(), added=None):
    """Recursive additive merge: template fills gaps, project values win.

    Returns the merged object. `added` accumulates dotted paths of what was new,
    so the caller can report exactly what changed rather than "updated".
    """
    if added is None:
        added = []
    if not isinstance(project, dict) or not isinstance(template, dict):
        return project
    out = dict(project)
    for k, tv in template.items():
        here = path + (k,)
        if k in TEMPLATE_ONLY:
            continue
        if k not in out:
            if k in NEVER_ADD:
                continue
            out[k] = tv
            added.append(".".join(here))
        elif k in PRESERVE_ALWAYS:
            continue                      # project's verified value stands
        elif isinstance(tv, dict) and isinstance(out[k], dict):
            out[k] = merge(out[k], tv, here, added)
        # scalars and lists the project already set: left alone.
    return out


def yaml_names(text):
    """Every `name:` value in a manifest, in order. Line-scanned, not parsed.

    Same technique and same reason as check-domain.sh: no YAML library exists here,
    and we need exactly one field. Read-only, so a miss under-reports a new agent
    rather than corrupting anything.
    """
    out = []
    for ln in text.splitlines():
        m = re.match(r"^\s*-?\s*(?:name|- name):\s*(\S+)", ln)
        if m:
            out.append(m.group(1).strip("\"'"))
    return out


def yaml_version(text):
    m = re.search(r"^schema_version:\s*(\d+)", text, re.M)
    return int(m.group(1)) if m else None


def main():
    args = list(sys.argv[1:])
    check_only = "--check" in args
    args = [a for a in args if a != "--check"]

    tdir = None
    if "--templates" in args:
        i = args.index("--templates")
        tdir = args[i + 1] if i + 1 < len(args) else None
        del args[i:i + 2]

    if not args:
        print("usage: upgrade-config.py <project-root> [--check] [--templates <dir>]")
        return 1
    root = os.path.abspath(args[0])
    if tdir is None:
        tdir = os.path.join(root, ".claude", "skills", "harness", "templates")
    if not os.path.isdir(tdir):
        print(f"upgrade-config: no templates at {tdir} — run /harness-deploy first.")
        return 1

    gaps = []

    # ---- harness.json: merged --------------------------------------------------
    p_json = os.path.join(root, ".harness", "harness.json")
    t_json = os.path.join(tdir, "harness.json")
    if not os.path.isfile(p_json):
        print(f"upgrade-config: no {p_json} — this project is not initialised. "
              f"Run /harness-init (without --upgrade).")
        return 1
    try:
        proj, tmpl = load_json(p_json), load_json(t_json)
    except Exception as e:
        print(f"upgrade-config: cannot read config ({e})")
        return 1

    pv, tv = proj.get("schema_version"), tmpl.get("schema_version")
    added = []
    merged = merge(proj, tmpl, added=added)
    merged.pop("_template", None)         # a template-only marker; not project state
    merged["schema_version"] = tv

    if added or pv != tv:
        gaps.append("harness.json")
        print(f"harness.json: schema_version {pv} -> {tv}")
        for a in added:
            print(f"  + {a}")
        if not added:
            print("  (no new entries — version bump only)")
        preserved = [f"test_kinds.{k}.cmd = {v.get('cmd')!r}"
                     for k, v in (proj.get("test_kinds") or {}).items()
                     if isinstance(v, dict) and v.get("cmd")]
        for p in preserved:
            print(f"  = preserved {p}")
        if not check_only:
            shutil.copyfile(p_json, p_json + ".harness-bak")
            tmp = p_json + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(merged, f, indent=2)
                f.write("\n")
            os.replace(tmp, p_json)
            print(f"  written (backup at {os.path.basename(p_json)}.harness-bak)")
    else:
        print(f"harness.json: up to date (schema_version {pv}).")

    # ---- team-config.yaml: REPORTED, never rewritten ---------------------------
    p_yaml = os.path.join(root, ".harness", "team-config.yaml")
    t_yaml = os.path.join(tdir, "team-config.yaml")
    if not os.path.isfile(p_yaml):
        print(f"team-config.yaml: MISSING at {p_yaml} — domain enforcement is off "
              f"(check-domain.sh fails open without a manifest). Run /harness-init.")
        gaps.append("team-config.yaml")
    else:
        pt, tt = open(p_yaml, encoding="utf-8").read(), open(t_yaml, encoding="utf-8").read()
        pver, tver = yaml_version(pt), yaml_version(tt)
        pnames, tnames = set(yaml_names(pt)), yaml_names(tt)
        new_agents = [n for n in tnames if n.startswith("harness-") and n not in pnames]
        if pver != tver or new_agents:
            gaps.append("team-config.yaml")
            print(f"team-config.yaml: schema_version {pver} -> {tver} "
                  f"— NOT rewritten (see the header of this script for why).")
            for n in new_agents:
                print(f"  + new agent `{n}` — copy its block from {os.path.relpath(t_yaml, root)}")
            print("  Add the entries above by hand, then set schema_version to "
                  f"{tver}. Do NOT copy the template over your file: your `domain` "
                  "globs are per-project and the template's are placeholders.")
        else:
            print(f"team-config.yaml: up to date (schema_version {pver}).")

    if check_only:
        return 1 if gaps else 0

    # A YAML gap survives an apply — this script deliberately does not rewrite the
    # manifest. Exiting 0 here would report "upgraded" while domain enforcement is
    # still running on the old roster, so the unresolved half exits non-zero even
    # though the JSON half succeeded.
    if "team-config.yaml" in gaps:
        print("\nMANUAL STEP REQUIRED — team-config.yaml was NOT changed. "
              "Until the entries above are added by hand, any new agent has no "
              "declared domain and check-domain.sh will block all of its writes.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
