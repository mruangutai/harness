#!/usr/bin/env python3
"""check-domain.sh: the in-flight claim set decides who may write a worktree.

Slice of the former test-check-domain.py (issue #1527) — issue #1304's claim-set cases,
including the frozen prior-hook control (fixtures/prior-check-domain.sh.fixture) that
proves the pre-change hook allowed what the guard now refuses. Its own file rather than
a tail on test-check-domain-approval.py: at ~4s it was that file's outlier, and the
surface is claim ownership, not approval.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_tests)
import json, os, shutil, subprocess, sys, tempfile
from isolated_bin import isolated_bin
from check_domain_support import (FIXTURE_MANIFEST, HOOK, TESTS_DIR, _env, drive, fixture,
    make_linked_worktree)


def bug1304_pre_change_hook(dest):
    copied_bin = isolated_bin(dest)
    hook = os.path.join(copied_bin, "check-domain.sh")
    fixture_path = os.path.join(
        TESTS_DIR, "fixtures", "prior-check-domain.sh.fixture")
    shutil.copyfile(fixture_path, hook)
    os.chmod(hook, 0o755)
    return hook


def _bug1304_fire(root, destination, agent, hook=HOOK, tool="Write"):
    absolute = destination if os.path.isabs(destination) else os.path.join(root, destination)
    os.makedirs(os.path.dirname(absolute), exist_ok=True)
    if tool == "Edit":
        with open(absolute, "a", encoding="utf-8"):
            pass
        tool_input = {"file_path": absolute, "old_string": "before", "new_string": "after"}
    else:
        tool_input = {"file_path": absolute, "content": "after"}
    payload = {"agent_type": agent, "tool_name": tool, "tool_input": tool_input}
    return subprocess.run([hook], input=json.dumps(payload), capture_output=True,
                          text=True, env=_env(root))


def bug1304_assert_pre_change_allows(results, name, root, destination, agent):
    isolated = tempfile.mkdtemp()
    prior = bug1304_pre_change_hook(isolated)
    allowed = _bug1304_fire(root, destination, agent, hook=prior)
    stderr = allowed.stderr or ""
    quiet = not any(marker in stderr for marker in (
        "enforcement OFF", "was not enforced", "passing through"))
    control = _bug1304_fire(
        root, ".harness/forbidden/positive-control.md", agent, hook=prior)
    results.append((
        name + " is allowed by the frozen pre-change hook",
        allowed.returncode == 0 and quiet and control.returncode == 2,
        f"allow={allowed.returncode} control={control.returncode} stderr={stderr[:160]!r}",
    ))
    shutil.rmtree(isolated, ignore_errors=True)


def _bug1304_domain_expect(results, root, agent, name, destination, want,
                           contains=None, tool="Write"):
    response = _bug1304_fire(root, destination, agent, tool=tool)
    text = response.stdout + response.stderr
    ok = response.returncode == want and (contains is None or contains in text)
    results.append((name, ok, f"exit={response.returncode} output={text[:180]!r}"))
    return response


def _bug1304_domain_context(agent, inflight_registry):
    manifest = FIXTURE_MANIFEST.replace(
        '          - { path: ".", read: true }',
        '          - { path: ".claude/worktrees/**", upsert: true }\n'
        '          - { path: ".", read: true }',
    )
    root = fixture(manifest)
    first = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-1304-A"), "A")
    second = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-1304-B"), "B")
    inflight_registry.claim(
        first, agent, "harness-product-lead", first,
        feature="FEAT-1304-A-claim-guard")
    return {
        "manifest": manifest, "root": root, "first": first, "second": second,
        "agent": agent, "main": ".harness/allowed/main.md",
    }


def _bug1304_domain_main_routes(results, context):
    root = context["root"]
    agent = context["agent"]
    first = context["first"]
    main = context["main"]
    cases = (
        ("relative main", main),
        ("absolute main", os.path.join(root, main)),
        ("sibling", os.path.join(context["second"], ".harness", "allowed", "sibling.md")),
    )
    for label, destination in cases:
        _bug1304_domain_expect(
            results, root, agent, f"{label}-checkout write is refused",
            destination, 2, first)
        bug1304_assert_pre_change_allows(
            results, label, root, destination, agent)

    _bug1304_domain_expect(
        results, root, agent, "relative held-worktree write is allowed",
        os.path.relpath(os.path.join(first, ".harness", "allowed", "own.md"), root), 0)
    _bug1304_domain_expect(
        results, root, agent, "absolute held-worktree write is allowed",
        os.path.join(first, ".harness", "allowed", "own-absolute.md"), 0)


def _bug1304_domain_unbound_routes(results, context):
    agent = context["agent"]
    root = fixture(context["manifest"])
    response = _bug1304_fire(root, context["main"], agent)
    results.append(("unbound agent remains allowed", response.returncode == 0,
                    f"exit={response.returncode}"))
    scratch = os.path.join(tempfile.mkdtemp(), "scratch.md")
    _bug1304_domain_expect(
        results, context["root"], agent, "scratch write remains allowed", scratch, 0)


def _bug1304_domain_owner_claim(results, context, inflight_registry):
    agent = context["agent"]
    root = fixture(context["manifest"])
    matching = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-1304-C"), "C")
    inflight_registry.claim(
        root, agent, "harness-product-lead", root, feature="FEAT-404-no-worktree")
    destination = ".harness/allowed/unmatched.md"
    response = _bug1304_fire(root, destination, agent)
    results.append(("unresolved owner-root claim remains unbound",
                    response.returncode == 0, f"exit={response.returncode}"))
    inflight_registry.claim(
        root, agent, "harness-product-lead", root, feature="FEAT-1304-C-linked")
    _bug1304_domain_expect(
        results, root, agent, "owner-root matching claim refuses main write",
        destination, 2, matching)
    bug1304_assert_pre_change_allows(
        results, "owner-root matching claim", root, destination, agent)


def _bug1304_domain_multi_and_malformed(results, context, inflight_registry):
    agent = context["agent"]
    inflight_registry.claim(
        context["second"], agent, "harness-product-lead", context["second"],
        feature="FEAT-1304-B-claim-guard")
    _bug1304_domain_expect(
        results, context["root"], agent, "two claims still allow either held worktree",
        os.path.join(context["second"], ".harness", "allowed", "own.md"), 0)

    malformed = os.path.join(context["root"], ".claude", "worktrees", "broken")
    os.makedirs(malformed, exist_ok=True)
    with open(os.path.join(malformed, ".git"), "w", encoding="utf-8") as handle:
        handle.write("not-a-pointer\n")
    destination = os.path.join(malformed, ".harness", "allowed", "x.md")
    _bug1304_domain_expect(
        results, context["root"], agent,
        "malformed checkout pointer refuses with a nonempty claim set",
        destination, 2, context["first"])
    bug1304_assert_pre_change_allows(
        results, "malformed checkout", context["root"], destination, agent)


def _bug1304_domain_ambiguous(results, context, inflight_registry):
    agent = context["agent"]
    root = fixture(context["manifest"])
    make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT"), "AMB1")
    make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-X"), "AMB2")
    inflight_registry.claim(
        root, agent, "harness-product-lead", root, feature="FEAT-X-ambiguous")
    _bug1304_domain_expect(
        results, root, agent, "ambiguous claim refuses and names candidates",
        context["main"], 2, "FEAT, FEAT-X")
    bug1304_assert_pre_change_allows(
        results, "ambiguous claim", root, context["main"], agent)


def _bug1304_domain_short_claim(results, context, inflight_registry):
    agent = context["agent"]
    root = fixture(context["manifest"])
    short = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "BUG-1304"), "SHORT")
    inflight_registry.claim(
        short, agent, "harness-product-lead", short,
        feature="BUG-1304-worktree-relative-path-guard")
    _bug1304_domain_expect(
        results, root, agent, "short-form worktree claim refuses main write",
        context["main"], 2)
    bug1304_assert_pre_change_allows(
        results, "short-form", root, context["main"], agent)


def _bug1304_domain_aged_claim(results, context, inflight_registry):
    registry = os.path.join(context["first"], inflight_registry.REGISTRY_REL)
    data = json.load(open(registry, encoding="utf-8"))
    data["claims"][0]["started_at"] = (
        __import__("time").time() - inflight_registry.CLAIM_TTL_SECONDS - 5)
    with open(registry, "w", encoding="utf-8") as handle:
        json.dump(data, handle)
    _bug1304_domain_expect(
        results, context["root"], context["agent"],
        "aged compatibility claim still refuses",
        context["main"], 2, context["first"])
    bug1304_assert_pre_change_allows(
        results, "aged claim", context["root"], context["main"], context["agent"])


def _bug1304_domain_unreadable(results, context, inflight_registry):
    agent = context["agent"]
    root = fixture(context["manifest"])
    worktree = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-BAD"), "BAD")
    inflight_registry.claim(
        worktree, agent, "harness-product-lead", worktree,
        feature="FEAT-BAD-unreadable")
    registry = os.path.join(worktree, inflight_registry.REGISTRY_REL)
    with open(registry, "w", encoding="utf-8") as handle:
        handle.write("{")
    _bug1304_domain_expect(
        results, root, agent, "unreadable registry refuses and names file",
        context["main"], 2, registry)
    bug1304_assert_pre_change_allows(
        results, "unreadable registry", root, context["main"], agent)
    with open(registry, "w", encoding="utf-8") as handle:
        json.dump({"schema_version": 2, "claims": []}, handle)
    response = _bug1304_fire(root, context["main"], agent)
    results.append(("readable empty registry remains allowed",
                    response.returncode == 0, f"exit={response.returncode}"))


def _bug1304_domain_partial_registry(results, context, inflight_registry):
    agent = context["agent"]
    root = fixture(context["manifest"])
    own = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-OWN"), "OWN")
    corrupt = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-CORRUPT"), "CORRUPT")
    inflight_registry.claim(
        own, agent, "harness-product-lead", own, feature="FEAT-OWN-readable")
    registry = os.path.join(corrupt, inflight_registry.REGISTRY_REL)
    os.makedirs(os.path.dirname(registry), exist_ok=True)
    with open(registry, "w", encoding="utf-8") as handle:
        handle.write("{")
    response = _bug1304_fire(
        root, os.path.join(own, ".harness", "allowed", "inside.md"), agent)
    results.append(("readable member allows despite unrelated unreadable registry",
                    response.returncode == 0, f"exit={response.returncode}"))
    _bug1304_domain_expect(
        results, root, agent, "outside partial claim set refuses unreadable registry",
        context["main"], 2, registry)
    bug1304_assert_pre_change_allows(
        results, "partial unreadable", root, context["main"], agent)


def run_bug1304_claim_set():
    """Issue #1304 claim-set cases; frozen guard provenance: a4e8ecf7."""
    import inflight_registry

    results = []
    context = _bug1304_domain_context("harness-documentor", inflight_registry)
    _bug1304_domain_main_routes(results, context)
    _bug1304_domain_unbound_routes(results, context)
    _bug1304_domain_owner_claim(results, context, inflight_registry)
    _bug1304_domain_multi_and_malformed(results, context, inflight_registry)
    _bug1304_domain_ambiguous(results, context, inflight_registry)
    _bug1304_domain_short_claim(results, context, inflight_registry)
    _bug1304_domain_aged_claim(results, context, inflight_registry)
    _bug1304_domain_unreadable(results, context, inflight_registry)
    _bug1304_domain_partial_registry(results, context, inflight_registry)

    failures = 0
    for name, ok, detail in results:
        print(("PASS " if ok else "FAIL "), "[bug1304]", name)
        if not ok:
            failures += 1
            print("      " + detail)
    return failures


def main():
    return drive(globals())


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
