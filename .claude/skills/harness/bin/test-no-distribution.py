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
    # Four doors, not six: /harness-map and /harness-deepen were deleted when the
    # codebase map tier was retired (DEC-149 records the removal). The guard is that a
    # distribution sweep does not take the REMAINING doors with it.
    check("case1_presence_four_other_command_doors_survive", len(other_cmds) >= 4,
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
EXCLUDED_EXACT = {".harness/harness/docs/DECISIONS.md"}
EXCLUDED_PREFIXES = (".harness/logs/", ".harness/notes/", ".harness/harness/features/")

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
    # THIS IS THE WRITE-SURFACE TRIPWIRE, and it is an EXACT SET rather than a count. A fleet
    # member is a repository the factory may write to, so every addition must be a decision that
    # fails a test until someone records it here. `len(repos) == 1` was the earlier form and it
    # was strictly weaker: it could not tell an addition from a SUBSTITUTION, so swapping a
    # member for a different repository passed. Naming the set catches both.
    #
    # `harness-factory-smoke` earns its place as a KEPT FIXTURE (FEAT-33 SC-01, 2026-08-23), not
    # as a served product. `provision --repo` resolves a declaration through this file, and
    # `mruangutai/harness` is deliberately absent from it (DEC-174), so a live run of the
    # board-create path had nowhere else to point. That path cannot be reached by any runner —
    # its create branch fires only when the declared project number does not exist, and no fake
    # can prove GitHub accepts the mutation. The live run immediately found a defect eleven fakes
    # had hidden: a fresh Projects v2 board already carries a `Status` field.
    expected_repos = {"mruangutai/kaya-ai", "mruangutai/harness-factory-smoke"}
    found_repos = {r.get("name") for r in repos if isinstance(r, dict)}
    # CARDINALITY IS ASSERTED SEPARATELY, and the set comparison alone is NOT enough. A set
    # loses duplicates: two `- name: mruangutai/kaya-ai` entries carrying DIFFERENT
    # `default_branch` values satisfy `found_repos == expected_repos` and satisfy `load_fleet`,
    # and `repo_entry`'s first-match-wins then hands `factory_workspace` a branch nobody chose.
    # The earlier `len(repos) == 1` form caught that case and the set form does not, so this
    # assertion is only strictly stronger than the count with the length check beside it.
    check("case3_presence_fleet_is_exactly_the_declared_set",
          found_repos == expected_repos and len(repos) == len(expected_repos),
          f"expected {sorted(expected_repos)} ({len(expected_repos)} entries), found "
          f"{sorted(n for n in found_repos if n)} in {len(repos)} entries")

    # DEC-174 (amended): harness is not a fleet member. The convention that harness
    # develops itself in the live checkout and in worktrees — never in a factory
    # workspace clone — is enforced by ABSENCE from this list, not by prose. Assert the
    # absence, so re-adding the entry fails a test instead of passing silently.
    check("case3_absence_harness_is_not_a_fleet_member",
          not any(isinstance(r, dict) and r.get("name") == "mruangutai/harness"
                  for r in repos),
          f"repos: {repos}")

    kaya = next((r for r in repos if isinstance(r, dict) and r.get("name") == "mruangutai/kaya-ai"), None)
    check("case3_presence_kaya_default_branch_is_master",
          bool(kaya) and kaya.get("default_branch") == "master",
          f"kaya-ai entry: {kaya}")

    # FEAT-24: THE BOARD LEFT THIS FILE. `fleet.yaml` declares which repositories the factory
    # serves and nothing about how their cards move; each repository's board lives in its own
    # `.harness/harness.json`. `load_fleet` REJECTS a board here, so a re-added one closes
    # every write outside the harness root through resolve_fleet — assert the absence, at both
    # levels, so it fails a test instead of a whole session.
    check("case3_absence_no_board_in_fleet",
          "board" not in data
          and not any(isinstance(r, dict) and "board" in r for r in repos),
          f"top-level board: {data.get('board')!r}; repos carrying one: "
          f"{[r.get('name') for r in repos if isinstance(r, dict) and 'board' in r]}")

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
    dec_path = os.path.join(ROOT, ".harness", "harness", "docs", "DECISIONS.md")
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

    # The sweep covers BOTH the moved harness docs and the surviving global docs/
    # (PRINCIPLES.md stays there by map ruling) — the control below proves the
    # authority file was actually visited.
    docs_dirs = [os.path.join(ROOT, ".harness", "harness", "docs"),
                 os.path.join(ROOT, "docs")]
    ref_hits = []
    saw_decisions = False
    for _dd in docs_dirs:
        for dirpath, _dirnames, filenames in os.walk(_dd):
            for fn in filenames:
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, ROOT)
                if rel.endswith("DECISIONS.md"):
                    saw_decisions = True
                try:
                    with open(full, "r", encoding="utf-8", errors="ignore") as fh:
                        text = fh.read()
                except OSError:
                    continue
                if DEC12_REF_RE.search(text):
                    ref_hits.append(rel)
    check("case4_absence_no_dec12_references_under_docs", ref_hits == [],
          f"found in: {ref_hits}")
    # POSITIVE CONTROL (FEAT-22 T-04): the walk above proves an ABSENCE, and an
    # absence over a mis-pointed or empty directory is vacuously true — the docs
    # moved once already and could move again. Assert the walk actually visited the
    # authority file, so a silent re-point reds here instead of greening everything.
    check("case4_control_docs_walk_reached_decisions",
          saw_decisions, "the walk never visited DECISIONS.md")

    index_path = os.path.join(ROOT, ".harness", "harness", "docs", "DECISIONS-INDEX.md")
    with open(index_path, "r", encoding="utf-8") as fh:
        index_text = fh.read()
    dec113_rows = INDEX_DEC113_ROW_RE.findall(index_text)
    dec12_rows = INDEX_DEC12_ROW_RE.findall(index_text)
    check("case4_presence_exactly_one_dec113_index_row", len(dec113_rows) == 1,
          f"found {len(dec113_rows)} rows beginning '- DEC-113 '")
    check("case4_absence_no_dec12_index_row", len(dec12_rows) == 0,
          f"found {len(dec12_rows)} rows beginning '- DEC-12 '")


# ============================== Case 5 ==============================
# the repository-to-board pairing declared in the live fleet is pinned.

def case5():
    fleet_path = os.path.join(ROOT, ".harness", "factory", "fleet.yaml")
    import yaml
    with open(fleet_path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    check("board_lives_per_repo_not_fleet_level",
          "board" not in data,
          f"top-level 'board' key still present in fleet.yaml: {data.get('board')}")

    # THE PER-REPOSITORY BOARD ASSERTIONS MOVED OUT OF THIS FILE (FEAT-24). They asserted
    # that every repos entry declares a board and that kaya-ai is paired with board 2 — both
    # true of the fleet-level shape this feature removed, and both now unassertable here
    # because the board is not in this file. The absence is asserted as
    # `case3_absence_no_board_in_fleet`; the pairing is asserted where it now lives, in
    # kaya-ai's own `.harness/harness.json` on `master`, by T-07's verify over `gh api`.


# ============================== Case 6 ==============================
# FEAT-42 T-07 — ONE root resolver, and the retired environment chain occurs NOWHERE.
#
# THE ABSENCE HALF SCANS EVERY TRACKED SOURCE FILE IN THE REPOSITORY, not one directory, and
# it is derived from `git ls-files` rather than a fixed list ON PURPOSE. A fixed list proves
# that the sites someone remembered were fixed and says nothing about the seventh. The site
# that decided this scope was `.omp/extensions/harness-hooks.ts` — outside
# `.claude/skills/harness/bin/` entirely, and invisible to any directory-scoped sweep.
#
# FOUR EXCLUSIONS, AND A READER WILL WIDEN THEM UNLESS THE REASONS ARE HERE.
#   test-* files SET the variable. It is the test-injection seam, assigned repo-wide in
#     exactly one place — test-gh-close-gate.py:41 — and read by the fixtures. Removing the
#     seam would leave the gates untestable against anything but the live checkout.
#   harness_boundary.py is the ONE module allowed to read it, because it is the resolver.
#     That is the whole point of the invariant, not an exception to it.
#   *.md files are prose. Notes, decisions and observations discuss the variable by name and
#     always will; a record that stays true as written is not a site.
#   The record tree — .harness/logs/, .harness/notes/, .harness/harness/features/ — is that
#     same prose rule at a wider extension, and it arrives at the identical three prefixes
#     EXCLUDED_PREFIXES already holds under "Historical records that stay true as written".
#     This feature's own plan.yaml names the variable dozens of times and a ship-review page
#     twice, because their job is describing its removal; committing them would move the
#     count from 21 to 72 and it could never return to zero. Operator ruling, 2026-08-27.
#
# EXCLUDED_PREFIXES IS REUSED, is_excluded_from_scan IS NOT. That helper also consults
# EXCLUDED_EXACT, which exempts DECISIONS.md alone among markdown — every other tracked *.md
# would then count, inflating the total past the 21 baseline this case was written against.
#
# THE PRESENCE HALF IS WHAT STOPS THE ABSENCE HALF PASSING VACUOUSLY. A grep that finds
# nothing because the resolver was deleted looks identical to one that finds nothing because
# every caller was migrated.
CHAIN_NAME = "HARNESS" + "_PROJECT_DIR"      # assembled so this line is not itself a site

RESOLVER_REL = ".claude/skills/harness/bin/harness_boundary.py"

# Names this feature DELETED. Each was a second implementation of the one rule.
DELETED_NAMES = ("harness_root", "_repo_root_from_script", "_root_from", "_resolve_repo_root")


def case6():
    tracked = git_ls_files()
    scanned = [
        f for f in tracked
        if not os.path.basename(f).startswith("test-")
        and os.path.basename(f) != "harness_boundary.py"
        and not f.endswith(".md")
        and not f.startswith(EXCLUDED_PREFIXES)
    ]
    offenders = []
    for rel in scanned:
        text = read_text(rel)
        if text is None:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if CHAIN_NAME in line:
                offenders.append(f"{rel}:{n}: {line.strip()[:100]}")
    check("case6_absence_the_env_chain_occurs_nowhere", not offenders,
          "%d occurrence(s) of the retired chain survive:\n  %s"
          % (len(offenders), "\n  ".join(offenders[:20])))

    # --- the presence half ---
    resolver = read_text(RESOLVER_REL) or ""
    missing = [n for n in ("MARKER", "def resolve_root(", "def root_above(",
                           "def root_from_script(") if n not in resolver]
    check("case6_presence_the_resolver_defines_all_four", not missing,
          f"{RESOLVER_REL} is missing: {missing}")

    importers = {rel for rel in tracked
                 if "import harness_boundary" in (read_text(rel) or "")}
    check("case6_presence_sixteen_files_reach_the_resolver", len(importers) >= 16,
          f"only {len(importers)} tracked file(s) import harness_boundary: "
          f"{sorted(importers)[:20]}")

    # --- the deleted names, and the two survivors that are NOT them ---
    # SAME test-* EXCLUSION AS THE ABSENCE HALF ABOVE, and for the same reason: those files
    # discuss the deleted names in prose — test-post-merge-sweep.py's docstring records the
    # measured defect _resolve_repo_root was written to fix, and stays true as written — and
    # this file names all four in DELETED_NAMES, so without the exclusion it fails itself.
    bin_rel = ".claude/skills/harness/bin/"
    bin_files = [f for f in tracked
                 if f.startswith(bin_rel) and not os.path.basename(f).startswith("test-")]
    for name in DELETED_NAMES:
        hits = []
        for rel in bin_files:
            for n, line in enumerate((read_text(rel) or "").splitlines(), 1):
                if re.search(r"\b%s\b" % re.escape(name), line):
                    hits.append(f"{rel}:{n}")
        check(f"case6_absence_{name.strip('_')}_is_gone", not hits,
              f"{name} survives at: {hits[:8]}")

    wayfind = read_text(bin_rel + "wayfind.py") or ""
    check("case6_absence_wayfind_defines_no_root_of_its_own",
          not re.search(r"^def root\(", wayfind, re.M),
          "wayfind.py still defines a module-level root()")

    # THE TWO SURVIVORS. Both answer a DIFFERENT question from resolve_root, and a sweep that
    # took them with it would be over-broad rather than complete.
    check("case6_presence_worktree_owner_survives",
          "def worktree_owner(" in resolver,
          "harness_boundary.worktree_owner is gone — it answers which checkout owns a PATH")
    sweep = read_text(bin_rel + "post-merge-sweep.sh") or ""
    check("case6_presence_main_checkout_resolver_survives",
          "_resolve_main_checkout_root" in sweep,
          "post-merge-sweep._resolve_main_checkout_root is gone — it asks git which linked "
          "worktree is main, which is not this question")


# ============================== Case 7 ==============================
# THE INVOKING DIRECTORY IS NOT ON THE IMPORT PATH.

def case7():
    """Every gate that launches Python excludes the governed cwd (#556).

    Python puts the invoking directory at sys.path[0] AHEAD of PYTHONPATH. A policy module
    in the governed agent cwd could therefore replace the real module. Interpreter `-I`
    is used where only stdlib/project modules are needed. Heredocs that need normal
    site-packages start with a bootstrap that removes only sys.path[0], then executes stdin.
    Both forms exclude the cwd and work on the macOS system Python 3.9 used by OMP.

    This case is the invariant, not the two pairs in test-check-domain.py and
    test-bash-write-guard.py: those prove two hooks are shut; this catches the next
    gate script added without either safe-path form.
    """
    pat = re.compile(r"(?<!`)python3 (?!-I )(-c |- )(?=[\'\"$]|<<)")
    scripts = [f for f in git_ls_files()
               if f.startswith(".claude/skills/harness/bin/") and f.endswith(".sh")]
    check("case7_scripts_found", len(scripts) >= 9,
          f"only {len(scripts)} gate scripts scanned — the glob stopped matching")
    naked = []
    for rel in scripts:
        for i, line in enumerate(read_text(rel).splitlines(), 1):
            if pat.search(line) and "sys.path.pop(0)" not in line:
                naked.append(f"{rel}:{i}")
    check("case7_every_python_launch_isolates_the_cwd", not naked,
          f"python3 launched without -I or safe-path bootstrap, so the cwd shadows imports: {naked}")

    # THE PAIRED HALF. Without it the case above is satisfied by a regex that matches
    # nothing at all — a typo in the pattern would read as a clean tree.
    guarded = re.compile(r"python3 -I (-c |- )")
    hits = sum(1 for rel in scripts for line in read_text(rel).splitlines()
               if guarded.search(line))
    safe_hits = sum(1 for rel in scripts for line in read_text(rel).splitlines()
                    if "python3 -c" in line and "sys.path.pop(0)" in line)
    check("case7_the_scan_can_see_the_invocations", hits >= 16 and safe_hits >= 3,
          f"found {hits} isolated launches and {safe_hits} safe-python launches")


def main():
    case1()
    case2()
    case3()
    case4()
    case5()
    case6()
    case7()

    if failures:
        print(f"\n{len(failures)} FAILURE(S): {failures}")
        return 1
    print("\nALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
