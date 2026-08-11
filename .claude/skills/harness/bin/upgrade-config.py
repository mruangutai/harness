#!/usr/bin/env python3
"""`/harness-init --upgrade`: merge newer template entries without clobbering the project.

  upgrade-config.py <project-root> [--check] [--templates <dir>]

  (default)  merge harness.json and REPORT on team-config.yaml. Idempotent.
  --check    report the schema_version gap and what would change. Writes nothing.

THE ASYMMETRY IS DELIBERATE:

  harness.json    is JSON -> merged deterministically, here.
  team-config.yaml is YAML -> REPORTED ONLY, never rewritten.

The asymmetry SURVIVES DEC-171, but the reason changed. PyYAML is now required, so
READING the manifest is a real parse (T-04) rather than a line scan. WRITING it is
still refused, for a reason a parser does not fix: `yaml.safe_dump` does not preserve
comments, and `team-config.yaml` is more comment than data — every `domain` glob is
justified in prose beside it. Round-tripping the manifest through a parser would
silently delete the reasoning that makes the harness's only write-scope guarantee
auditable. So this still prints the specific new entries and the user adds them; a
manual step is an acceptable price for not stripping the file's explanations.

THE PROJECT ALWAYS WINS on a value it already has. `test_kinds.*.cmd` above all:
those are commands dev-ops verified by running, and re-imposing the template's
`null` would turn a working gate back into a soft skip. New template keys are
added; existing project keys are left exactly as they are.

Exit 0 = up to date, or merged. Exit 1 = --check found a gap, or an error.
"""
import json
import os
import shutil
import sys

# F-03: this import was MISSING while `harness_yaml.load_str` was called at :99 and
# :124, so every invocation died with NameError. It shipped because T-04's verify had
# two halves and only one existed: the surviving half greps for ABSENCE OF REGEX, which
# deleting the regexes satisfies exactly — with or without a working parser.
#
# This file runs as a script, so its own directory is already sys.path[0]; no
# PYTHONPATH is needed, unlike the hooks' heredocs.
import harness_yaml

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
    """Every `name:` value in a manifest, at ANY nesting depth (T-04).

    Was a line scan, on the stated grounds that "no YAML library exists here".
    DEC-171 reversed that, and the scan had two defects a real parse removes:

    - `^\\s*-?\\s*(?:name|- name):` matched the LITERAL TEXT `name:` anywhere at any
      indent, so a `name:` nested under some unrelated key counted as an agent, and a
      quoted value containing `name:` could too.
    - It could not distinguish a real entry from one inside a comment or a folded
      block scalar — the same class of bug that made `team-config.yaml` unparseable
      while six line scanners read it happily.

    Still read-only: a miss under-reports a new agent rather than corrupting anything.
    """
    doc = harness_yaml.load_str(text, "<manifest>")
    out = []

    def walk(node):
        if isinstance(node, dict):
            n = node.get("name")
            # Q2: this DROPPED a non-str name (`if isinstance(n, str)`), which reads as
            # a type guard but is a silent filter — and it contradicts D-08, whose rule
            # is coerce-at-the-consumer for anything used as an identifier. A name is an
            # identifier. YAML 1.1 resolves an unquoted `no:`/`on:`/`01` to a bool or
            # int, so `- name: no` vanished from the roster rather than being reported.
            #
            # Fixing F-03 made this REACHABLE for the first time, which is why the panel
            # raised it from low to med: before the import landed, nothing here ran at
            # all. bool is excluded from the numeric case for the usual reason — it is
            # an int subclass.
            if n is not None and not isinstance(n, (dict, list)):
                s = str(n).strip()
                if s:
                    out.append(s)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(doc)
    return out


def yaml_version(text):
    """`schema_version` as an int, or None.

    safe_load returns it TYPED, so this no longer needs `int(m.group(1))` — but it
    must still tolerate a project that wrote it as a quoted string, which the old
    `(\\d+)` regex silently rejected (it required bare digits, so `schema_version: "2"`
    read as absent and the upgrade path reported no gap at all)."""
    doc = harness_yaml.load_str(text, "<manifest>")
    v = doc.get("schema_version") if isinstance(doc, dict) else None
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, int):
        return v
    s = str(v).strip()
    return int(s) if s.isdigit() else None


def main():
    # Review finding 1: the module's documented gate had ZERO production callers,
    # so a missing PyYAML surfaced as a raw traceback instead of INSTALL_COMMAND.
    # First statement, before any parse can be attempted.
    harness_yaml.require_or_die()
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
        print(f"upgrade-config: no templates at {tdir} — the templates ship inside "
              f"this repository at .claude/skills/harness/bin/../templates, so a "
              f"missing templates directory means the checkout is incomplete.")
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
        # A manifest that does not parse is REPORTED, not raised. Found by this task's
        # own test: the raw YamlParseError escaped as a traceback, which tells the user
        # "the upgrade tool is broken" when the truth is "your manifest is". The gap is
        # what SC-07's init gate exists to catch early — say so, and name the line.
        # The PROJECT's file and the SHIPPED TEMPLATE are parsed separately (review
        # finding 4). Both used to sit in one try whose handler said "fix the file
        # first" — so a malformed shipped template sent the user off to edit a file of
        # theirs that was perfectly fine. Two files, two different people's problem.
        pver = tver = None
        pnames, tnames = set(), []
        try:
            pver, pnames = yaml_version(pt), set(yaml_names(pt))
        except harness_yaml.YamlParseError as e:
            print(f"team-config.yaml: DOES NOT PARSE — {e}")
            print("  The upgrade cannot compare a manifest it cannot read. Fix the file "
                  "first; `check-domain.sh` is failing closed on it too (DEC-171 am.1).")
            gaps.append("team-config.yaml")
        try:
            tver, tnames = yaml_version(tt), yaml_names(tt)
        except harness_yaml.YamlParseError as e:
            print(f"THE SHIPPED TEMPLATE at {t_yaml} does not parse — {e}")
            print("  This is a harness bug, NOT your project. Your team-config.yaml is "
                  "not the problem and editing it will not help. The remedy is a "
                  "complete checkout of this repository, not a distribution step; "
                  "report it if that does not fix it.")
            gaps.append("team-config.yaml")
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
