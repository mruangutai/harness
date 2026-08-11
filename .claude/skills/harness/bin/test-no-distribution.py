#!/usr/bin/env python3
"""Tests that the distribution mechanism (deploy.sh, /harness-deploy, the deploy registry) is
gone from the tree, and that removing it did not take anything load-bearing with it.

WHY paired assertions: DEC-169 — an absence check alone proves only that the wrong words are
gone; a grep that was going to pass anyway proves nothing. Every case here pairs an ABSENCE
assertion with a PRESENCE assertion for that reason.

Root is resolved from this file's own location, never from the cwd (matches its siblings, e.g.
test-check-plan-routes.py's BIN_DIR/REPO_ROOT derivation).
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name} {detail}")
        failures.append(name)


def git_ls_files():
    """Tracked files only, resolved via -C ROOT so cwd never matters (see module docstring).

    NOTE (T-13 receipt): this is a deliberate scope limit, not an oversight. A scan widened to
    --others --exclude-standard would pick up whatever untracked junk the working tree happens to
    carry and make the gate non-deterministic. It also means THIS file is invisible to its own
    scan until it is committed — see the first ALLOW_LIST entry below.
    """
    r = subprocess.run(
        ["git", "-C", ROOT, "ls-files"],
        capture_output=True, text=True, check=True,
    )
    return [line for line in r.stdout.splitlines() if line]


def read_text(rel_path):
    full = os.path.join(ROOT, rel_path)
    try:
        with open(full, "r", encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except OSError:
        return None


# ============================== Case 1 ==============================
# the mechanism is gone and the tree is otherwise intact.

def case1():
    tracked = git_ls_files()

    deploy_sh_hits = [f for f in tracked if os.path.basename(f) == "deploy.sh"]
    check("case1_absence_no_deploy_sh_tracked_anywhere", deploy_sh_hits == [],
          f"deploy.sh still tracked at: {deploy_sh_hits}")

    check("case1_absence_no_harness_deploy_command",
          not os.path.exists(os.path.join(ROOT, ".claude", "commands", "harness-deploy.md")),
          ".claude/commands/harness-deploy.md still exists")

    cmd_dir = os.path.join(ROOT, ".claude", "commands")
    other_cmds = [f for f in os.listdir(cmd_dir) if f.startswith("harness") and f.endswith(".md")]
    check("case1_presence_six_other_command_doors_survive", len(other_cmds) >= 6,
          f"only {len(other_cmds)} harness*.md commands remain: {other_cmds}")

    bin_dir = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
    check("case1_presence_check_plan_routes_survives",
          os.path.exists(os.path.join(bin_dir, "check-plan-routes.py")),
          "check-plan-routes.py is missing")
    check("case1_presence_factory_workspace_survives",
          os.path.exists(os.path.join(bin_dir, "factory_workspace.py")),
          "factory_workspace.py is missing")


# ============================== Case 2 ==============================
# the token sweep, deliberately wider than the survey that produced this plan.

TOKEN_RE = re.compile(r"harness-deploy|deploy\.sh|harness-registry|registry\.json")

# Historical records that stay true as written — excluded from the sweep, and nothing else.
EXCLUDED_EXACT = {"docs/harness/DECISIONS.md"}
EXCLUDED_PREFIXES = (".harness/logs/", ".harness/notes/", ".harness/features/")

# EXACTLY TWO ENTRIES. Declared here, never derived from what happens to be present, so a new
# unswept site fails rather than being silently absorbed. Path-scoped: an entry exempts its path
# from ALL four tokens, not just the one that motivated it.
ALLOW_LIST = [
    # this file necessarily contains all four tokens above, in its own pattern and this list;
    # inert on a run where it is untracked (git ls-files does not see it), load-bearing once committed.
    ".claude/skills/harness/bin/test-no-distribution.py",
    # case 20's $HOME-shaped trap builds its OWN synthetic registry.json inside a temp dir (SC-02);
    # that fixture is legitimate and must not be swept away to satisfy this check.
    ".claude/skills/harness/bin/test-check-plan-routes.py",
]


def is_excluded_from_scan(rel_path):
    if rel_path in EXCLUDED_EXACT:
        return True
    return any(rel_path.startswith(p) for p in EXCLUDED_PREFIXES)


def case2():
    tracked = git_ls_files()
    scanned = [f for f in tracked if not is_excluded_from_scan(f)]

    violations = []
    reached_fleet_yaml = False
    for rel in scanned:
        text = read_text(rel)
        if text is None:
            continue
        if "fleet.yaml" in text:
            reached_fleet_yaml = True
        if rel in ALLOW_LIST:
            continue
        if TOKEN_RE.search(text):
            violations.append(rel)

    check("case2_absence_no_unswept_distribution_tokens", violations == [],
          f"unswept token(s) found in: {violations}")
    check("case2_presence_scan_reached_the_tree", reached_fleet_yaml,
          "no scanned file matched fleet\\.yaml — the scan set may be empty, "
          "which would make the absence half pass vacuously")


# ============================== Case 3 ==============================
# the fleet declaration is the reachability record.

def case3():
    fleet_path = os.path.join(ROOT, ".harness", "factory", "fleet.yaml")
    data = None
    loaded_ok = False
    try:
        import yaml
        with open(fleet_path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        loaded_ok = True
    except Exception as e:  # noqa: BLE001 - reported via check(), not raised
        check("case3_presence_fleet_yaml_safe_loads", False, f"{fleet_path} failed to parse: {e}")
    else:
        check("case3_presence_fleet_yaml_safe_loads", True)

    repos = (data or {}).get("repos", []) if loaded_ok else []
    check("case3_presence_fleet_has_exactly_two_repos", len(repos) == 2,
          f"repos: {repos}")

    kaya = next((r for r in repos if isinstance(r, dict) and r.get("name") == "mruangutai/kaya-ai"), None)
    check("case3_presence_kaya_default_branch_is_master",
          bool(kaya) and kaya.get("default_branch") == "master",
          f"kaya-ai entry: {kaya}")

    registry_hits = []
    harness_dir = os.path.join(ROOT, ".harness")
    for dirpath, _dirnames, filenames in os.walk(harness_dir):
        if "registry.json" in filenames:
            registry_hits.append(os.path.relpath(os.path.join(dirpath, "registry.json"), ROOT))
    check("case3_absence_no_registry_json_under_harness", registry_hits == [],
          f"found: {registry_hits}")


# ============================== Case 4 ==============================
# the falsified decisions are struck, and the strike did not overreach.

DEC12_HEADING_RE = re.compile(r"^## DEC-12 ", re.M)
DEC113_HEADING_RE = re.compile(r"^## DEC-113 ", re.M)
NEXT_SECTION_RE = re.compile(r"^## DEC-|^---", re.M)
STALE_MARKER = "<!-- stale:"
DEC12_REF_RE = re.compile(r"DEC-12(?:[^0-9]|$)", re.M)
INDEX_DEC113_ROW_RE = re.compile(r"^- DEC-113 ", re.M)
INDEX_DEC12_ROW_RE = re.compile(r"^- DEC-12 ", re.M)

# The substring asserted inside DEC-113's sliced section (see slice_section below). Chosen per
# the operator ruling: it must be INSIDE the slice and must cover the PRECEDENCE half of the
# surviving rule, not merely its location (a location-only pin like `paths.crew_overrides` is
# too coarse). Present verbatim on the line "resolves it first." within DEC-113's section.
DEC113_PRECEDENCE_SUBSTRING = "resolves it first"


def slice_section(text, heading_re):
    """Return the text from `heading_re`'s match up to (not including) the next `## DEC-` or
    `---` line, whichever comes first. None if the heading is not found."""
    m = heading_re.search(text)
    if not m:
        return None
    rest = text[m.end():]
    nxt = NEXT_SECTION_RE.search(rest)
    end = m.end() + (nxt.start() if nxt else len(rest))
    return text[m.start():end]


def case4():
    dec_path = os.path.join(ROOT, "docs", "harness", "DECISIONS.md")
    with open(dec_path, "r", encoding="utf-8") as fh:
        dec_text = fh.read()

    check("case4_absence_no_dec12_heading", DEC12_HEADING_RE.search(dec_text) is None,
          "a '## DEC-12 ' heading is still present")
    check("case4_absence_no_stale_marker_reintroduced", STALE_MARKER not in dec_text,
          "'<!-- stale:' marker mechanism (removed under #202/DEC-188) is back")

    heading_count = len(DEC113_HEADING_RE.findall(dec_text))
    check("case4_presence_exactly_one_dec113_heading", heading_count == 1,
          f"found {heading_count} '## DEC-113 ' headings")

    dec113_slice = slice_section(dec_text, DEC113_HEADING_RE)
    check("case4_presence_dec113_precedence_rule_survives",
          dec113_slice is not None and DEC113_PRECEDENCE_SUBSTRING in dec113_slice,
          f"substring {DEC113_PRECEDENCE_SUBSTRING!r} not found within DEC-113's sliced section")

    docs_dir = os.path.join(ROOT, "docs")
    ref_hits = []
    for dirpath, _dirnames, filenames in os.walk(docs_dir):
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, ROOT)
            try:
                with open(full, "r", encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()
            except OSError:
                continue
            if DEC12_REF_RE.search(text):
                ref_hits.append(rel)
    check("case4_absence_no_dec12_references_under_docs", ref_hits == [],
          f"found in: {ref_hits}")

    index_path = os.path.join(ROOT, "docs", "harness", "DECISIONS-INDEX.md")
    with open(index_path, "r", encoding="utf-8") as fh:
        index_text = fh.read()
    dec113_rows = INDEX_DEC113_ROW_RE.findall(index_text)
    dec12_rows = INDEX_DEC12_ROW_RE.findall(index_text)
    check("case4_presence_exactly_one_dec113_index_row", len(dec113_rows) == 1,
          f"found {len(dec113_rows)} rows beginning '- DEC-113 '")
    check("case4_absence_no_dec12_index_row", len(dec12_rows) == 0,
          f"found {len(dec12_rows)} rows beginning '- DEC-12 '")


def main():
    case1()
    case2()
    case3()
    case4()

    if failures:
        print(f"\n{len(failures)} FAILURE(S): {failures}")
        return 1
    print("\nALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
