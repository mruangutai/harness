#!/usr/bin/env python3
"""check-domain.py: the in-flight claim set decides who may write a worktree.

Slice of the former test-check-domain.py (issue #1527) — issue #1304's claim-set cases,
including the frozen prior-hook control (`fixtures/prior-check-domain.fixture`) that
proves the pre-change hook allowed what the guard now refuses. Its own file rather than
a tail on test-check-domain-approval.py: at ~4s it was that file's outlier, and the
surface is claim ownership, not approval.
"""
from integration_support import TESTS
import functools, json, os, shutil, subprocess, sys, tempfile, time
import inflight_registry
from check_support import Checks
from isolated_bin import isolated_bin
from check_domain_support import (FIXTURE_MANIFEST, HOOK, _env, drive, fixture,
    fixture_fleet, make_linked_worktree)

AGENT = "harness-documentor"
PRIOR_FIXTURE = str(TESTS / "integration" / "fixtures" / "prior-check-domain.fixture")
C = Checks()


def check(name, ok, detail=""):
    return C.check("[bug1304] " + name, ok, detail)


@functools.cache
def bug1304_pre_change_hook():
    """The frozen prior hook in one isolated bin copy, built once: every fixture root reaches
    it through HARNESS_PROJECT_DIR, so where the copy sits changes no answer."""
    copied_bin = isolated_bin(tempfile.mkdtemp())
    hook = os.path.join(copied_bin, "check-domain.py")
    shutil.copyfile(PRIOR_FIXTURE, hook)
    os.chmod(hook, 0o755)
    return hook


def _bug1304_fire(root, destination, agent=AGENT, hook=HOOK, tool="Write",
                  agent_id=None, parent_agent_id=None, feature=None):
    absolute = destination if os.path.isabs(destination) else os.path.join(root, destination)
    os.makedirs(os.path.dirname(absolute), exist_ok=True)
    if tool == "Edit":
        with open(absolute, "a", encoding="utf-8"):
            pass
        tool_input = {"file_path": absolute, "old_string": "before", "new_string": "after"}
    else:
        tool_input = {"file_path": absolute, "content": "after"}
    payload = {"agent_type": agent, "tool_name": tool, "tool_input": tool_input}
    if agent_id:
        payload["harness_agent_id"] = agent_id
    if parent_agent_id:
        payload["harness_parent_agent_id"] = parent_agent_id
    if feature:
        payload["harness_feature"] = feature
    return subprocess.run([hook], input=json.dumps(payload), capture_output=True,
                          text=True, env=_env(root))


def _rewrite_registry(path, mutate):
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    mutate(data)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle)


def _write_unreadable(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("{")


def bug1304_assert_pre_change_allows(name, root, destination):
    prior = bug1304_pre_change_hook()
    allowed = _bug1304_fire(root, destination, hook=prior)
    stderr = allowed.stderr or ""
    quiet = not any(marker in stderr for marker in (
        "enforcement OFF", "was not enforced", "passing through"))
    control = _bug1304_fire(root, ".harness/forbidden/positive-control.md", hook=prior)
    check(
        name + " is allowed by the frozen pre-change hook",
        allowed.returncode == 0 and quiet and control.returncode == 2,
        f"allow={allowed.returncode} control={control.returncode} stderr={stderr[:160]!r}",
    )


def _expect(name, response, want, contains=None):
    output = response.stdout + response.stderr
    ok = response.returncode == want and (contains is None or contains in output)
    check(name, ok, f"exit={response.returncode} output={output[:240]!r}")
    return response


def _bug1304_domain_expect(root, name, destination, want, contains=None):
    return _expect(name, _bug1304_fire(root, destination), want, contains)


def _bug1304_domain_context():
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
        first, AGENT, "harness-product-lead", first,
        feature="FEAT-1304-A-claim-guard")
    return {
        "manifest": manifest, "root": root, "first": first, "second": second,
        "main": ".harness/allowed/main.md",
    }


def _bug1304_domain_main_routes(context):
    root = context["root"]
    first = context["first"]
    main = context["main"]
    cases = (
        ("relative main", main),
        ("absolute main", os.path.join(root, main)),
        ("sibling", os.path.join(context["second"], ".harness", "allowed", "sibling.md")),
    )
    for label, destination in cases:
        _bug1304_domain_expect(
            root, f"{label}-checkout write is refused", destination, 2, first)
        bug1304_assert_pre_change_allows(label, root, destination)

    _bug1304_domain_expect(
        root, "relative held-worktree write is allowed",
        os.path.relpath(os.path.join(first, ".harness", "allowed", "own.md"), root), 0)
    _bug1304_domain_expect(
        root, "absolute held-worktree write is allowed",
        os.path.join(first, ".harness", "allowed", "own-absolute.md"), 0)


def _bug1304_domain_unbound_routes(context):
    root = fixture(context["manifest"])
    _bug1304_domain_expect(root, "unbound agent remains allowed", context["main"], 0)
    scratch = os.path.join(tempfile.mkdtemp(), "scratch.md")
    _bug1304_domain_expect(context["root"], "scratch write remains allowed", scratch, 0)


def _bug1304_domain_owner_claim(context):
    root = fixture(context["manifest"])
    matching = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-1304-C"), "C")
    inflight_registry.claim(
        root, AGENT, "harness-product-lead", root, feature="FEAT-404-no-worktree")
    destination = ".harness/allowed/unmatched.md"
    _bug1304_domain_expect(
        root, "unresolved owner-root claim remains unbound", destination, 0)
    inflight_registry.claim(
        root, AGENT, "harness-product-lead", root, feature="FEAT-1304-C-linked")
    _bug1304_domain_expect(
        root, "owner-root matching claim refuses main write", destination, 2, matching)
    bug1304_assert_pre_change_allows("owner-root matching claim", root, destination)


def _bug1304_domain_multi_and_malformed(context):
    inflight_registry.claim(
        context["second"], AGENT, "harness-product-lead", context["second"],
        feature="FEAT-1304-B-claim-guard")
    _bug1304_domain_expect(
        context["root"], "two claims still allow either held worktree",
        os.path.join(context["second"], ".harness", "allowed", "own.md"), 0)

    malformed = os.path.join(context["root"], ".claude", "worktrees", "broken")
    os.makedirs(malformed, exist_ok=True)
    with open(os.path.join(malformed, ".git"), "w", encoding="utf-8") as handle:
        handle.write("not-a-pointer\n")
    destination = os.path.join(malformed, ".harness", "allowed", "x.md")
    _bug1304_domain_expect(
        context["root"], "malformed checkout pointer refuses with a nonempty claim set",
        destination, 2, context["first"])
    bug1304_assert_pre_change_allows("malformed checkout", context["root"], destination)


def _runtime_lineage_domain_routes(context):
    _rewrite_registry(
        os.path.join(context["first"], inflight_registry.REGISTRY_REL),
        lambda data: data["claims"][0].update({
            "agent_id": "DocumentorOne",
            "parent_agent_id": "ProductLeadOne",
        }))
    receipt = inflight_registry.claim_with_receipt(
        context["second"], AGENT, "harness-product-lead", context["second"],
        feature="FEAT-1304-B-claim-guard",
    )
    inflight_registry.attach_runtime_identity(
        context["second"], AGENT, "FEAT-1304-B-claim-guard",
        claim_id=receipt["claim_id"],
        agent_id="DocumentorTwo",
        parent_agent_id="ProductLeadTwo",
    )
    first_destination = os.path.join(
        context["first"], ".harness", "allowed", "runtime-one.md")
    second_destination = os.path.join(
        context["second"], ".harness", "allowed", "runtime-two.md")
    one = {"agent_id": "DocumentorOne", "parent_agent_id": "ProductLeadOne"}
    own = _bug1304_fire(context["root"], first_destination, **one)
    sibling = _bug1304_fire(context["root"], second_destination, **one)
    second = _bug1304_fire(
        context["root"], second_destination,
        agent_id="DocumentorTwo", parent_agent_id="ProductLeadTwo")
    _expect("exact runtime lineage allows its own worktree", own, 0)
    sibling_output = (sibling.stdout + sibling.stderr)[:240]
    check(
        "exact runtime lineage refuses a same-persona sibling worktree",
        sibling.returncode == 2 and context["first"] in sibling.stderr,
        f"exit={sibling.returncode} output={sibling_output!r}",
    )
    # #1882: the refusal names the identity the guard judged, so the next occurrence of an
    # unexplained cross-feature block carries its own evidence instead of a guess.
    check(
        "the sibling refusal names the runtime identity it judged (#1882)",
        "agent_id=DocumentorOne" in sibling.stderr and "parent=ProductLeadOne" in sibling.stderr,
        f"output={sibling_output!r}",
    )
    no_identity = _bug1304_fire(context["root"], context["main"])
    check(
        "an identity-less refusal says so (#1882)",
        no_identity.returncode == 2 and "agent_id=none" in no_identity.stderr,
        f"exit={no_identity.returncode} output={(no_identity.stdout + no_identity.stderr)[:240]!r}",
    )
    _expect("second runtime lineage retains its own worktree", second, 0)


def _bug1304_domain_ambiguous(context):
    root = fixture(context["manifest"])
    make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT"), "AMB1")
    make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-X"), "AMB2")
    inflight_registry.claim(
        root, AGENT, "harness-product-lead", root, feature="FEAT-X-ambiguous")
    _bug1304_domain_expect(
        root, "ambiguous claim refuses and names candidates",
        context["main"], 2, "FEAT, FEAT-X")
    bug1304_assert_pre_change_allows("ambiguous claim", root, context["main"])


def _bug1304_domain_short_claim(context):
    root = fixture(context["manifest"])
    short = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "BUG-91"), "SHORT")
    inflight_registry.claim(
        short, AGENT, "harness-product-lead", short,
        feature="BUG-91-worktree-relative-path-fixture")
    _bug1304_domain_expect(
        root, "short-form worktree claim refuses main write", context["main"], 2)
    bug1304_assert_pre_change_allows("short-form", root, context["main"])


def _age_claim(data):
    data["claims"][0]["started_at"] = time.time() - 10 * 86400


def _bug1304_domain_aged_claim(context):
    """DEC-204/DEC-233: a claim binds for exactly as long as its OMP supervisor lives. Age
    alone never releases it; a dead supervisor always does."""
    registry = os.path.join(context["first"], inflight_registry.REGISTRY_REL)
    _rewrite_registry(registry, _age_claim)
    _bug1304_domain_expect(
        context["root"], "ten-day-old claim with a live supervisor still refuses",
        context["main"], 2, context["first"])
    bug1304_assert_pre_change_allows("aged claim", context["root"], context["main"])
    dead = subprocess.run([sys.executable, "-c", "import os; print(os.getpid())"],
                          capture_output=True, text=True, check=True)

    def exited_supervisor(data):
        data["claims"][0]["supervisor_pid"] = int(dead.stdout)
        data["claims"][0].pop("supervisor_started_at", None)
        data["claims"][0]["started_at"] = time.time()

    _rewrite_registry(registry, exited_supervisor)
    response = _bug1304_fire(context["root"], context["main"])
    check(
        "fresh claim whose supervisor has exited no longer binds",
        context["first"] not in response.stdout + response.stderr,
        f"exit={response.returncode} output={(response.stdout + response.stderr)[:180]!r}")


def _bug1304_domain_unreadable(context):
    root = fixture(context["manifest"])
    worktree = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-BAD"), "BAD")
    inflight_registry.claim(
        worktree, AGENT, "harness-product-lead", worktree,
        feature="FEAT-BAD-unreadable")
    registry = os.path.join(worktree, inflight_registry.REGISTRY_REL)
    _write_unreadable(registry)
    _bug1304_domain_expect(
        root, "unreadable registry refuses and names file", context["main"], 2, registry)
    bug1304_assert_pre_change_allows("unreadable registry", root, context["main"])
    with open(registry, "w", encoding="utf-8") as handle:
        json.dump({"schema_version": 2, "claims": []}, handle)
    _bug1304_domain_expect(root, "readable empty registry remains allowed", context["main"], 0)


def _bug1304_domain_partial_registry(context):
    root = fixture(context["manifest"])
    own = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-OWN"), "OWN")
    corrupt = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-CORRUPT"), "CORRUPT")
    inflight_registry.claim(
        own, AGENT, "harness-product-lead", own, feature="FEAT-OWN-readable")
    registry = os.path.join(corrupt, inflight_registry.REGISTRY_REL)
    _write_unreadable(registry)
    _bug1304_domain_expect(
        root, "readable member allows despite unrelated unreadable registry",
        os.path.join(own, ".harness", "allowed", "inside.md"), 0)
    _bug1304_domain_expect(
        root, "outside partial claim set refuses unreadable registry",
        context["main"], 2, registry)
    bug1304_assert_pre_change_allows("partial unreadable", root, context["main"])


def _repository_fixture():
    # A wildcard control-plane grant reaches every product's `.harness/<segment>/docs/`, so
    # the repository decision, not the grant, must keep each product's segment its own.
    workspace = tempfile.mkdtemp(prefix="harness-repository-binding-")
    root = fixture_fleet(FIXTURE_MANIFEST.replace(
        "{ path: .harness/allowed/**, upsert: true }",
        "{ path: .harness/allowed/**, upsert: true }\n"
        "          - { path: .harness/*/docs/**, upsert: true }"), json.dumps({
            "schema": "factory-fleet/1",
            "workspace_root": workspace,
            "repos": [
                {"name": "acme/product-a", "default_branch": "main"},
                {"name": "acme/product-b", "default_branch": "main"},
            ],
        }))
    products = {
        name: os.path.join(workspace, name, "allowed", "change.md")
        for name in ("product-a", "product-b")
    }
    for target in products.values():
        os.makedirs(os.path.dirname(target), exist_ok=True)
    return root, products


def _repository_claim(root, repository, feature, agent_id, parent_agent_id):
    receipt = inflight_registry.claim_with_receipt(
        root, AGENT, "harness-product-lead", root,
        feature=feature,
        repository=repository,
    )
    if not inflight_registry.attach_runtime_identity(
        root, AGENT, feature,
        claim_id=receipt["claim_id"],
        agent_id=agent_id,
        parent_agent_id=parent_agent_id,
    ):
        raise AssertionError("fixture claim did not attach")
    return receipt


def _repository_fire(root, target, feature, agent_id, parent_agent_id, tool="Write"):
    return _bug1304_fire(
        root, target, tool=tool,
        agent_id=agent_id, parent_agent_id=parent_agent_id, feature=feature,
    )


def _repository_happy_routes(feature):
    root, products = _repository_fixture()
    first = _repository_claim(
        root, "product-a", feature, "DocumentorOne", "ProductLeadOne")
    cases = (
        ("repository-bound child can repeat Write in its own product",
         _repository_fire(
             root, products["product-a"], feature, "DocumentorOne", "ProductLeadOne"),
         0, None),
        ("repository-bound child can Edit in its own product",
         _repository_fire(
             root, products["product-a"], feature, "DocumentorOne", "ProductLeadOne",
             tool="Edit"),
         0, None),
        ("repository-bound child cannot cross into another product",
         _repository_fire(
             root, products["product-b"], feature, "DocumentorOne", "ProductLeadOne"),
         2, "mismatched"),
        ("repository binding includes the immediate parent",
         _repository_fire(
             root, products["product-a"], feature, "DocumentorOne", "ProductLeadTwo"),
         2, "mismatched"),
        ("repository-bound child writes its own product's control-plane segment",
         _repository_fire(
             root, os.path.join(root, ".harness", "product-a", "docs", "change.md"),
             feature, "DocumentorOne", "ProductLeadOne"),
         0, None),
        ("repository-bound child cannot write another product's control-plane segment",
         _repository_fire(
             root, os.path.join(root, ".harness", "product-b", "docs", "change.md"),
             feature, "DocumentorOne", "ProductLeadOne"),
         2, "mismatched"),
        # A segment is a fleet member whatever its spelling: on a case-insensitive disk
        # `.harness/PRODUCT-B/` IS product-b's directory, so it needs product-b's claim.
        ("repository-bound child cannot reach another product's segment by changing its case",
         _repository_fire(
             root, os.path.join(root, ".harness", "PRODUCT-B", "docs", "change.md"),
             feature, "DocumentorOne", "ProductLeadOne"),
         2, "mismatched"),
    )
    for name, response, want, contains in cases:
        _expect(name, response, want, contains)
    _repository_claim(
        root, "product-a", feature, "DocumentorTwo", "ProductLeadOne")
    sibling = _repository_fire(
        root, products["product-a"], feature, "DocumentorTwo", "ProductLeadOne")
    _expect(
        "same-role siblings retain distinct valid product claims", sibling, 0)
    return first


def _repository_missing_and_released(feature):
    missing_root, missing_products = _repository_fixture()
    missing = _repository_fire(
        missing_root, missing_products["product-a"], feature, "MissingChild", "ProductLeadOne")
    _expect(
        "product write without a repository claim fails closed", missing, 2, "missing")

    released_root, released_products = _repository_fixture()
    receipt = _repository_claim(
        released_root, "product-a", feature,
        "ReleasedChild", "ProductLeadOne")
    inflight_registry.release(released_root, claim_id=receipt["claim_id"], feature=feature)
    released = _repository_fire(
        released_root, released_products["product-a"], feature,
        "ReleasedChild", "ProductLeadOne")
    _expect(
        "released repository claim fails closed", released, 2, "released")


def _repository_stale_and_ambiguous(feature):
    stale_root, stale_products = _repository_fixture()
    _repository_claim(
        stale_root, "product-a", feature, "StaleChild", "ProductLeadOne")

    def never_alive(data):
        data["claims"][0]["supervisor_pid"] = 99999999
        data["claims"][0].pop("supervisor_started_at", None)

    _rewrite_registry(os.path.join(stale_root, inflight_registry.REGISTRY_REL), never_alive)
    stale = _repository_fire(
        stale_root, stale_products["product-a"], feature, "StaleChild", "ProductLeadOne")
    _expect(
        "stale repository claim fails closed", stale, 2, "stale")

    ambiguous_root, ambiguous_products = _repository_fixture()
    receipt = _repository_claim(
        ambiguous_root, "product-a", feature,
        "AmbiguousChild", "ProductLeadOne")

    def duplicate_claim(data):
        duplicate = dict(data["claims"][0])
        duplicate["claim_id"] = receipt["claim_id"] + "-duplicate"
        data["claims"].append(duplicate)

    _rewrite_registry(
        os.path.join(ambiguous_root, inflight_registry.REGISTRY_REL), duplicate_claim)
    ambiguous = _repository_fire(
        ambiguous_root, ambiguous_products["product-a"], feature,
        "AmbiguousChild", "ProductLeadOne")
    _expect(
        "ambiguous repository claim fails closed", ambiguous, 2, "ambiguous")


def _repository_collision_and_unreadable(feature, first_claim_id):
    collision_root, collision_products = _repository_fixture()
    _repository_claim(
        collision_root, "product-a", feature,
        "CollidingChild", "ProductLeadOne")

    def foreign_claim(data):
        foreign = dict(data["claims"][0])
        foreign["claim_id"] += "-foreign"
        foreign["feature"] = "FEAT-496-other-dispatch"
        data["claims"].append(foreign)

    _rewrite_registry(
        os.path.join(collision_root, inflight_registry.REGISTRY_REL), foreign_claim)
    collision = _repository_fire(
        collision_root, collision_products["product-a"], feature,
        "CollidingChild", "ProductLeadOne")
    _expect(
        "reused active runtime identity fails as collision",
        collision, 2, "collision")

    unreadable_root, unreadable_products = _repository_fixture()
    _write_unreadable(os.path.join(unreadable_root, inflight_registry.REGISTRY_REL))
    unreadable = _repository_fire(
        unreadable_root, unreadable_products["product-a"], feature,
        "UnreadableChild", "ProductLeadOne")
    _expect(
        "unreadable repository registry fails closed", unreadable, 2, "unreadable")
    output = unreadable.stdout + unreadable.stderr
    check(
        "repository refusal does not expose registry paths or claim ids",
        inflight_registry.REGISTRY_REL not in output and first_claim_id not in output,
        output[:240],
    )


def _repository_binding_in_feature_worktree():
    """#2056: a fleet feature plans in its harness planning worktree, and dispatch-guard records
    its claims where inflight_registry.feature_root puts the feature — that worktree's registry.
    The repository binding must be read from that same registry, not the owner root's, or every
    product-segment write of a correctly dispatched child is refused as `missing`."""
    feature = "FEAT-92-product-a-platform"
    root, products = _repository_fixture()
    worktree = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "harness", feature), feature)
    assert os.path.realpath(inflight_registry.feature_root(root, feature)) == os.path.realpath(worktree)
    _repository_claim(
        worktree, "product-a", feature, "DocumentorOne", "ProductLeadOne")
    for name, target in (
        ("worktree-registry binding allows the planning worktree's control-plane segment",
         os.path.join(worktree, ".harness", "product-a", "docs", "change.md")),
        ("worktree-registry binding allows the product checkout",
         products["product-a"]),
    ):
        _expect(name, _repository_fire(
            root, target, feature, "DocumentorOne", "ProductLeadOne"), 0)
    _expect(
        "worktree-registry binding still refuses a stranger's lineage",
        _repository_fire(root, products["product-a"], feature, "Stranger", "ProductLeadOne"),
        2, "runtime repository binding")


def _repository_binding_routes():
    """FEAT-495: wildcard product grants never outrank exact runtime repository lineage."""
    feature = "FEAT-93-product-write"
    first = _repository_happy_routes(feature)
    _repository_missing_and_released(feature)
    _repository_stale_and_ambiguous(feature)
    _repository_collision_and_unreadable(feature, first["claim_id"])
    _repository_binding_in_feature_worktree()


def run_bug1304_claim_set():
    """Issue #1304 claim-set cases; frozen guard provenance: a4e8ecf7."""
    context = _bug1304_domain_context()
    _bug1304_domain_main_routes(context)
    _bug1304_domain_unbound_routes(context)
    _bug1304_domain_owner_claim(context)
    _bug1304_domain_multi_and_malformed(context)
    _runtime_lineage_domain_routes(context)
    _bug1304_domain_ambiguous(context)
    _bug1304_domain_short_claim(context)
    _bug1304_domain_aged_claim(context)
    _bug1304_domain_unreadable(context)
    _bug1304_domain_partial_registry(context)
    _repository_binding_routes()
    return len(C.failed)


def main():
    return drive(globals())


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
