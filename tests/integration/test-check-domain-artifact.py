#!/usr/bin/env python3
"""check-domain.py: artifact integrity on the Write and Edit routes.

Slice of the former test-check-domain.py (issue #1527) — FEAT-50's artifact binding,
BUG-1124's state.yaml upserts, BUG-1106's Edit route, BUG-1305's run-identity marker
and identity cases, and BUG-151's self-check of the aggregation safeguard that the
shared driver in check_domain_support.py applies to every block in this family.
"""
from integration_support import BIN
import io, json, os, re, subprocess, sys, tempfile, yaml
from isolated_bin import isolated_bin
from check_domain_support import (HERE, HOOK, _aggregation_verdict, _fire_edit,
    _handoff_done_when_fixture, _handoff_text, _invoke, _run_block_captured, drive, fire,
    fire_post, fire_write_payload, fixture, fixture_fleet, make_linked_worktree)

VALIDATE_DIGEST = str(BIN / "validate-digest.py")


def _report(results, label, tag="", cut=None):
    """Print each (name, ok, detail) in the column-0 ok/FAIL shape drive's aggregation
    safeguard parses, then a pass-count line when `label` is given; return the failures."""
    prefix = f"[{tag}] " if tag else ""
    failures = 0
    for name, ok, detail in results:
        if ok:
            print(f"ok    {prefix}{name}")
            continue
        failures += 1
        shown = detail if cut is None else str(detail).strip()[:cut]
        print(f"FAIL  {prefix}{name}\n      | {shown}")
    if label:
        print(f"\n{len(results) - failures}/{len(results)} {label} cases passed.")
    return failures


FEAT50_MANIFEST = """schema_version: 1
teams:
  - name: build
    members:
      - name: harness-documentor
        domain:
          - { path: .harness/*/features/*/BRIEF.md, upsert: true }
"""


FEAT50_FEATURE = "FEAT-X-thing"


FEAT50_REL = f".harness/harness/features/{FEAT50_FEATURE}/BRIEF.md"


def _feat50_feature_fixture(wt_id=None):
    root = fixture(FEAT50_MANIFEST)
    if wt_id is None:
        return root, None
    worktree = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", wt_id), wt_id)
    return root, worktree


def _feat50_binding_case(name, wt_id):
    root, worktree = _feat50_feature_fixture(wt_id)
    target = os.path.join(root, FEAT50_REL)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    result = fire(root, FEAT50_REL)
    ok = result.returncode == 2 and target in result.stderr and worktree in result.stderr
    return (name, ok, f"{result.returncode}: {result.stderr}"), root, worktree, target, result


def _feat50_inside_case(root, worktree):
    rel = os.path.join(os.path.relpath(worktree, root), FEAT50_REL)
    os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
    result = fire(root, rel)
    ok = result.returncode == 0 and "belongs in worktree" not in result.stderr
    return ("feature-checkout-inside binding skipped after worktree strip", ok,
            f"{result.returncode}: {result.stderr}")


def _feat50_absent_case():
    root, _worktree = _feat50_feature_fixture()
    os.makedirs(os.path.dirname(os.path.join(root, FEAT50_REL)), exist_ok=True)
    result = fire(root, FEAT50_REL)
    return ("feature-checkout-absent", result.returncode == 0,
            f"{result.returncode}: {result.stderr}")


def _feat50_mutant_between(start, end, iso):
    with open(HOOK, encoding="utf-8") as source_file:
        source = source_file.read()
    begin = source.find(start)
    finish = source.find(end, begin + len(start))
    if begin < 0 or finish < 0:
        raise AssertionError("INCONCLUSIVE: mutant anchors absent")
    changed = source[:begin] + source[finish:]
    if changed == source:
        raise AssertionError("INCONCLUSIVE: mutant is byte-identical")
    path = os.path.join(iso, "check-domain.py")
    with open(path, "w", encoding="utf-8") as mutant_file:
        mutant_file.write(changed)
    os.chmod(path, os.stat(HOOK).st_mode)
    return path


def _feat50_binding_red_case(root, target, refused):
    iso = isolated_bin(root)
    mutant = _feat50_mutant_between(
        '    feature_checkout_guard(verdict["rel"], target)\n',
        '    approval_guard(verdict["rel"], agent)\n', iso)
    muted = fire(root, target, hook=mutant)
    ok = refused.returncode == 2 and muted.returncode == 0 and "Traceback" not in muted.stderr
    return ("feature-checkout-red", ok,
            f"real={refused.returncode}, mutant={muted.returncode}: {muted.stderr}")


def _feat50_digest_fixture():
    root = fixture("schema_version: 1\nteams: []\n")
    worktree = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-D"), "FEAT-D")
    rel = ".harness/harness/features/FEAT-D-thing/runs/r1/digest.md"
    path = os.path.join(worktree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return root, path


def _feat50_write_text(path, content):
    with open(path, "w", encoding="utf-8") as digest_file:
        digest_file.write(content)


def _feat50_digest_clobber_case(root, path, prior):
    _feat50_write_text(path, prior)
    result = fire_write_payload(root, path, "wholly different digest\n")
    ok = (result.returncode == 2
          and "replace rather than extend" in result.stderr
          and "run directory of its own" in result.stderr)
    return ("digest-clobber", ok, f"{result.returncode}: {result.stderr}"), result


def _feat50_digest_append_case(root, path, prior):
    append = fire_write_payload(root, path, prior + "and more\n")
    _feat50_write_text(path, " \n")
    whitespace = fire_write_payload(root, path, "first digest\n")
    os.unlink(path)
    new_file = fire_write_payload(root, path, "first digest\n")
    ok = append.returncode == 0 and whitespace.returncode == 0 and new_file.returncode == 0
    detail = (f"append={append.returncode}, whitespace={whitespace.returncode}, "
              f"new={new_file.returncode}")
    return "digest-append", ok, detail


def _feat50_digest_unreadable_case(root, path):
    os.makedirs(path)
    result = fire_write_payload(root, path, "replacement\n")
    os.rmdir(path)
    ok = result.returncode == 2 and "cannot be read safely" in result.stderr
    return "digest-unreadable", ok, f"{result.returncode}: {result.stderr}"


def _feat50_digest_post_case(root, path, prior):
    _feat50_write_text(path, prior)
    result = fire_write_payload(root, path, "wholly different digest\n", "--post")
    ok = result.returncode == 0 and "recorded digest" not in result.stderr
    return "digest rule is PRE-Write-only", ok, f"{result.returncode}: {result.stderr}"


def _feat50_digest_red_case(root, path, clobber):
    iso = isolated_bin(root)
    mutant = _feat50_mutant_between(
        "def _rule_run_digest(rel, content, lines, shown, absolute_path):\n"
        "    if absolute_path is None:\n        return []\n    out = []\n",
        "    return out\n", iso)
    muted = fire_write_payload(root, path, "wholly different digest\n", hook=mutant)
    ok = clobber.returncode == 2 and muted.returncode == 0 and "Traceback" not in muted.stderr
    return ("digest-clobber-red", ok,
            f"real={clobber.returncode}, mutant={muted.returncode}: {muted.stderr}")


def _bug1124_state_fixture():
    root = fixture("schema_version: 1\nteams: []\n")
    worktree = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-S"), "FEAT-S")
    rel = ".harness/harness/features/FEAT-S-thing/runs/r1/state.yaml"
    path = os.path.join(worktree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return root, path


def _bug1124_collision_case(root, path):
    """Issue #1124: a slug reused for a DIFFERENT run's state.yaml is refused."""
    _feat50_write_text(path, "schema_version: 1\nrun_id: run-alpha\nstatus: building\n")
    result = fire_write_payload(root, path, "schema_version: 1\nrun_id: run-beta\nstatus: building\n")
    ok = (result.returncode == 2
          and "different run's state" in result.stderr
          and "run directory of its own" in result.stderr)
    return ("state-run-id-collision", ok, f"{result.returncode}: {result.stderr}"), result


def _bug1124_upsert_case(root, path):
    """The SAME run_id may be rewritten any number of times — the checkpoint upsert (DEC-154)."""
    _feat50_write_text(path, "schema_version: 1\nrun_id: run-alpha\nstatus: building\n")
    first = fire_write_payload(root, path, "schema_version: 1\nrun_id: run-alpha\nstatus: reviewing\n")
    second = fire_write_payload(root, path, "schema_version: 1\nrun_id: run-alpha\ncycles_used: 3\n")
    ok = first.returncode == 0 and second.returncode == 0
    return ("state-run-id-upsert-allowed", ok,
            f"first={first.returncode}:{first.stderr}, second={second.returncode}:{second.stderr}")


def _bug1124_no_run_id_case(root, path):
    """Issue #1106, gap (b): a prior file with no run_id used to be silently allowed through
    unchanged — the write could not be shown to be the same run, and "cannot verify" was
    treated as "allow". Now it is refused: the identity cannot be verified, so a Write that
    could silently replace the prior checkpoint is denied."""
    _feat50_write_text(path, "schema_version: 1\nstatus: building\n")
    result = fire_write_payload(root, path, "schema_version: 1\nrun_id: run-alpha\nstatus: building\n")
    ok = (result.returncode == 2
          and "no run_id" in result.stderr
          and "run directory of its own" in result.stderr)
    return ("state-no-prior-run-id-refused", ok, f"{result.returncode}: {result.stderr}")


def _bug1124_no_incoming_run_id_case(root, path):
    """The symmetric case: a prior WITH run_id, and an incoming write that carries none.
    Also refused — the incoming write cannot be shown to be an upsert of that run either."""
    _feat50_write_text(path, "schema_version: 1\nrun_id: run-alpha\nstatus: building\n")
    result = fire_write_payload(root, path, "schema_version: 1\nstatus: reviewing\n")
    ok = (result.returncode == 2
          and "carries no run_id" in result.stderr
          and "run directory of its own" in result.stderr)
    return ("state-no-incoming-run-id-refused", ok, f"{result.returncode}: {result.stderr}")


def _bug1124_prior_unparseable_case(root, path):
    """Issue #1106, gap (b): a prior that exists with content but is not valid YAML — a
    genuinely different failure mode from an UNREADABLE prior (permission denied, a
    directory) already covered by `_bug1124_unreadable_case`. Must also refuse."""
    _feat50_write_text(path, "status: [unterminated flow seq\n")
    result = fire_write_payload(root, path, "schema_version: 1\nrun_id: run-alpha\nstatus: building\n")
    ok = (result.returncode == 2
          and "does not parse" in result.stderr
          and "silently replace" in result.stderr)
    return ("state-prior-unparseable-refused", ok, f"{result.returncode}: {result.stderr}")


def _bug1124_new_file_case(root, path):
    # FEAT-104 D-11: this new checkpoint must satisfy the version floor so the
    # case continues to isolate run-id collision admission.
    result = fire_write_payload(root, path, "schema_version: 2\nrun_id: run-gamma\nstatus: building\n")
    ok = result.returncode == 0
    return ("state-new-file-allowed", ok, f"{result.returncode}: {result.stderr}")


def _bug1124_unreadable_case(root, path):
    """Code review finding: a prior state.yaml that lexists but cannot be OPENED (here, a
    directory sitting at the path) must deny, mirroring the sibling #1058 digest guard —
    not fail open by treating an unreadable prior as "nothing to compare"."""
    os.makedirs(path)
    result = fire_write_payload(root, path, "schema_version: 1\nrun_id: run-delta\n")
    os.rmdir(path)
    ok = result.returncode == 2 and "cannot be read safely" in result.stderr
    return ("state-unreadable-prior-denied", ok, f"{result.returncode}: {result.stderr}")


def _bug1124_red_case(root, path, collision):
    iso = isolated_bin(root)
    mutant = _feat50_mutant_between(
        "def _state_yaml_prior_refusal(doc, _version, rel, shown, absolute_path):\n"
        "    if absolute_path is None:\n        return []\n",
        "\n\ndef _state_yaml_prior_parse(", iso)
    muted = fire_write_payload(root, path,
                               "schema_version: 1\nrun_id: run-beta\nstatus: building\n",
                               hook=mutant)
    ok = collision.returncode == 2 and muted.returncode == 0 and "Traceback" not in muted.stderr
    return ("state-run-id-collision-red", ok,
            f"real={collision.returncode}, mutant={muted.returncode}: {muted.stderr}")


def _feat52_foreign_cwd_receipt_pair():
    workspace = tempfile.mkdtemp()
    root = fixture_fleet(
        """schema_version: 1
teams:
  - name: build
    members:
      - name: harness-documentor
        domain:
          - { path: .harness/*/features/*/runs/**, upsert: true }
""",
        ("schema: factory-fleet/1\n"
         f"workspace_root: {workspace}\n"
         "repos:\n"
         "  - name: acme/widget\n"
         "    default_branch: main\n"),
    )
    worktree = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-90"), "FEAT-90"
    )
    rel = ".harness/harness/features/FEAT-90-alpha/runs/r1/receipt.md"
    receipt = os.path.join(worktree, rel)
    product_cwd = os.path.join(workspace, "widget")
    os.makedirs(os.path.dirname(receipt), exist_ok=True)
    os.makedirs(product_cwd, exist_ok=True)

    allowed = fire(root, receipt, cwd=product_cwd)
    refused = fire(root, os.path.join(product_cwd, rel), cwd=product_cwd)
    return (
        "SC-15 PAIR: foreign product cwd allows its feature-worktree receipt and refuses its product twin",
        allowed.returncode == 0 and refused.returncode == 2,
        f"allow={allowed.returncode}: {allowed.stderr}; refuse={refused.returncode}: {refused.stderr}",
    )


def _feat50_binding_results():
    main, root, worktree, target, refused = _feat50_binding_case(
        "feature-checkout-main", FEAT50_FEATURE)
    short = _feat50_binding_case("feature-checkout-main short prefix", "FEAT-X")[0]
    return [
        main,
        short,
        _feat50_inside_case(root, worktree),
        _feat50_absent_case(),
        _feat50_binding_red_case(root, target, refused),
    ]


def _feat50_digest_results():
    digest_root, digest_path = _feat50_digest_fixture()
    prior = "recorded cycle-0 text\n"
    clobber_case, clobber = _feat50_digest_clobber_case(digest_root, digest_path, prior)
    return [
        clobber_case,
        _feat50_digest_append_case(digest_root, digest_path, prior),
        _feat50_digest_unreadable_case(digest_root, digest_path),
        _feat50_digest_post_case(digest_root, digest_path, prior),
        _feat50_digest_red_case(digest_root, digest_path, clobber),
    ]


def _bug1124_state_results():
    state_root, state_path = _bug1124_state_fixture()
    collision_case, collision = _bug1124_collision_case(state_root, state_path)
    return [
        collision_case,
        _bug1124_upsert_case(*_bug1124_state_fixture()),
        _bug1124_no_run_id_case(*_bug1124_state_fixture()),
        _bug1124_new_file_case(*_bug1124_state_fixture()),
        _bug1124_red_case(state_root, state_path, collision),
        _bug1124_unreadable_case(*_bug1124_state_fixture()),
        _bug1124_no_incoming_run_id_case(*_bug1124_state_fixture()),
        _bug1124_prior_unparseable_case(*_bug1124_state_fixture()),
    ]


def run_feat50_artifact_integrity():
    """Issues #1057/#1058: bind feature writes and preserve recorded digests."""
    results = (_feat50_binding_results() + _feat50_digest_results()
               + _bug1124_state_results() + [_feat52_foreign_cwd_receipt_pair()])
    return _report(results, "FEAT-50 artifact-integrity")


def _fire_digest_edit(root, path, old_s, new_s, replace_all=False):
    # NO agent_type, matching fire_write_payload's payload shape:
    # these cases test the SHAPE gate (DEC-180, domain-independent), not the domain
    # phase, and check-domain.py exempts a payload with no agent_type from the domain
    # phase entirely so the shape-only behaviour can be isolated.
    return _fire_edit(root, path, old_s, new_s, agent=None, replace_all=replace_all)


def _fire_path_only_edit(root, path):
    """The omp Edit shape: file_path only, no old_string/new_string to reconstruct from."""
    return _invoke(root, {"tool_name": "Edit", "tool_input": {"file_path": path}})


def _bug1106_edit_after(fixture_fn, prior, old_s, new_s):
    """Write `prior` into a fresh fixture, fire an agentless Edit; return (path, result)."""
    root, path = fixture_fn()
    _feat50_write_text(path, prior)
    return path, _fire_digest_edit(root, path, old_s, new_s)


def _bug1106_digest_edit_cases():
    # --- digest.md: a REPLACE-shaped Edit (old_string spans the whole prior text) must
    # be refused exactly like a Write that would replace it.
    prior = "recorded cycle-0 text\n"
    digest_path, r = _bug1106_edit_after(
        _feat50_digest_fixture, prior, prior, "wholly different digest\n")
    results = [("bug1106 Edit route: replacing a run's digest.md via Edit is REFUSED",
                r.returncode == 2 and "replace rather than extend" in r.stderr,
                f"exit {r.returncode}: {r.stderr.strip()[:250]}")]
    on_disk = open(digest_path, encoding="utf-8").read()
    results.append(("bug1106 Edit route: the refused digest Edit left the file untouched",
                    on_disk == prior, repr((prior, on_disk))))

    # --- digest.md: a genuine APPEND-shaped Edit (old_string is a true prefix, new_string
    # extends it) is allowed — this is not a blanket "no Edit on digest.md" rule.
    _, r = _bug1106_edit_after(_feat50_digest_fixture, prior, prior, prior + "and more\n")
    results.append(("bug1106 Edit route NEGATIVE CONTROL: a genuine append via Edit is "
                    "ALLOWED", r.returncode == 0, f"exit {r.returncode}: {r.stderr[:200]}"))
    return results


def _bug1106_state_edit_cases():
    # --- state.yaml: an Edit that changes run_id to a DIFFERENT run is refused exactly
    # like the equivalent Write.
    prior = "schema_version: 1\nrun_id: run-alpha\nstatus: building\n"
    state_path, r = _bug1106_edit_after(
        _bug1124_state_fixture, prior, "run_id: run-alpha", "run_id: run-beta")
    results = [("bug1106 Edit route: a state.yaml run_id collision via Edit is "
                "REFUSED",
                r.returncode == 2 and "different run's state" in r.stderr,
                f"exit {r.returncode}: {r.stderr.strip()[:250]}")]
    on_disk = open(state_path, encoding="utf-8").read()
    results.append(("bug1106 Edit route: the refused state.yaml Edit left the file "
                    "untouched", "run-alpha" in on_disk, on_disk))

    # --- state.yaml: the SAME run_id, a legitimate checkpoint upsert via Edit, is
    # allowed.
    _, r = _bug1106_edit_after(
        _bug1124_state_fixture, prior, "status: building", "status: reviewing")
    results.append(("bug1106 Edit route NEGATIVE CONTROL: a same-run_id checkpoint "
                    "upsert via Edit is ALLOWED",
                    r.returncode == 0, f"exit {r.returncode}: {r.stderr[:200]}"))
    return results


def _bug1106_fail_closed_cases():
    # --- An ambiguous or unmatched Edit payload cannot describe the candidate bytes.
    # Governed artifacts fail closed and route the caller to a whole-file Write rather
    # than assuming the editor will reject the operation before this hook matters.
    _, unmatched = _bug1106_edit_after(
        _bug1124_state_fixture, "schema_version: 1\nrun_id: run-alpha\nstatus: building\n",
        "no-such-text-in-file", "replacement")
    _, ambiguous = _bug1106_edit_after(
        _bug1124_state_fixture, "schema_version: 1\nrun_id: run-alpha\nstatus: x\nnote: x\n",
        "x", "y")
    return [
        (name, r.returncode == 2 and "Write the complete file instead" in r.stderr,
         f"exit {r.returncode}: {r.stderr[:200]}")
        for name, r in (
            ("bug1106 Edit route: an unmatched old_string fails closed", unmatched),
            ("bug1106 Edit route: a non-unique old_string fails closed", ambiguous),
        )
    ]


def _bug1106_unrelated_edit_case():
    # --- An Edit to an UNRELATED file (not digest.md/state.yaml) is completely
    # unaffected by this widening — the PRE route stays Write-only for everything else.
    other_root, other_path = _feat50_digest_fixture()
    other_path = other_path.replace("digest.md", "notes.md")
    _feat50_write_text(other_path, "some notes\n")
    r = _fire_digest_edit(other_root, other_path, "some notes", "different notes entirely")
    return ("bug1106 Edit route NEGATIVE CONTROL: an unrelated file's Edit is "
            "still unaffected (no PRE check runs at all for it)",
            r.returncode == 0, f"exit {r.returncode}: {r.stderr[:200]}")


def run_bug1106_edit_route_cases():
    """Issue #1106, gap (a): an Edit targeting a run's digest.md or state.yaml is now
    intercepted PRE-write, by reconstructing the full resulting content from the on-disk
    prior and old_string/new_string, then running it through the SAME content guards the
    Write route already uses (issue #1058's digest prefix test, issues #1124/#1106's
    state.yaml run-identity test)."""
    results = (_bug1106_digest_edit_cases() + _bug1106_state_edit_cases()
               + _bug1106_fail_closed_cases() + [_bug1106_unrelated_edit_case()])
    return _report(results, "bug1106 Edit-route")


def _bug1305_edit_append_result(prior, artifact):
    root, path = _feat50_digest_fixture()
    _feat50_write_text(path, prior)
    response = _fire_digest_edit(
        root, path, "  headline: recorded\n",
        "  headline: recorded\n" + artifact)
    return ("digest Edit append repair remains allowed",
            response.returncode == 0, response.stderr)


def _bug1305_edit_insertion_result(prior, artifact):
    root, path = _feat50_digest_fixture()
    _feat50_write_text(path, prior)
    response = _fire_digest_edit(
        root, path, "VERDICT: PASS\n", artifact + "VERDICT: PASS\n")
    return (
        "digest Edit insertion is refused with complete-block append route",
        response.returncode == 2
        and "complete corrected VERDICT / DIGEST / artifact block" in response.stderr,
        response.stderr,
    )


def _bug1619_complete_correction_result():
    invalid = """VERDICT: PASS
DIGEST:
  headline: simplify reader found a blocker
  team: simplify
  steps_run: 1
  cycles_used: 0
  members:
    - { step: reader, persona: code-reviewer, verdict: FAIL, headline: "reader blocker", files_touched: [] }
  must_fix: [reader blocker]
  branch: feat/example
  files_touched: []
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status: []
  adequacy_notes: []
  needs_approval: none
  severity_max: none
  matrix_ok: none
  coverage_gaps: []
  findings: []
  readers: []
artifact: .harness/harness/features/FEAT-D-thing/runs/r1/digest.md
"""
    corrected = invalid.replace("VERDICT: PASS", "VERDICT: FAIL", 1)
    # FEAT-1928: the durable record is prose followed by fenced YAML blocks; the last fenced
    # mapping is the record, so a correction is one more complete block after the first.
    recorded = "# lead assessment\n\n```yaml\n" + invalid + "```\n"
    combined = recorded + "\n```yaml\n" + corrected + "```\n"
    root, path = _feat50_digest_fixture()
    _feat50_write_text(path, recorded)
    response = fire_write_payload(root, path, combined)
    validation = subprocess.run(
        [VALIDATE_DIGEST, "harness-validator-lead"],
        input=combined, capture_output=True, text=True)
    return (
        "a complete corrected block repairs an invalid digest append-only",
        response.returncode == 0 and validation.returncode == 0,
        f"guard={response.returncode}: {response.stderr}; "
        f"validator={validation.returncode}: {validation.stdout}",
    )


def _bug1305_digest_write_result(name, prior, candidate, allowed, witness=False):
    root, path = _feat50_digest_fixture()
    _feat50_write_text(path, prior)
    if witness:
        _bug1305_write_marker(path)
    response = fire_write_payload(root, path, candidate)
    expected = 0 if allowed else 2
    return name, response.returncode == expected, response.stderr


def run_bug1305_digest_repair_cases():
    """BUG-1305/#1619: append-only preservation has an actionable repair route."""
    prior = "VERDICT: PASS\nDIGEST:\n  headline: recorded\n"
    artifact = "  artifact: notes/x.md\n"
    results = [
        _bug1305_edit_append_result(prior, artifact),
        _bug1305_edit_insertion_result(prior, artifact),
        _bug1619_complete_correction_result(),
        _bug1305_digest_write_result(
            "cross-run digest replacement remains refused",
            prior, "wholly different digest\n", False),
        _bug1305_digest_write_result(
            "digest Write append remains allowed",
            prior, prior + artifact, True),
        _bug1305_digest_write_result(
            "digest Write append remains allowed beside identity witness",
            prior, prior + artifact, True, witness=True),
    ]
    return _report(results, "BUG-1305 digest", "bug1305-digest", 300)


def run_bug1106_shared_pattern_consistency():
    """The digest.md/state.yaml patterns are respelled, not shared, between
    check-domain.py (whose shape-phase import of harness_boundary must stay ABSORBING —
    see the comment beside RE_STATE_YAML there) and harness_boundary.py (which
    bash-write-guard.py imports safely). Assert the two copies are byte-identical so this
    respelling cannot silently drift (issue #1106)."""
    with open(HOOK, encoding="utf-8") as f:
        cd_source = f.read()
    with open(os.path.join(HERE, "harness_boundary.py"), encoding="utf-8") as f:
        hb_source = f.read()

    def _pattern_literal(source, varname):
        marker = varname + " "
        idx = source.find("\n" + marker)
        if idx < 0:
            return None
        line = source[idx + 1:source.index("\n", idx + 1)]
        if "re.compile(r" not in line:
            return None
        start = line.index('r"') + 1
        end = line.index('"', start + 1)
        return line[start:end + 1]

    cd_digest = _pattern_literal(cd_source, "RE_RUN_DIGEST  ")
    hb_digest = _pattern_literal(hb_source, "RE_RUN_DIGEST =")
    cd_state = _pattern_literal(cd_source, "RE_STATE_YAML  ")
    hb_state = _pattern_literal(hb_source, "RE_STATE_YAML =")

    results = [
        ("bug1106: RE_RUN_DIGEST is found in both check-domain.py and harness_boundary.py",
         cd_digest is not None and hb_digest is not None,
         f"check-domain={cd_digest!r} harness_boundary={hb_digest!r}"),
        ("bug1106: RE_RUN_DIGEST's pattern text is byte-identical in both files",
         cd_digest == hb_digest, f"{cd_digest!r} != {hb_digest!r}"),
        ("bug1106: RE_STATE_YAML is found in both check-domain.py and harness_boundary.py",
         cd_state is not None and hb_state is not None,
         f"check-domain={cd_state!r} harness_boundary={hb_state!r}"),
        ("bug1106: RE_STATE_YAML's pattern text is byte-identical in both files",
         cd_state == hb_state, f"{cd_state!r} != {hb_state!r}"),
    ]
    return _report(results, "bug1106 pattern-consistency")


def _bug1305_marker_path(state_path):
    return os.path.join(os.path.dirname(state_path), ".run-identity.json")


def _bug1305_write_marker(state_path, run_id="A", run_uid=None):
    marker = {
        "run_id": run_id, "feature": "FEAT-S-thing", "squad": "eng",
        "host": "omp", "identity": "session", "run_uid": run_uid,
        "created_at": "2026-09-05T00:00:00+00:00",
    }
    with open(_bug1305_marker_path(state_path), "w", encoding="utf-8") as fh:
        json.dump(marker, fh)


def _bug1305_unverifiable_edit_result(name, response):
    refused = (
        response.returncode == 2
        and "run identity" in response.stderr
        and "witness" in response.stderr
        and "Write the complete file instead" in response.stderr
    )
    return name, refused, response.stderr


def _bug1305_absent_prior_edit_case():
    root, state = _bug1124_state_fixture()
    _bug1305_write_marker(state)
    response = _fire_digest_edit(
        root, state, "run_id: A", "run_id: B")
    return _bug1305_unverifiable_edit_result(
        "absent-prior Edit refuses unverifiable witness identity", response)


def _bug1305_unmatched_edit_case():
    root, state = _bug1124_state_fixture()
    _bug1305_write_marker(state)
    _feat50_write_text(
        state, "schema_version: 1\nrun_id: A\nfeature: FEAT-S-thing\n"
        "squad: eng\nhost: omp\n")
    response = _fire_digest_edit(
        root, state, "run_id: missing", "run_id: B")
    return _bug1305_unverifiable_edit_result(
        "unmatched state Edit refuses unverifiable witness identity", response)


def _bug1305_omp_edit_cases():
    root, state = _bug1124_state_fixture()
    _bug1305_write_marker(state)
    _feat50_write_text(
        state, "schema_version: 1\nrun_id: A\nfeature: FEAT-S-thing\n"
        "squad: eng\nhost: omp\nstatus: building\n")
    response = _fire_path_only_edit(root, state)
    refused = _bug1305_unverifiable_edit_result(
        "omp file-path-only state Edit fails closed", response)

    permitted = _fire_digest_edit(
        root, state, "status: building", "status: review")
    allowed = (
        "uniquely reconstructable state Edit remains allowed",
        permitted.returncode == 0,
        permitted.stderr,
    )
    return [refused, allowed]


def _bug1305_edit_reconstruction_cases():
    return [
        _bug1305_absent_prior_edit_case(),
        _bug1305_unmatched_edit_case(),
        *_bug1305_omp_edit_cases(),
    ]


def _bug1305_unreconstructable_artifact_cases(label, root, path, prior):
    absent = _fire_digest_edit(root, path, "missing", "replacement")
    _feat50_write_text(path, prior)
    unmatched = _fire_digest_edit(root, path, "missing", "replacement")
    omp_edit = _fire_path_only_edit(root, path)
    results = []
    for shape, response in (
        ("absent-prior", absent),
        ("unmatched", unmatched),
        ("omp file-path-only", omp_edit),
    ):
        allowed_route = "Write the complete file instead" in response.stderr
        results.append((
            f"{label} {shape} Edit fails closed",
            response.returncode == 2 and allowed_route,
            response.stderr,
        ))
    return results


def _bug1305_nonstate_edit_reconstruction_cases():
    digest_root, digest_path = _feat50_digest_fixture()
    results = _bug1305_unreconstructable_artifact_cases(
        "digest", digest_root, digest_path, "recorded digest\n")
    with tempfile.TemporaryDirectory() as handoff_root:
        _, handoff_path = _handoff_done_when_fixture(handoff_root)
        results.extend(_bug1305_unreconstructable_artifact_cases(
            "handoff", handoff_root, handoff_path,
            _handoff_text("Scope: done\nAuthority: plan-task:T-03.verify")))
    return results


def _bug1305_marker_foreign_refusals():
    root, state = _bug1124_state_fixture()
    _bug1305_write_marker(state)
    write = fire_write_payload(
        root, state,
        "schema_version: 1\nrun_id: B\nfeature: FEAT-S-thing\nsquad: eng\nhost: omp\n")

    root, state = _bug1124_state_fixture()
    _bug1305_write_marker(state)
    _feat50_write_text(
        state, "schema_version: 1\nrun_id: A\nfeature: FEAT-S-thing\nsquad: eng\nhost: omp\n")
    edit = _fire_digest_edit(root, state, "run_id: A", "run_id: B")
    return [
        ("foreign first Write is refused by witness", write.returncode == 2
         and "Issue 1305" in write.stderr and "A" in write.stderr
         and "B" in write.stderr, write.stderr),
        ("foreign Edit is refused by witness", edit.returncode == 2
         and "Issue 1305" in edit.stderr and "A" in edit.stderr
         and "B" in edit.stderr, edit.stderr),
    ]


def _bug1305_marker_witness_precedence():
    root, state = _bug1124_state_fixture()
    _bug1305_write_marker(state)
    _feat50_write_text(state, "{")
    unparseable = fire_write_payload(root, state, "schema_version: 1\nrun_id: B\n")

    root, state = _bug1124_state_fixture()
    _bug1305_write_marker(state)
    _feat50_write_text(state, "schema_version: 1\nrun_id: A\n")
    legacy = fire_write_payload(root, state, "schema_version: 1\nrun_id: B\n")
    return [
        ("witness outranks an unparseable prior", unparseable.returncode == 2
         and "Issue 1305" in unparseable.stderr
         and "does not parse" not in unparseable.stderr, unparseable.stderr),
        ("witness outranks legacy run_id ladder", legacy.returncode == 2
         and "Issue 1305" in legacy.stderr
         and "Issue 1124" not in legacy.stderr, legacy.stderr),
    ]


def _bug1305_marker_recovery_cases():
    results = []
    for label, prior in (("absent", None), ("zero-byte", "")):
        root, state = _bug1124_state_fixture()
        _bug1305_write_marker(state)
        if prior is not None:
            _feat50_write_text(state, prior)
        response = fire_write_payload(
            root, state,
            # "absent" creates a checkpoint and must satisfy the FEAT-104 floor;
            # "zero-byte" is an update, but sharing the value keeps the cases uniform.
            "schema_version: 2\nrun_id: A\nfeature: FEAT-S-thing\nsquad: eng\nhost: omp\n")
        results.append((
            f"recovering owner with {label} prior is allowed",
            response.returncode == 0, response.stderr))

    root, state = _bug1124_state_fixture()
    with open(_bug1305_marker_path(state), "w", encoding="utf-8") as fh:
        fh.write("{")
    response = fire_write_payload(root, state, "schema_version: 1\nrun_id: A\n")
    results.append((
        "unreadable witness fails closed", response.returncode == 2
        and "cannot be read" in response.stderr
        and "Issue 1305" in response.stderr, response.stderr))
    return results


def _bug1305_marker_file_protection():
    root, state = _bug1124_state_fixture()
    identity = _bug1305_marker_path(state)
    with open(identity, "w", encoding="utf-8") as fh:
        fh.write("{}\n")
    write = fire_write_payload(root, identity, '{"run_id": "forged"}\n')
    edit = _fire_digest_edit(root, identity, "{}", '{"run_id": "forged"}')
    unmatched_edit = _fire_digest_edit(
        root, identity, "not present", '{"run_id": "forged"}')
    # The checkpoint is new, so satisfy the version floor while this case
    # isolates run_uid legality.
    legal = fire_write_payload(
        root, state, "schema_version: 2\nrun_id: A\nrun_uid: U\n")
    os.unlink(identity)
    create = fire_write_payload(root, identity, '{"run_id": "forged"}\n')
    create_edit = _fire_digest_edit(
        root, identity, "not present", '{"run_id": "forged"}')
    return [
        ("Write of existing witness is refused", write.returncode == 2
         and "identity witness" in write.stderr, write.stderr),
        ("Edit of existing witness is refused", edit.returncode == 2
         and "identity witness" in edit.stderr, edit.stderr),
        ("unmatched Edit of existing witness is refused",
         unmatched_edit.returncode == 2
         and "identity witness" in unmatched_edit.stderr, unmatched_edit.stderr),
        ("run_uid is a legal checkpoint key beside identity witness",
         legal.returncode == 0, legal.stderr),
        ("Write creating false witness is refused", create.returncode == 2
         and "identity witness" in create.stderr, create.stderr),
        ("Edit creating false witness is refused", create_edit.returncode == 2
         and "identity witness" in create_edit.stderr, create_edit.stderr),
    ]


def _post_write(root, state):
    return fire_post(root, {
        "tool_name": "Write", "hook_event_name": "PostToolUse",
        "tool_input": {"file_path": state},
    })


def _read_marker(state):
    marker_path = _bug1305_marker_path(state)
    return open(marker_path, "rb").read() if os.path.isfile(marker_path) else b""


def _bug1305_post_landing(root, state):
    response = _post_write(root, state)
    after_first = open(state, "rb").read()
    marker_first = _read_marker(state)
    parsed = yaml.safe_load(after_first.decode("utf-8"))
    marker_doc = json.loads(marker_first) if marker_first else {}
    uid = parsed.get("run_uid") if isinstance(parsed, dict) else None
    return response, after_first, marker_first, marker_doc, uid


def _bug1305_marker_post_mint_cases():
    root, state = _bug1124_state_fixture()
    landed = "schema_version: 1\nrun_id: A\nfeature: FEAT-S-thing\nsquad: eng\nhost: omp\n"
    _feat50_write_text(state, landed)
    response, after_first, marker_first, marker_doc, uid = _bug1305_post_landing(root, state)
    _post_write(root, state)
    marker_second = _read_marker(state)
    return [
        ("POST mints uid and matching witness", response.returncode == 0
         and re.fullmatch(r"[0-9a-f]{32}", str(uid or ""))
         and marker_doc.get("run_uid") == uid, response.stderr),
        ("second POST is byte stable", open(state, "rb").read() == after_first
         and marker_second == marker_first and bool(marker_first), ""),
    ]


def _bug1305_marker_post_preservation_cases():
    root, state = _bug1124_state_fixture()
    explicit = "schema_version: 1\nrun_id: A\nrun_uid: fixed\n"
    _feat50_write_text(state, explicit)
    before = open(state, "rb").read()
    _post_write(root, state)
    preserved = open(state, "rb").read() == before

    root, state = _bug1124_state_fixture()
    _feat50_write_text(state, "{")
    _post_write(root, state)
    malformed = (
        open(state, encoding="utf-8").read() == "{"
        and not os.path.exists(_bug1305_marker_path(state)))
    return [
        ("POST preserves supplied uid bytes", preserved, ""),
        ("POST leaves malformed checkpoint untouched", malformed, ""),
    ]


def run_bug1305_marker_cases():
    """BUG-1305 SC-01/10: guard, seed-field precedence, and POST minting."""
    results = (
        _bug1305_edit_reconstruction_cases()
        + _bug1305_nonstate_edit_reconstruction_cases()
        + _bug1305_marker_foreign_refusals()
        + _bug1305_marker_witness_precedence()
        + _bug1305_marker_recovery_cases()
        + _bug1305_marker_file_protection()
        + _bug1305_marker_post_mint_cases()
        + _bug1305_marker_post_preservation_cases()
    )
    return _report(results, "BUG-1305 marker", "bug1305", 300)


def _bug1305_identity_doc(run_id="A", run_uid=None):
    text = (
        f"schema_version: 1\nrun_id: {run_id}\nfeature: FEAT-S-thing\n"
        "squad: eng\nhost: omp\nstatus: building\n")
    if run_uid is not None:
        text += f"run_uid: {run_uid}\n"
    return text


def _bug1305_identity_write(prior, incoming, marker=False, session_id=None):
    root, state = _bug1124_state_fixture()
    if prior is not None:
        _feat50_write_text(state, prior)
    if marker:
        _bug1305_write_marker(state, run_uid="U1")
    extra = {"session_id": session_id} if session_id is not None else None
    return fire_write_payload(root, state, incoming, extra=extra)


def _bug1305_identity_edit(new_string=""):
    root, state = _bug1124_state_fixture()
    _feat50_write_text(state, _bug1305_identity_doc(run_uid="U1"))
    return _fire_digest_edit(root, state, "run_uid: U1\n", new_string)


def _refused(response, present, absent=()):
    """Exit 2, every `present` text in stderr and no `absent` text."""
    stderr = response.stderr
    return (response.returncode == 2 and all(text in stderr for text in present)
            and not any(text in stderr for text in absent))


def _bug1305_identity_refusal_cases():
    prior = _bug1305_identity_doc(run_uid="U1")
    missing = _bug1305_identity_write(prior, _bug1305_identity_doc())
    edit = _bug1305_identity_edit()
    different_edit = _bug1305_identity_edit("run_uid: U2\n")
    different = _bug1305_identity_write(
        prior, _bug1305_identity_doc(run_uid="U2"))
    precedence = _bug1305_identity_write(
        prior, _bug1305_identity_doc(run_id="B", run_uid="U1"), marker=True)
    no_field = ("field disagreement",)
    return [
        ("modal collision Write omitting uid is refused",
         _refused(missing, ("U1", "run identity"), no_field), missing.stderr),
        ("modal collision Edit removing uid is refused",
         _refused(edit, ("U1", "run identity"), no_field), edit.stderr),
        ("different minted uid is refused",
         _refused(different, ("U1", "U2")), different.stderr),
        ("different minted uid Edit is refused",
         _refused(different_edit, ("U1", "U2")), different_edit.stderr),
        ("run_id disagreement keeps Issue 1124 precedence",
         _refused(precedence, ("Issue #1124",), ("Issue 1305",)), precedence.stderr),
    ]


def _bug1305_identity_allow_cases():
    prior = _bug1305_identity_doc(run_uid="U1")
    incoming = _bug1305_identity_doc(run_uid="U1")
    resumed = _bug1305_identity_write(prior, incoming, session_id="S2")
    # D-01 forbids session-keyed ownership: this same-uid S2 update catches it.
    absent = _bug1305_identity_write(
        None,
        # `prior=None` creates a checkpoint; the helper remains version 1 for
        # the legacy update-path cases below.
        _bug1305_identity_doc().replace(
            "schema_version: 1", "schema_version: 2", 1),
        marker=True)
    zeroed = _bug1305_identity_write(
        "", _bug1305_identity_doc(), marker=True)
    legacy = _bug1305_identity_doc()
    legacy_same = _bug1305_identity_write(legacy, legacy)
    legacy_new = _bug1305_identity_write(
        legacy, _bug1305_identity_doc(run_uid="U2"))
    return [
        ("DEC-154 resumed owner with same uid remains allowed across sessions",
         resumed.returncode == 0, resumed.stderr),
        ("recovering owner with absent checkpoint remains allowed",
         absent.returncode == 0, absent.stderr),
        ("recovering owner with zero-byte checkpoint remains allowed",
         zeroed.returncode == 0, zeroed.stderr),
        ("legacy checkpoint without uid remains allowed",
         legacy_same.returncode == 0, legacy_same.stderr),
        ("legacy checkpoint accepts incoming uid",
         legacy_new.returncode == 0, legacy_new.stderr),
    ]


def run_bug1305_identity_cases():
    """BUG-1305 SC-01: prior checkpoint uid owns resumed-write admission."""
    results = _bug1305_identity_refusal_cases() + _bug1305_identity_allow_cases()
    return _report(results, "BUG-1305 identity", "bug1305-identity", 300)


def run_2056_main_session_feature_checkout():
    """#2056: the MAIN SESSION's feature-artifact write is bound to the feature's worktree too.
    FEAT-01-kaya-platform's feature.json was written into the main checkout by the main session
    while its planning worktree held the live copy; the governed-only guard never saw it."""
    feature = "FEAT-9-fleet-thing"
    rel = f".harness/product-a/features/{feature}/BRIEF.md"
    root = fixture("schema_version: 1\nteams: []\n")
    worktree = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "harness", feature), feature)

    def main_write(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return fire_write_payload(root, path, "{}")

    in_main = main_write(os.path.join(root, rel))
    in_worktree = main_write(os.path.join(worktree, rel))
    other = main_write(os.path.join(root, ".harness", "harness", "docs", "note.md"))
    results = [
        ("main session: a feature artifact in the main checkout is refused, naming the worktree",
         in_main.returncode == 2 and worktree in in_main.stderr, in_main.stderr),
        ("main session: the same artifact inside the feature's worktree is allowed",
         in_worktree.returncode == 0, in_worktree.stderr),
        ("main session: a non-feature path in the main checkout is untouched",
         other.returncode == 0, other.stderr),
    ]
    return _report(results, None, "2056", 240)


def run_bug151_selfcheck_cases():
    """BUG-151: the aggregation safeguard must fire exactly on a zeroness disagreement
    between printed column-0 FAIL lines and a block's returned total (D-01), and must
    tolerate any disagreement in COUNT once both sides are already non-zero.
    """
    cases = [
        ("printed-fail-zero-total", "FAIL  x\n", 0, True),
        ("printed-ok-zero-total", "ok    x\n", 0, False),
        ("printed-fail-nonzero-total", "FAIL  x\n", 1, False),
        ("printed-ok-nonzero-total", "ok    x\n", 1, True),
        ("indented-fail-does-not-count", "ok    x\n      | FAIL inside a detail line\n", 0, False),
        ("two-printed-one-counted-agrees-on-zeroness", "FAIL  x\nFAIL  y\n", 1, False),
    ]
    fails = 0
    for name, captured, total, expect_diagnostic in cases:
        try:
            verdict = _aggregation_verdict(name, captured, total)
        except Exception as exc:
            fails += 1
            print(f"FAIL  [bug151-selfcheck] {name}\n      | raised {exc!r}")
            continue
        got_diagnostic = verdict is not None
        if got_diagnostic == expect_diagnostic:
            print(f"ok    [bug151-selfcheck] {name}")
        else:
            fails += 1
            detail = str(verdict)[:120] if verdict is not None else "None"
            print(f"FAIL  [bug151-selfcheck] {name}\n      | verdict={detail}")

    # Binds the safeguard to the REAL discovery-loop seam: a locally-defined,
    # non-discoverable fake block (never module-level, never "run_"-prefixed)
    # prints a column-0 FAIL line but returns 0 -- BUG-151's exact original
    # defect shape -- and is run through _run_block_captured(), the same
    # helper main()'s discovery loop calls. If the tee/redirect_stdout wrap
    # inside that helper is ever removed, this fake block's printed FAIL is
    # silently absorbed and the assertion below goes RED.
    def _fake_fail_block():
        print("FAIL  fake-block-prints-fail-returns-zero")
        return 0

    wiring_name = "wiring-seam-catches-print-fail-return-zero"
    passthrough = io.StringIO()
    try:
        _, wiring_verdict = _run_block_captured(_fake_fail_block, "fake-block", stream=passthrough)
    except Exception as exc:
        fails += 1
        print(f"FAIL  [bug151-selfcheck] {wiring_name}\n      | raised {exc!r}")
    else:
        if wiring_verdict is not None:
            print(f"ok    [bug151-selfcheck] {wiring_name}")
        else:
            fails += 1
            print(f"FAIL  [bug151-selfcheck] {wiring_name}\n      | verdict=None (seam failed to capture)")
    return fails


def main():
    return drive(globals())


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
