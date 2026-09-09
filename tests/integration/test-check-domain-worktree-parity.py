#!/usr/bin/env python3
"""check-domain.sh: grant parity between a worktree and its owning checkout.

Slice of the former test-check-domain.py (issue #1527). Its own file because this
one block is the family's longest serial run: 49 cases, each a hook subprocess.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_tests)
import os, shutil, subprocess, sys, tempfile
from check_domain_support import (HOOK, ROOT, _env, drive, fixture, make_linked_worktree)


WTG = []


def wtg(name, ok, detail=""):
    WTG.append((name, ok, detail))


def run_worktree_grant_parity():
    """T-03 (FEAT-30, SC-05) — the grant an agent has inside a worktree is the grant it
    has at the checkout root, for ALL SIXTEEN agents, one assertion each.

    THIS PINS TODAY'S LAYOUT ON PURPOSE: exactly one segment after WORKTREES_SEGMENT.
    T-04 replaces the fixed-segment strip with a mechanism that reads the git pointer,
    and these sixteen cases are the baseline it must leave green. Do NOT extend this to
    the repo-and-id layout here — T-04 owns that.

    THE ROSTER IS WALKED, NOT LISTED. Every node carrying both a `name` and a
    list-valued `domain`, at every nesting level: members inside each team's `members`,
    leads under `leads`, and harness-orchestrator as a bare top-level key. The length is
    asserted to be exactly 16 and reports the names it found when it is not — a roster
    that silently shrinks would make every following assertion vacuous rather than red.

    TWO DEVIATIONS FROM THE SIGNED INTENT, both forced by measurement, both disclosed
    rather than smoothed over:

    1. The intent says instantiate by "replacing each single-star segment" with a token.
       Replacing the whole SEGMENT destroys literal prefixes — the reviewers' grant
       `notes/review-harness-code-reviewer-*.md` becomes `notes/zz`, which their own
       glob cannot match. Measured: 7 of 16 agents resolved to harness-orchestrator
       instead of themselves. The star is replaced WITHIN its segment, keeping literals.

    2. The intent says take "the first entry of its own domain list". In the harness base
       a glob match is accepted only when the TARGET passes is_control_plane_target, so
       an agent whose first entry is product code — `src/**`, `docs/**`, `web/src/**`,
       `supabase/migrations/**` — resolves to NOBODY at BOTH paths. `tests/**` is now a
       target-side control-plane entry, so harness-qa's first domain entry is selected
       rather than falling through. For agents without such an entry, the first entry
       that is a control-plane target is used instead, and an agent with none at all is
       a reported FAILURE, never a skip.

    The membership assertion is not decoration. Equality alone is satisfied by two empty
    sets, so each case also asserts the agent is IN both sets. T-03's verify mutates
    WORKTREES_SEGMENT by name in a copied module and requires this file to FAIL, which is
    only reachable if the in-worktree half of every pair really traverses the worktree
    path.
    """
    import harness_yaml as _hy
    import harness_boundary as _hb

    fails = 0
    tmp = tempfile.mkdtemp()

    manifest_src = os.path.join(ROOT, ".harness", "team-config.yaml")
    with open(manifest_src, encoding="utf-8") as f:
        manifest_text = f.read()

    # THE REAL MANIFEST, not FIXTURE_MANIFEST. The roster and the grants under test are
    # the shipped ones; a fixture manifest would assert parity for personas that do not
    # exist and would never notice a real grant losing its worktree parity.
    root = fixture(manifest_text)

    # A REAL LINKED WORKTREE, both sides of the pointer pair, per D-09. A bare directory
    # made with os.makedirs resolves identically under today's fixed-segment strip, so
    # these cases would pass now and go red the moment T-04 lands — sixteen false
    # failures attributed to T-04 instead of to the fixture.
    wt_id = "wt1"
    owner_entry = os.path.join(root, ".git", "worktrees", wt_id)
    os.makedirs(owner_entry)
    os.makedirs(os.path.join(root, ".git", "refs"), exist_ok=True)
    wt_path = os.path.join(root, ".claude", "worktrees", wt_id)
    os.makedirs(wt_path)
    # the worktree side
    with open(os.path.join(wt_path, ".git"), "w") as f:
        f.write("gitdir: %s\n" % owner_entry)
    # the owner side, naming the worktree's own .git file
    with open(os.path.join(owner_entry, "gitdir"), "w") as f:
        f.write("%s\n" % os.path.join(wt_path, ".git"))
    # NO .harness/team-config.yaml inside wt1, deliberately: these cases root the session
    # at the fixture root, and a nearer manifest would move the base out from under the
    # assertion.

    # THE OWNER MUST BE A REAL CHECKOUT for worktree_owner to name it: it walks up to the
    # first `.git` entry, and a DIRECTORY is what makes a root the owner.
    parsed = _hb.worktree_owner(wt_path)
    wtg("the fixture worktree is a REAL linked worktree, parsed and legitimate",
        parsed is not None and parsed[1] is not None and parsed[2] is True,
        f"worktree_owner({wt_path}) = {parsed!r} — a bare directory or an unparsed "
        f"pointer here makes all sixteen cases below prove nothing")

    def instantiate(pat):
        """A glob to a concrete relative path, replacing the star INSIDE its segment."""
        out = []
        for seg in pat.strip("/").split("/"):
            out.append("zz/zz" if seg == "**" else seg.replace("*", "zz"))
        return "/".join(out)

    roster = []

    def walk(node):
        if isinstance(node, dict):
            nm, dom = node.get("name"), node.get("domain")
            if isinstance(nm, str) and isinstance(dom, list):
                roster.append((nm, dom))
            for k, v in node.items():
                if k not in ("name", "domain"):
                    walk(v)
        elif isinstance(node, list):
            for x in node:
                walk(x)

    walk(_hy.yaml.safe_load(manifest_text))
    names = sorted(n for n, _ in roster)
    wtg("the roster walk finds exactly 16 agents carrying a name and a list domain",
        len(roster) == 16,
        f"found {len(roster)}: {names!r} — every case below is vacuous if this is wrong")

    def resolve(path):
        r = subprocess.run([HOOK, "--resolve", path], capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, timeout=20,
                           env=_env(root))
        return set(r.stdout.split())

    unit_path = os.path.join(root, "tests", "unit", "test-zz.py")
    integration_path = os.path.join(root, "tests", "integration", "test-zz.py")
    unit_grants = resolve(unit_path)
    integration_grants = resolve(integration_path)
    expected_test_writers = {
        "harness-qa", "harness-backend-dev", "harness-dev-ops"}
    for agent in sorted(expected_test_writers):
        wtg(f"tests/unit grants {agent}", agent in unit_grants,
            f"resolved {sorted(unit_grants)!r}")
        wtg(f"tests/integration grants {agent}", agent in integration_grants,
            f"resolved {sorted(integration_grants)!r}")
    for agent in ("harness-frontend-dev", "harness-ai-dev", "harness-data-engineer"):
        wtg(f"tests/unit denies {agent}", agent not in unit_grants,
            f"resolved {sorted(unit_grants)!r}")
    bin_grants = resolve(os.path.join(
        root, ".claude", "skills", "harness", "bin", "zz.sh"))
    wtg("harness-qa cannot write governed bin shell",
        "harness-qa" not in bin_grants, f"resolved {sorted(bin_grants)!r}")
    wt_unit_grants = resolve(os.path.join(wt_path, "tests", "unit", "test-zz.py"))
    wtg("tests/unit grants are identical in a linked worktree",
        wt_unit_grants == unit_grants,
        f"root={sorted(unit_grants)!r}, worktree={sorted(wt_unit_grants)!r}")

    for agent, domain in sorted(roster):
        chosen = None
        for entry in domain:
            pat = entry.get("path") if isinstance(entry, dict) else entry
            if not isinstance(pat, str):
                continue
            rel = instantiate(pat)
            if _hb.is_control_plane_target(rel):
                chosen = (pat, rel)
                break
        if chosen is None:
            wtg(f"{agent}: in-worktree grant equals root grant",
                False,
                "no domain entry instantiates to a control-plane target, so no path in "
                "this agent's domain can be granted in the harness base. Reported as a "
                "failure rather than skipped: a skip here is a silent hole.")
            continue
        pat, rel = chosen
        at_root = resolve(os.path.join(root, rel))
        in_wt = resolve(os.path.join(wt_path, rel))
        wtg(f"{agent}: in-worktree grant equals root grant, and names {agent}",
            at_root == in_wt and agent in at_root,
            f"glob {pat!r} -> {rel!r}; at root {sorted(at_root)!r}, in worktree "
            f"{sorted(in_wt)!r}; equal={at_root == in_wt}, "
            f"contains-self={agent in at_root}")

    # ================= T-04: THE DEEP LAYOUT =================
    # Everything above pins the ONE-level shape and must stay green (SC-09). Everything
    # below is what NO path could reach before T-04: the fixed-segment strip left the
    # repository segment in the path, so the second candidate matched no glob.

    deep = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "harness", "FEAT-90"), "FEAT-90")

    # SC-02c — one case per agent at <segment>/<repo>/<id>/, all sixteen.
    for agent, domain in sorted(roster):
        chosen = None
        for entry in domain:
            pat = entry.get("path") if isinstance(entry, dict) else entry
            if not isinstance(pat, str):
                continue
            rel = instantiate(pat)
            if _hb.is_control_plane_target(rel):
                chosen = (pat, rel)
                break
        if chosen is None:
            wtg(f"SC-02c {agent}: DEEP-layout grant equals root grant", False,
                "no domain entry instantiates to a control-plane target")
            continue
        pat, rel = chosen
        at_root = resolve(os.path.join(root, rel))
        in_deep = resolve(os.path.join(deep, rel))
        wtg(f"SC-02c {agent}: DEEP-layout grant equals root grant, and names {agent}",
            at_root == in_deep and agent in at_root,
            f"glob {pat!r} -> {rel!r}; root {sorted(at_root)!r}, deep "
            f"{sorted(in_deep)!r}; equal={at_root == in_deep}, self={agent in at_root}")

    # THE DEPTH IS NOT LOAD-BEARING. A rule that asks which checkout it stands in does
    # not care how deep the path is; a rule with a segment count does. Four levels.
    very_deep = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "a", "b", "c", "FEAT-90"), "abcFEAT90")
    _probe = ".harness/zz/features/zz/BRIEF.md"
    wtg("the depth is not load-bearing: <segment>/a/b/c/<id> resolves like the root",
        resolve(os.path.join(very_deep, _probe)) == resolve(os.path.join(root, _probe))
        and "harness-pm" in resolve(os.path.join(very_deep, _probe)),
        f"deep-4 {sorted(resolve(os.path.join(very_deep, _probe)))!r} vs root "
        f"{sorted(resolve(os.path.join(root, _probe)))!r}")

    # THE OLD MECHANISM IS GONE, not left standing beside its replacement. A dead regex
    # kept "for reference" is what leaves a segment count load-bearing for the next reader.
    wtg("WORKTREE_REL_RE no longer exists on harness_boundary",
        not hasattr(_hb, "WORKTREE_REL_RE"),
        "the fixed-segment strip is still importable, so a caller can still use it")

    # linked_worktrees: exactly the registered checkouts, and empty when there are none.
    lw_root = fixture(manifest_text)
    os.makedirs(os.path.join(lw_root, ".git"))
    wtg("linked_worktrees returns [] for a checkout with no worktrees",
        _hb.linked_worktrees(lw_root) == [],
        f"got {_hb.linked_worktrees(lw_root)!r}")
    a = make_linked_worktree(
        lw_root, os.path.join(lw_root, ".claude", "worktrees", "harness", "FEAT-90"), "FEAT-90")
    b = make_linked_worktree(
        lw_root, os.path.join(lw_root, ".claude", "worktrees", "harness", "FEAT-91"), "FEAT-91")
    wtg("linked_worktrees returns exactly the two registered checkouts, as realpaths",
        _hb.linked_worktrees(lw_root) == sorted([_hb.real(a), _hb.real(b)]),
        f"got {_hb.linked_worktrees(lw_root)!r}, want {sorted([_hb.real(a), _hb.real(b)])!r}")

    for name, ok, detail in WTG:
        if ok:
            print(f"ok    {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n        {detail}")
    print(f"\n{len(WTG) - fails}/{len(WTG)} worktree grant-parity cases passed.\n")
    shutil.rmtree(tmp, ignore_errors=True)
    return fails


def main():
    return drive(globals())


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
