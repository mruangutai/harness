#!/usr/bin/env python3
"""Validate an agent's digest OBJECT: its persona schema, then the semantic gates.

FEAT-1928: every harness agent returns its digest as an object `{VERDICT, DIGEST,
artifact}` through YieldTool. The STRUCTURAL contract — required fields, types, exact
enums, list-entry shapes, the closed key set and the `none`/`n/a` spelling — is one JSON
Schema per persona under bin/digest-schemas/, applied by digest_schema.py. This file
parses no digest text. What stays here is what a schema cannot say: the VERDICT-bound
gates (a declined or failed gate beside PASS), the mission pins, the dev receipt, the
review binding and the mechanical code grade, the qa kind policy and matrix floor, the
lead roll-up, the claim registry errand, the #919 suite re-run and, for a lead, the one
sanctioned append of the validated object to its durable digest.md (SC-07, DEC-208).

Never guess a verdict: silent misrouting is worse than a halt. An LLM reader charitably
normalizes `severity_max: medium` or `must-fix`, so drift is refused here, by name.

Usage:  validate-digest.py <persona> [file]   (reads stdin if no file)
        validate-digest.py --hook              (yield hook; exit 2 rejects)

CLI input is one JSON object. Content that is not one is read as a durable digest.md
and its last fenced mapping (digest_record.py) is validated against the same live
schema — the path feature-record.py close-run takes. Exit 0 = valid; exit 1 = contract
violation (reasons on stdout). Hook mode validates the payload's `digest_object`, the
raw `data` of the yield, and rejects anything that is not a mapping.
"""
import sys, re, os, subprocess

# Same directory as this script; sys.path[0] is that directory under `python3 <path>`.
# The placeholder vocabulary lives there so INV-6 and this check cannot drift (issue #16).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness_boundary
import harness_yaml
import artifact_accessors
import amendment_contract
import digest_record
import digest_schema
from code_grade import classify, commit_oid, gated_set
from gate_policy import GatePolicyError, evaluate_review, load_policy

SEV = ["none", "low", "med", "high", "critical"]

# The one instruction a return that is not an object gets, in hook and CLI alike.
OBJECT_REQUIRED = ("return the digest as an object: yield({data: {VERDICT, DIGEST, artifact}})"
                   " — a string, null, absent or wrapped `data` carries no digest.")


def _placeholder(val):
    """The DEC-121 did-nothing spelling (`none`/`null`/`n/a`) the schemas accept as `unset`."""
    return isinstance(val, str) and val.strip().lower() in harness_yaml.PLACEHOLDER_UNSET

# ...but declining to REPORT a gate is not the same as passing it. This is keyed by
# PERSONA as well as field, because the same field means different things by role
# and a field-only rule gets it wrong:
#
#   dev      suite: n/a + PASS  -> REJECTED. It refused or could not run the tests;
#                                  the Iron Law says no production code without a
#                                  passing test, so PASS is unearned.
#   qa       suite/matrix_ok n/a + PASS -> REJECTED. The project's only blocking
#                                  gate did not run. This is the audit's worst row.
#   dev-ops  suite: n/a + PASS  -> ALLOWED. `test_matrix` maps config/scaffolding/
#                                  docs to [] (DEC-100), so "no tests apply" is the
#                                  correct outcome, not a dodge.
#   reviewer severity_max n/a + PASS -> ALLOWED. A ui-reviewer on a non-UI diff
#                                  reviewed nothing and blocks nothing.
#
# So: only the roles whose PASS is *earned by the gate* are bound by it.
#
# FEAT-07 added `task_verify` and with it a SECOND axis, so the exemption is no
# longer "this persona is exempt" but "this persona is exempt from THIS field by
# THIS mechanism". Both axes, stated rather than left to be rediscovered:
#
#   PER FIELD.     dev-ops `suite: n/a` + PASS stays ALLOWED (above), while
#                  dev-ops `task_verify: n/a` + PASS is REJECTED. Every PLAN task
#                  carries a `verify:`, so where a return DECLARES a task, `n/a`
#                  means refused or blocked. No task declared is CONDITIONAL, below.
#   PER MECHANISM. This dict gates only the DECLINED value (`n/a`). Reporting an
#                  outright FAILURE is the separate GATE_FAIL_VALUES table below.
#                  `dev-ops` is absent from `suite` in BOTH, so dev-ops
#                  `suite: fail` + PASS stays accepted — deliberate (D-03), and
#                  recorded as a residue in BRIEF `## Verification gaps`.
GATE_FIELDS = {"dev": {"suite", "task_verify"}, "qa": {"suite", "matrix_ok"},
               "dev-ops": {"task_verify"}}

# ...and declining to report is not the same as REPORTING A FAILURE. Measured at
# 3bfedc9, four rows were accepted that should not have been: dev `suite: fail`,
# qa `suite: fail` and qa `matrix_ok: false`, each alongside `VERDICT: PASS`, all
# returning `digest ok` exit 0. Cause: the GATE_FIELDS check below is nested INSIDE
# the `val in PLACEHOLDER_UNSET` branch, so it can only ever see a placeholder.
#
# Keyed persona -> field -> the value that counts as FAILURE for that field, NOT a
# set of field names, because the failing values differ in TYPE: `suite`/`task_verify`
# fail as the STRING "fail" while `matrix_ok` fails as the BOOLEAN False. A
# string-keyed table would silently never fire on matrix_ok.
#
# The fourth row stays open on purpose: `dev-ops` carries `task_verify` only and must
# NOT gain `suite` (D-03), so dev-ops `suite: fail` + PASS remains accepted.
GATE_FAIL_VALUES = {"dev": {"suite": "fail", "task_verify": "fail"},
                    "qa": {"suite": "fail", "matrix_ok": False},
                    "dev-ops": {"task_verify": "fail"}}

# A field whose obligation is GOVERNED by another field. A dispatch carrying no PLAN
# task has no `verify:` command, so `task_verify` cannot be required of it; `task` is
# what declares which case a return is. Chosen over a bare `no-task` enum value
# (D-07) because `task: none` is a task-id-shaped string that the lead's
# dispatch-carries-the-T-NN-id rule (T-05) gives a cross-reference to.
CONDITIONAL = {"task_verify": "task"}

# A field whose obligation is lifted by what the return BOTH DECLARED and DID.
# An ANALYSIS dispatch -- read this, report that -- writes no production code, so the
# Iron Law binds on nothing: there is no code owed a passing test, and `suite` has no
# gate to decline. Before this, such a return had NO truthful digest. MEASURED
# 2026-08-26: three of four member runs lost their report body to the re-prompt, and
# TWO agents reasoned themselves into a fabricated `suite: pass` to satisfy the schema.
# A schema that teaches agents to misreport the record is worse than no schema.
#
# BOTH CONDITIONS, NEVER ONE. Each closes the other's hole, and both holes were real:
#
#   `task: none` alone       a CLAIM about the dispatch. A return can write it and
#                            still edit ten files, and the Iron Law would be bypassed
#                            on code that exists.
#   `files_touched: []` alone a dev handed a REAL task that REFUSED it also touches
#                            nothing, and its PASS is unearned. The case
#                            "suite: n/a with VERDICT PASS is a fail-open" pins that
#                            exact return -- `task: T-01`, `files_touched: []` -- and
#                            it MUST stay rejected.
#
# Only the pair separates "had nothing to test" from "declined to test".
NOTHING_TO_GATE = {"dev": {"suite"}}

# A field whose obligation is lifted by the MISSION the dispatch carries, and the one
# value it must then hold. Feature-close distillation (DEC-145) runs after the merge:
# the readers judge Expertise candidates, review no diff and run no suite. Under the
# build/validate contract two of them had no truthful return (#1855, measured on
# FEAT-61): qa could not PASS without `suite: pass` — which then fired the #919 rerun
# on a suite the dispatch forbade — and the code-reviewer could not bind `code_grade`
# to a review_sha that is already an ancestor of the default branch, so it forged a
# review note to satisfy the binding.
#
# The mission rides in the DISPATCH (`HARNESS-MISSION: distill`, forwarded by the host
# as `harness_mission`) exactly as the review pin does (#1677): the one text the
# persona does not author. The value is PINNED, not merely released: a gate field on a
# mission with no gate is decoration, and `suite: pass` beside Expertise edits is the
# fabricated-record shape this file exists to refuse. Any mission not listed here
# changes nothing — fail closed.
MISSION_UNGATED = {"distill": {"qa": {"suite": "n/a", "matrix_ok": "n/a"},
                               "reviewer": {"code_grade": "n_a", "reviewed": "none"}}}


def _mission_pinned_value(field, persona, mission):
    """The value `field` MUST hold on this mission, or None when the gate binds."""
    return MISSION_UNGATED.get(mission, {}).get(persona, {}).get(field)


def _nothing_to_gate(field, persona, seen):
    """True when this return declared no task AND changed no file, so `field` would
    gate work that does not exist.

    FAILS CLOSED on anything unexpected -- a missing, unparsed or non-list
    `files_touched`, or any `task` value other than the literal `none`, leaves the
    gate BINDING. The default in the `task` read is load-bearing for the same reason
    `_unbound`'s is: `str(None).lower()` is `"none"` in Python, so a MISSING `task`
    written without it would switch the requirement off.
    """
    if field not in NOTHING_TO_GATE.get(persona, ()):
        return False
    if str(seen.get("task", "")).strip().lower() != "none":
        return False
    touched = seen.get("files_touched")
    return isinstance(touched, list) and not touched

def _unbound(field, seen):
    """True when `field`'s governor declares this dispatch carries no PLAN task.

    The `""` default is LOAD-BEARING: `str(None).lower()` is `"none"` in Python, so
    `seen.get(gov)` written without it would make a MISSING `task` switch the
    requirement off — the conditional mechanism failing open in its own first line.
    Fail closed: no governor value, or any value other than `none`, means it BINDS.
    """
    gov = CONDITIONAL.get(field)
    if gov is None:
        return False
    return str(seen.get(gov, "")).strip().lower() == "none"


def _amendments_errors(seen):
    """BUG-1716 SC-01: the eng-lead schema closes each `amendments` entry's keys and types;
    amendment_contract adds the rules it shares with plan-merge.py record-amendments (legal
    plan anchors in `files`), so the return and the ledger writer cannot drift."""
    entries = seen.get("amendments")
    if not isinstance(entries, list):
        return []
    return [message for index, entry in enumerate(entries) if isinstance(entry, dict)
            for message in amendment_contract.entry_errors(entry, index)]


def review_config_path(config_path=None):
    """Resolve the gate config once, with a fixture override for tests."""
    if config_path is not None:
        return config_path
    root = harness_boundary.resolve_root(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, ".harness", "harness.json")
ALIAS = {
    "harness-pm": "pm", "harness-qa": "qa", "harness-documentor": "documentor",
    "harness-dev-ops": "dev-ops", "harness-visual-designer": "visual-designer",
    "harness-frontend-dev": "dev", "harness-backend-dev": "dev",
    "harness-ai-dev": "dev", "harness-data-engineer": "dev",
    "harness-code-reviewer": "reviewer", "harness-security-reviewer": "reviewer",
    "harness-ui-reviewer": "reviewer",
    "harness-product-lead": "lead", "harness-eng-lead": "lead",
    "harness-validator-lead": "lead",
    "harness-orchestrator": "orchestrator",
    # #1895: a run the main session built directly (DEC-174 `run-start --agent main-session`)
    # carries the DEV contract -- the main session wrote the diff and owns the same task /
    # task_verify / suite receipt -- so the composed close-run can validate its digest.
    "main-session": "dev",
}

def norm(p):
    return ALIAS.get(p, ALIAS.get("harness-" + p, p))


def _repo_root_for_feature(feature_dir):
    """The checkout root that owns `feature_dir`.

    A feature directory is always `<root>/.harness/<repo>/features/<FEAT>`, so its root
    is four levels up. THIS IS THE ONE REPOSITORY BASIS every mechanical operation in
    this module uses: the default-branch lookup, the merge base, every commit
    resolution, the canonical diff and `gated_set()` all receive it explicitly, by
    `git -C` or as `commit_oid`'s `repo_root`. BUG-1081: deriving any of them from
    ambient cwd or from this file's installed location gave the grade a different
    repository from the one the review pin belongs to — two bases, not one.
    """
    return os.path.realpath(os.path.join(feature_dir, "..", "..", "..", ".."))


def resolve_reviewed_commit(root, revision):
    """Resolve an untrusted review revision to a commit OID in `root`, or None.

    `root` is the checkout that owns the feature under review
    (`_repo_root_for_feature`) — never the process cwd. `commit_oid` refuses an
    option-like revision before Git is ever invoked.
    """
    try:
        return commit_oid(root, revision).encode()
    except ValueError:
        return None


def reviewed_python_change(root, reviewed):
    """Return whether the review range changes Python, or a blocking range error."""
    if not isinstance(reviewed, str) or reviewed.count("..") != 1:
        return None, "reviewed range must name exactly one base..head range."
    base, head = (part.strip() for part in reviewed.split(".."))
    if not base or not head:
        return None, "reviewed range must name non-empty base and head revisions."
    base_oid = resolve_reviewed_commit(root, base)
    head_oid = resolve_reviewed_commit(root, head)
    if base_oid is None or head_oid is None:
        return None, "reviewed range could not be resolved to commit revisions."
    result = subprocess.run(
        ["git", "-C", root, "diff", "--name-only", "-z", base_oid, head_oid, "--"],
        capture_output=True,
    )
    if result.returncode:
        return None, "reviewed range could not be diffed for code-grade enforcement."
    return any(path.endswith(b".py") for path in result.stdout.split(b"\0") if path), None


# BUG-1081: a `code_grade` claim is a CLAIM. FEAT-43 (SEC-01) bound the range a review
# reports to the range the system of record says was reviewed, and wave 4 stopped the
# digest choosing the base for the `n_a` decision — but for `pass`, `fail` and `grade_2`
# nothing ever RAN the grader. A review therefore passed when `code-grade.py` was
# skipped, crashed, or reported a blocking result as a clean one, which is issue #1081.
#
# What changes here: the mechanical result is COMPUTED, for every ordinary code review,
# over `merge-base(<default branch>, review_sha)..review_sha` — a range the REPOSITORY
# derives with no digest input — and the digest's enum is REJECTED when it disagrees.
# The reviewer keeps every judgement that is judgement: findings, `must_fix`, severity,
# grade-2 reasons and the review policy, none of which this touches.
#
# The digest's own `reviewed` field is still validated (shape, and both revisions
# resolvable — still catching a malformed or option-like/injection revision) and its
# HEAD is still bound to `review_sha`. Its RESULT still decides nothing: Q8's ruling
# that "the digest's base becomes a reported value that is cross-checked, never an
# input that decides" is unchanged, and now holds for all four enum values rather than
# for `n_a` alone.
#
# Availability is deliberately traded for enforcement (D-05). FEAT-43 carved `pass`,
# `fail` and `grade_2` OUT of base derivation so an unresolvable default branch could
# not brick reviewer validation generally; that carve-out is exactly the bypass, because
# a checkout that cannot derive the repository-owned range cannot prove ANY mechanical
# result. Every derivation or grading failure now REFUSES the digest and names the
# repair. Reviews already require `origin/main` for the reviewer's own command, so the
# honest response is to repair `origin/HEAD` or the review pin and rerun.
_GRADE_PREFIX = "code_grade cannot be verified: "

CODE_GRADE_VALUES = {"pass", "fail", "grade_2", "n_a"}


def _git_line_or_none(root, *args):
    """One stripped line of `git -C root <args>`, or None on any failure — a missing
    ref, a non-zero exit, or `git` unavailable. Addressed with `-C` so every lookup in
    this module resolves against the checkout that owns the feature under review."""
    try:
        result = subprocess.run(["git", "-C", root, *args],
                                text=True, capture_output=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode:
        return None
    return result.stdout.strip() or None


def _default_branch_or_none(root):
    """`root`'s default branch — `origin/HEAD`'s target, e.g.
    `refs/remotes/origin/main` — or None when it cannot be resolved: no such
    remote-tracking ref, a checkout that never set one, or `git` unavailable.
    `origin/HEAD` is set once, at clone time, by whoever created the checkout — never a
    value a digest or a review can name."""
    return _git_line_or_none(root, "symbolic-ref", "-q", "refs/remotes/origin/HEAD")


def _merge_base_or_none(root, ref_a, ref_b):
    """`git -C root merge-base ref_a ref_b`, or None on any failure — no common
    ancestor, an unresolvable ref, or `git` unavailable."""
    return _git_line_or_none(root, "merge-base", ref_a, ref_b)


def _canonical_review_range(root, review_sha):
    """The range the REPOSITORY owns for this review, as `(base_oid, head_oid, error)`.

    `merge-base(<default branch>, review_sha)..review_sha` — never a range a digest
    names, because a digest-chosen base decides which functions get graded. FAILS
    CLOSED on four narrow conditions, each with its own repair: an unresolvable default
    branch, a `review_sha` that does not resolve, no merge base, and a DEGENERATE range
    (`review_sha` already an ancestor of the default branch), which is empty by
    construction and is zero evidence that nothing changed rather than proof that it
    did not. None of the four ever returns a result.
    """
    default_ref = _default_branch_or_none(root)
    if default_ref is None:
        return None, None, (_GRADE_PREFIX + "this checkout's default branch "
                            "(origin/HEAD) could not be resolved, so the range the "
                            "repository reviews cannot be derived — repair "
                            "origin/HEAD in this checkout and rerun.")
    head_oid = resolve_reviewed_commit(root, review_sha)
    if head_oid is None:
        return None, None, (_GRADE_PREFIX + f"this feature's recorded review_sha "
                            f"({review_sha!r}) does not resolve to a commit — re-pin "
                            f"review_sha in feature.json and rerun.")
    head_oid = head_oid.decode()
    base_oid = _merge_base_or_none(root, default_ref, head_oid)
    if base_oid is None:
        return None, None, (_GRADE_PREFIX + "no merge base between the default branch "
                            "and review_sha could be computed, so the range the "
                            "repository reviews cannot be derived — fetch the default "
                            "branch into this checkout and rerun.")
    if base_oid == head_oid:
        return None, None, (_GRADE_PREFIX + f"review_sha ({review_sha}) is already an "
                            f"ancestor of the default branch, so the derived review "
                            f"range is empty BY CONSTRUCTION — that is zero evidence "
                            f"nothing changed. Re-pin review_sha at the reviewed work "
                            f"and rerun.")
    return base_oid, head_oid, None


def _load_test_kinds(root):
    """`root`'s own `.harness/harness.json` `test_kinds` policy, as
    `(test_kinds, error)`.

    Read from the checkout under review, never from `review_config_path()`: the review
    policy and the grade bars are different configuration with different owners, and the
    bars must describe the repository actually being graded. A missing or empty policy
    is a named refusal, never an implicit production bar.
    """
    path = os.path.join(root, ".harness", "harness.json")
    try:
        doc = artifact_accessors.load_harness_json(path)
    except artifact_accessors.ArtifactAccessError as exc:
        return None, (_GRADE_PREFIX + f"{path} could not be read ({exc}), so this "
                      f"checkout's grade bars are unknown — repair harness.json "
                      f"and rerun.")
    kinds = doc.get("test_kinds") if isinstance(doc, dict) else None
    if not isinstance(kinds, dict) or not kinds:
        return None, (_GRADE_PREFIX + f"{path} carries no test_kinds policy, so a "
                      f"production path cannot be told from a test path — repair "
                      f"harness.json and rerun.")
    return kinds, None


# The three checks below replace prose that only the consuming LLM enforced (consumer
# audit, 2026-09-18). Each is a predicate over data the repository owns — the git log at
# the pin, the working tree at return, harness.json's test_kinds — and each REFUSES only
# a positive finding: when git or the policy cannot be read the check says nothing, because
# the grade enforcement above already refuses that checkout with its own repair.

HUMAN_COMMIT_MARK = "[harness:human]"


def _human_commits_in_range(root, base_oid, head_oid):
    """Full OIDs of `[harness:human]` commits in `base..head`, or None when git cannot say."""
    try:
        result = subprocess.run(
            ["git", "-C", root, "log", "--format=%H", "--fixed-strings",
             "--grep=" + HUMAN_COMMIT_MARK, f"{base_oid}..{head_oid}"],
            text=True, capture_output=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode:
        return None
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _prefix_matches(short, full_oids):
    return bool(short) and any(oid.startswith(short) for oid in full_oids)


def _human_commit_disagreement(actual, claimed):
    """`(unreported, not_in_range)`: human commits the digest omits, and claimed SHAs
    no human commit in the range begins with."""
    unreported = [a for a in actual if not any(a.startswith(c) for c in claimed if c)]
    not_in_range = [c for c in claimed if not _prefix_matches(c, actual)]
    return unreported, not_in_range


def _human_commits_error(root, review_sha, reported):
    """harness-code-review § Review a pinned SHA: every `[harness:human]` commit in the
    reviewed range is reported in `human_commits_in_scope`, and nothing else is. The
    list is COMPUTED from the canonical range and the digest's list is compared to it,
    abbreviated SHAs accepted; the schema requires the field, so `[]` claims none."""
    base_oid, head_oid, range_error = _canonical_review_range(root, review_sha)
    actual = None if range_error else _human_commits_in_range(root, base_oid, head_oid)
    if actual is None:
        return None
    claimed = [str(item).strip().strip("'\"") for item in (reported or [])]
    unreported, not_in_range = _human_commit_disagreement(actual, claimed)
    if not unreported and not not_in_range:
        return None
    parts = ["unreported " + ", ".join(a[:12] for a in unreported)] if unreported else []
    parts += ["not in the range " + ", ".join(not_in_range)] if not_in_range else []
    return (f"human_commits_in_scope disagrees with the reviewed range ({'; '.join(parts)}). "
            f"Every {HUMAN_COMMIT_MARK} commit in {base_oid[:12]}..{head_oid[:12]} is in scope "
            f"and inherits no earlier review; report exactly that set.")


def _dirty_tree_error(root):
    """harness-code-review § Review a pinned SHA: a tree matching no commit has no
    pinnable verdict. Tracked modifications outside `.harness/` at return time refuse a
    PASS or FAIL; the honest return is BLOCKED asking for a commit or a stash."""
    try:
        result = subprocess.run(
            ["git", "-C", root, "status", "--porcelain", "--untracked-files=no"],
            text=True, capture_output=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode:
        return None
    dirty = [line[3:] for line in result.stdout.splitlines()
             if len(line) > 3 and not line[3:].lstrip("\"").startswith(".harness/")]
    if not dirty:
        return None
    shown = ", ".join(dirty[:5]) + (" …" if len(dirty) > 5 else "")
    return (f"the working tree carries uncommitted changes outside .harness/ ({shown}); a tree "
            f"matching no commit has no pinnable verdict. Return BLOCKED and ask for a "
            f"{HUMAN_COMMIT_MARK} commit or a stash, then review the pin.")


def _qa_kind_policy_error(i, kind, state, test_kinds):
    """The harness.json cross-check for one kinds entry, or None."""
    policy = test_kinds.get(kind)
    if not isinstance(policy, dict):
        return f"kinds[{i}] names {kind!r}, which harness.json test_kinds does not declare."
    excluded = policy.get("status") == "excluded" or policy.get("cmd") is None
    if state == "not_applicable" and not excluded:
        return (f"kinds[{i}] ({kind}) claims not_applicable but harness.json carries a "
                f"runnable cmd for it — a kind that ran is satisfied or missing; one that "
                f"could not run is misconfigured (BLOCKED).")
    if state == "satisfied" and policy.get("cmd") is None:
        return (f"kinds[{i}] ({kind}) claims satisfied but harness.json has no cmd for it — "
                f"nothing could have run.")
    return None


def _qa_kind_entry_errors(i, entry, verdict, test_kinds):
    """The semantic rules for one `kinds` entry; its shape and `state` enum are the schema's."""
    if not isinstance(entry, dict):
        return []
    kind = str(entry.get("kind", "")).strip()
    state = entry.get("state")
    err = []
    if state == "misconfigured" and verdict in ("PASS", "FAIL"):
        err.append(f"kinds[{i}] ({kind}) is misconfigured but VERDICT is {verdict} — a kind "
                   f"that cannot run is BLOCKED, never a verdict on the code.")
    policy_error = test_kinds and _qa_kind_policy_error(i, kind, state, test_kinds)
    return err + ([policy_error] if policy_error else [])


def _qa_kind_errors(kinds, verdict, test_kinds):
    """harness-verification-rules § five states, checked against harness.json (the state
    enum is the schema's): `misconfigured` is BLOCKED, never a verdict; `not_applicable`
    is legal only for a kind the policy excludes; `satisfied` needs a runnable `cmd`.
    `test_kinds` None means the policy could not be read — only the shape rules run."""
    return [error for i, raw in enumerate(kinds)
            for error in _qa_kind_entry_errors(i, raw, verdict, test_kinds)]


def _classify_canonical_range(root, base_oid, head_oid, test_kinds):
    """`code_grade.classify` over the canonical range's gated functions, as
    `(result, error)`.

    Every grading failure — a committed Python file that does not parse above all —
    becomes a NAMED refusal here and never a traceback: a crash that escaped this
    boundary would be indistinguishable from a hook defect (DEC-127) and would leave
    the claim ungraded, which is the state BUG-1081 removes.
    """
    try:
        gated, _informational = gated_set(root, base_oid, head_oid)
        _records, result = classify(gated, test_kinds)
    except SyntaxError as exc:
        return None, (_GRADE_PREFIX + f"committed Python in "
                      f"{base_oid[:12]}..{head_oid[:12]} does not parse "
                      f"({exc.msg}, line {exc.lineno}) — fix the committed syntax "
                      f"error and rerun.")
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        # git absent or refusing (OSError, CalledProcessError), an unresolvable revision or a
        # malformed test_kinds policy (ValueError, TestKindsError), or output that is not text
        # (UnicodeDecodeError) — the grader's own boundary classes (FEAT-65).
        return None, (_GRADE_PREFIX + f"grading {base_oid[:12]}..{head_oid[:12]} "
                      f"failed ({type(exc).__name__}: {exc}).")
    return result, None


def _mechanical_code_grade(root, review_sha):
    """The result the REPOSITORY computes for this review, as
    `(result, range_text, error)` — the value a `code_grade` claim is CHECKED against
    rather than trusted (REQ-01).

    `n_a` is decided here and only here: the canonical range changed no `.py` path at
    all. A deletion-only Python range is NOT `n_a` (D-04) — a Python path changed, there
    is simply no head-side function left to gate, so it grades `pass`. Everything else
    goes to `code_grade.classify`, which owns the bars and the fail > grade_2 > pass
    precedence and never returns `n_a`.
    """
    base_oid, head_oid, error = _canonical_review_range(root, review_sha)
    if error:
        return None, None, error
    range_text = f"{base_oid}..{head_oid}"
    changed, error = reviewed_python_change(root, range_text)
    if error:
        return None, range_text, error
    if not changed:
        return "n_a", range_text, None
    test_kinds, error = _load_test_kinds(root)
    if error:
        return None, range_text, error
    result, error = _classify_canonical_range(root, base_oid, head_oid, test_kinds)
    return result, range_text, error


def _grade_2_qualnames(root, review_sha):
    """Qualnames the repository grades exactly 2 over the canonical range, or None when
    that cannot be computed — the grade enforcement above has already refused then."""
    base_oid, head_oid, error = _canonical_review_range(root, review_sha)
    test_kinds = None if error else _load_test_kinds(root)[0]
    if test_kinds is None:
        return None
    try:
        gated, _informational = gated_set(root, base_oid, head_oid)
        records, _result = classify(gated, test_kinds)
    except (OSError, subprocess.SubprocessError, ValueError, SyntaxError):
        return None  # the grade enforcement already refused this range, with its repair
    return sorted({r["qualname"] for r in records if r.get("grade") == 2})


def _grade_2_reasons_error(reasons, qualnames):
    """harness-code-risk-grading: one written reason per `REASON REQUIRED` function,
    naming it. A reason that names no graded function is decoration."""
    if not qualnames:
        return None
    text = " ".join(str(r) for r in reasons)
    unnamed = [q for q in qualnames if q.split(".")[-1] not in text]
    if not unnamed:
        return None
    return (f"grade_2_reasons names none of: {', '.join(unnamed)}. code-grade.py printed "
            f"REASON REQUIRED for each; write one reason per function, naming it, or "
            f"return code_grade: fail.")


SC_LINE_RE = re.compile(r"^\s*-\s*(SC-\d+)\s*:", re.M)
VERIFY_LINE_RE = re.compile(r"^\s*verify:\s*(\S+)", re.M)
CITATION_RE = re.compile(r"[\w./-]+\.\w+:\d+")


def _inspection_sc_ids(brief_text):
    """SC ids whose next `verify:` line reads `inspection`."""
    ids = []
    for match in SC_LINE_RE.finditer(brief_text):
        verify = VERIFY_LINE_RE.search(brief_text, match.end())
        if verify and verify.group(1) == "inspection":
            ids.append(match.group(1))
    return ids


def _read_or_none(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def _cited_sc_ids(body):
    """SC ids on artifact lines that also carry a `path:line` citation."""
    return {sc for line in body.splitlines() if CITATION_RE.search(line)
            for sc in re.findall(r"SC-\d+", line)}


def _inspection_citation_error(feature_dir, root, artifact):
    """harness-code-review § Stage 1: every `verify: inspection` SC is verified in the
    review artifact with a `file:line` citation on a line that names the SC. Silent when
    BRIEF or the artifact cannot be read — an unreadable artifact is DEC-156's finding."""
    brief = _read_or_none(os.path.join(feature_dir, "BRIEF.md")) if feature_dir else None
    wanted = _inspection_sc_ids(brief) if brief else []
    body = wanted and _read_or_none(
        artifact if os.path.isabs(artifact) else os.path.join(root, artifact))
    if not body:
        return None
    missing = [sc for sc in wanted if sc not in _cited_sc_ids(body)]
    if not missing:
        return None
    return (f"BRIEF marks {', '.join(missing)} `verify: inspection` and the review artifact "
            f"cites no file:line for them. Inspection SCs are checked here and nowhere else: "
            f"for each, one line naming the SC and the path:line that satisfies it.")


def _plan_task(feature_dir, task_id):
    """The plan.yaml task mapping with `id == task_id`, or None."""
    try:
        plan = artifact_accessors.load_plan(os.path.join(feature_dir, "plan.yaml"))
    except (OSError, harness_yaml.YamlParseError):
        return None
    return next((task for task in plan.get("tasks") or []
                 if isinstance(task, dict) and task.get("id") == task_id), None)


def _plan_verify_for(feature_dir, task_id):
    """The `verify:` string plan.yaml carries for `task_id`, or None."""
    verify = (_plan_task(feature_dir, task_id) or {}).get("verify")
    return verify.strip() if isinstance(verify, str) and verify.strip() else None


def _receipt_error(feature_dir, root, artifact, task_id):
    """harness-digest-dev § verify receipt: `task_verify: pass` is a claim; the receipt
    named by `artifact` must exist and carry the task's `verify:` command verbatim."""
    body = _read_or_none(artifact if os.path.isabs(artifact) else os.path.join(root, artifact))
    if body is None:
        return (f"task_verify: pass but the receipt {artifact} is not on disk. The receipt "
                f"holds the verify command and its verbatim output; write it before returning.")
    verify = _plan_verify_for(feature_dir, task_id) if feature_dir else None
    if verify and verify not in body:
        return (f"task_verify: pass but the receipt {artifact} does not carry the task's "
                f"verify command verbatim ({verify[:80]!r}). Paste the command as plan.yaml "
                f"spells it, then its output.")
    return None


def _findings_order_error(findings):
    """harness-code-review: findings are ranked — severity never rises down the list."""
    ranks = [SEV.index(entry["severity"]) for entry in findings
             if isinstance(entry, dict) and isinstance(entry.get("severity"), str)
             and entry["severity"] in SEV]
    if ranks == sorted(ranks, reverse=True):
        return None
    return ("findings are not ranked: a lower severity precedes a higher one. An unread "
            "list gates nothing — order by severity, highest first.")


def code_grade_enforcement_error(artifact, reviewed, code_grade, feature_dir=None,
                                 review_pin=None):
    """REQ-01: check a code reviewer's `code_grade` claim against the result this
    repository computes, and refuse the digest when they disagree.

    Plan reviews (DEC-207) never reach here — a pending plan has no code diff and no
    `review_sha`, and grading is not invoked for them at all (REQ-06/D-06). Returns an
    error string, or None when the claim matches.
    """
    _feature_dir, root, review_sha, error = _review_binding(artifact, feature_dir, review_pin)
    if error:
        return error
    if root is None:
        return "code_grade cannot be recomputed: no checkout root resolves from this vantage."
    _discarded, shape_error = reviewed_python_change(root, reviewed)
    if shape_error:
        return shape_error
    expected, range_text, error = _mechanical_code_grade(root, review_sha)
    if error:
        return error
    if expected == code_grade:
        return None
    return (f"code_grade={code_grade!r} disagrees with the mechanical result this "
            f"repository computes over {range_text}: expected {expected!r}. The "
            f"reviewer's enum is an audit claim, not evidence of itself — rerun "
            f"code-grade.py over the canonical range and report what it reports.")


FEATURE_DIR_IN_ARTIFACT_RE = re.compile(r"(\.harness/[^/\s]+/features/[^/\s]+)(?:/|$)")


def _contained_feature_dir(root, relative):
    r"""`(dir, error)` for a captured `.harness/<repo>/features/<FEAT>` path — the ONE
    place that decides the artifact line names a directory INSIDE `root`.

    `[^/\s]+` matches `..`, so `.harness/../features/..` satisfied the pattern and
    `_repo_root_for_feature`'s four `..` segments then resolved a DIFFERENT git work
    tree — measured, against this checkout, resolving to the parent repository that
    shares its object store. That redirected the review_sha read and every grading
    `git -C` call at once, which makes both sides of the binding digest-chosen and
    defeats REQ-02 exactly. Two checks, because they fail on different things:

      - No `.` or `..` segment. With the four segments plain, `_repo_root_for_feature`
        returns `root` BY CONSTRUCTION rather than by coincidence.
      - The resolved path is a strict descendant of `root`. This is what a symlinked
        `.harness` or `<repo>` component would defeat, which the token check cannot see.

    The returned path is the literal join, NOT its realpath: callers compare it against
    paths they built the same way, and on macOS a temp root resolves through
    `/private`, so returning a realpath here would silently break that comparison.
    """
    if any(segment in (".", "..") or not segment for segment in relative.split("/")):
        return None, (f"code_grade cannot be bound to review_sha: artifact path "
                       f"{relative!r} contains a relative segment — write your review "
                       f"under this feature's own .harness/<repo>/features/<FEAT>/notes/ "
                       f"directory, not a path that traverses out of it.")
    feature_dir = os.path.join(root, relative)
    real_root = os.path.realpath(root)
    if not os.path.realpath(feature_dir).startswith(real_root + os.sep):
        return None, (f"code_grade cannot be bound to review_sha: artifact path "
                       f"{relative!r} resolves outside this checkout, so the feature "
                       f"it names is not the one under review.")
    return feature_dir, None


def _worktree_holding(root, path):
    """The member of `root`'s checkout family — `root` itself or one of its linked
    worktrees — that contains absolute `path`, or None when no member does. The family is
    read from `.git/worktrees`, never from the digest, so the root this yields is no more
    digest-chosen than `root` was. Linked worktrees live UNDER the owner root
    (`.claude/worktrees/…`), so the deepest containing member is the holder."""
    real_path = os.path.realpath(path)
    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import harness_boundary
    family = [root] + harness_boundary.linked_worktrees(root)
    holders = [member for member in family
               if real_path.startswith(os.path.realpath(member) + os.sep)]
    return max(holders, key=lambda member: len(os.path.realpath(member)), default=None)


def _feature_dir_from_artifact(artifact, root):
    """The `.harness/<repo>/features/<FEAT>` directory named by this RETURN'S OWN
    `artifact` — the only field SEC-01 trusts to say which feature a reviewer belongs
    to, since every `harness-code-reviewer` writes its artifact under that path (SPEC 8)
    and it is never a persona-chosen field an attacker could point elsewhere. Split out
    of `resolve_review_sha` so the "WHICH feature" half of the lookup grades
    independently of the "WHAT it pins" half.

    Matching the pattern is NOT enough to trust the path; `_contained_feature_dir`
    is what decides it names a directory inside `root`.

    AN ABSOLUTE ARTIFACT BINDS TO THE CHECKOUT THAT HOLDS IT (#1883). Reviews and
    distills run in linked worktrees whose basename need not name the feature
    (`distill-FEAT-63`), and a dispatch may carry no feature marker; joining the
    suffix onto `root` then found no feature.json — or, measured, a DIFFERENT
    checkout's record for a path that was never inside any of them. The holding
    checkout is looked up in `root`'s own worktree family; an absolute path outside
    that family is refused as resolving outside this checkout.

    Returns `(dir, error)`.
    """
    if not isinstance(artifact, str) or not artifact.strip():
        return None, ("code_grade cannot be bound to review_sha: the return names no "
                       "artifact to resolve this feature from.")
    path = artifact.strip().replace(os.sep, "/")
    fm = FEATURE_DIR_IN_ARTIFACT_RE.search(path)
    if not fm:
        return None, (f"code_grade cannot be bound to review_sha: artifact "
                       f"{path!r} does not name a "
                       f".harness/<repo>/features/<FEAT>/ location — write your "
                       f"review under that feature's notes/.")
    if os.path.isabs(path):
        root = _worktree_holding(root, path)
        if root is None:
            return None, (f"code_grade cannot be bound to review_sha: artifact path "
                           f"{path!r} resolves outside this checkout and its linked "
                           f"worktrees, so the feature it names is not the one under "
                           f"review.")
    return _contained_feature_dir(root, fm.group(1))


def _resolve_feature_dir(artifact, feature_dir=None):
    """The `.harness/<repo>/features/<FEAT>` directory this review is bound to:
    `feature_dir` when given (fixture-override seam, mirrors
    `review_config_path`'s `config_path`), otherwise derived from the digest's
    own `artifact` via `_feature_dir_from_artifact`. Factored out so both
    `resolve_review_sha` (the SHA half) and the branch corroboration below (the
    checkout half) resolve the SAME feature, never two independent guesses.

    Returns `(dir, error)`.
    """
    if feature_dir is not None:
        return feature_dir, None
    root = _root_or_none()
    if root is None:
        return None, ("code_grade cannot be bound to review_sha: no checkout "
                       "root resolves from this vantage, so the claim is not "
                       "trusted.")
    return _feature_dir_from_artifact(artifact, root)


def _read_review_sha(feature_dir):
    """feature.json's `review_sha`, or `(None, error)` when it is unreadable or
    unpinned (DEC-121/INV-6 placeholder vocabulary)."""
    fj_path = os.path.join(feature_dir, "feature.json")
    try:
        doc = artifact_accessors.load_feature_json(fj_path)
    except artifact_accessors.FeatureJsonError as e:
        return None, (f"code_grade cannot be bound to review_sha: {fj_path} "
                       f"could not be read ({e}), so the claim is not trusted.")
    sha = doc.get("review_sha") if isinstance(doc, dict) else None
    if not isinstance(sha, str) or sha.strip().lower() in harness_yaml.PLACEHOLDER_UNSET:
        return None, (f"code_grade cannot be bound to review_sha: {fj_path} has "
                       f"no pinned review_sha — an unpinned feature (INV-6) "
                       f"cannot anchor a code_grade claim.")
    return sha.strip(), None


# #1677: THE PIN MAY COME FROM THE DISPATCH. INV-6's job is that no code review is unpinned —
# that the head a reviewer claims to have read equals a SHA the reviewer did not choose.
# feature.json's review_sha was the only source, which refused two correct reviews: a feature
# whose planning was stopped and whose feature.json is deliberately frozen at
# `review_sha: none`, and a DEC-174 direct patch with no feature at all. The pin a dispatcher
# writes into the assignment (`HARNESS-REVIEW-PIN: <sha>`, forwarded by the host as
# `harness_review_pin`) is equally outside the digest's control, so it is accepted as the pin
# when feature.json has none, and it must AGREE with feature.json's when both exist — the
# dispatch never overrides a recorded pin. `review_sha: none` alone stays a refusal.


def _pins_agree(root, recorded, pinned):
    recorded_oid = resolve_reviewed_commit(root, recorded)
    pinned_oid = resolve_reviewed_commit(root, pinned)
    return recorded_oid is not None and recorded_oid == pinned_oid


def _review_binding(artifact, feature_dir, review_pin):
    """(feature_dir, root, review_sha, error): the checkout and the pin a code review is
    bound to. `feature_dir` is None for a pinned review with no feature (nothing to
    corroborate a branch against); `error` is set when no trusted pin can be established."""
    feature_dir, dir_error = _resolve_feature_dir(artifact, feature_dir)
    if dir_error:
        if review_pin:
            return None, _root_or_none(), review_pin, None
        return None, None, None, dir_error
    root = _repo_root_for_feature(feature_dir)
    recorded, sha_error = _read_review_sha(feature_dir)
    if sha_error:
        if review_pin:
            return feature_dir, root, review_pin, None
        return feature_dir, root, None, sha_error
    if review_pin and not _pins_agree(root, recorded, review_pin):
        return feature_dir, root, None, (
            f"code_grade cannot be bound to review_sha: the dispatch pinned {review_pin!r} "
            f"but this feature's feature.json records review_sha {recorded!r} — a recorded "
            f"pin is never overridden; re-pin feature.json or dispatch against it.")
    return feature_dir, root, recorded, None


_BRANCH_UNSET = object()  # sentinel: no branch_override given -> derive from git


def _read_feature_branch(feature_dir):
    """feature.json's `branch` field, or None when absent, `none`, or the file
    is unreadable. Unlike `_read_review_sha`, this is NOT a fail-closed read:
    SEC-01's SHA binding already rejects an unreadable/unpinned feature.json
    elsewhere, and a legitimate feature.json may genuinely carry no branch
    (`branch: none` — e.g. FEAT-01, FEAT-15, FEAT-19 in this repo). "Cannot
    tell" here must mean "nothing to corroborate", never "reject".
    """
    fj_path = os.path.join(feature_dir, "feature.json")
    try:
        doc = artifact_accessors.load_feature_json(fj_path)
    except artifact_accessors.FeatureJsonError:
        return None
    branch = doc.get("branch") if isinstance(doc, dict) else None
    if not isinstance(branch, str) or branch.strip().lower() in harness_yaml.PLACEHOLDER_UNSET:
        return None
    return branch.strip()


def _current_branch_or_none(branch_override=_BRANCH_UNSET, feature_dir=None):
    """The branch of the checkout that owns `feature_dir`, or None when unknown."""
    if branch_override is not _BRANCH_UNSET:
        return branch_override
    root = _root_or_none() if feature_dir is None else _repo_root_for_feature(feature_dir)
    if root is None:
        return None
    try:
        result = subprocess.run(
            ["git", "-C", root, "rev-parse", "--abbrev-ref", "HEAD"],
            text=True, capture_output=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode:
        return None
    branch = result.stdout.strip()
    return branch if branch and branch != "HEAD" else None


def _branch_corroboration_error(feature_dir, current_branch):
    """SEC-01 hardening (wave 3): the digest's own `artifact` still picks
    WHICH feature.json's review_sha a claim is bound to (SEC-01's residual
    hole) — a reviewer can point `artifact` at a different shipped feature
    and reuse ITS pin. This corroborates against the one thing no digest
    controls: the checkout the validator is actually running in. ADDITIVE
    ONLY — it may turn an accept into a reject, never the reverse — so either
    side being unknown means "nothing to corroborate", not "reject":
      - `current_branch` is None (undeterminable checkout): behave as today.
      - the feature's `branch` is None (absent or `none`, a real recorded
        state — FEAT-01/15/19): behave as today.
    Only a REAL, DIFFERENT branch name on both sides rejects.
    """
    if current_branch is None:
        return None
    feature_branch = _read_feature_branch(feature_dir)
    if feature_branch is None:
        return None
    if feature_branch == current_branch:
        return None
    return (f"code_grade cannot be bound to review_sha: this feature's "
            f"recorded branch ({feature_branch!r}) does not match the current "
            f"checkout's branch ({current_branch!r}) — the digest's artifact: "
            f"line must name the feature actually under review in this "
            f"checkout, not another shipped feature's notes/ path.")


def _parse_reviewed_range(reviewed):
    """Split `reviewed` into `(base, head, None)`, or `(None, None, error)` on a
    malformed range — the same shape rules `reviewed_python_change` enforces on the
    canonical range,
    factored out so `code_grade_bound_to_review` stays a flat sequence of checks."""
    if not isinstance(reviewed, str) or reviewed.count("..") != 1:
        return None, None, "reviewed range must name exactly one base..head range."
    base, head = (part.strip() for part in reviewed.split(".."))
    if not base or not head:
        return None, None, "reviewed range must name non-empty base and head revisions."
    return base, head, None


_PLAN_REVIEW_PREFIX = "plan:"


def _is_plan_review(reviewed):
    return isinstance(reviewed, str) and reviewed.startswith(_PLAN_REVIEW_PREFIX)


def _resolve_plan_review_path(reviewed):
    named_path = reviewed[len(_PLAN_REVIEW_PREFIX):].strip()
    if not named_path:
        return None, "reviewed plan target is empty — write plan:<path-to-plan.yaml>."
    if os.path.isabs(named_path):
        return os.path.realpath(named_path), None
    root = _root_or_none()
    if root is None:
        return None, "reviewed plan target cannot be resolved from this checkout."
    return os.path.realpath(os.path.join(root, named_path)), None


def _pending_plan_status_error(plan_path):
    try:
        plan = artifact_accessors.load_plan(plan_path)
    except harness_yaml.YamlParseError as exc:
        # load_plan's one exported class: PlanSchemaError is a YamlParseError too (FEAT-65).
        return f"reviewed plan target {plan_path!r} could not be read ({exc})."
    approval = plan.get("approval") if isinstance(plan, dict) else None
    status = approval.get("status") if isinstance(approval, dict) else None
    if status == "pending":
        return None
    return (f"plan review mode is only valid while approval.status is pending; "
            f"{plan_path!r} records {status!r}.")


def _pinned_feature_review_error(feature_dir):
    feature_json = os.path.join(feature_dir, "feature.json")
    if not os.path.exists(feature_json):
        return None
    try:
        feature = artifact_accessors.load_feature_json(feature_json)
    except artifact_accessors.FeatureJsonError as exc:
        return f"pre-signature feature record {feature_json!r} is unreadable ({exc})."
    review_sha = feature.get("review_sha") if isinstance(feature, dict) else None
    if not isinstance(review_sha, str) \
            or review_sha.strip().lower() in harness_yaml.PLACEHOLDER_UNSET:
        return None
    return ("plan review mode is pre-signature only, but feature.json already "
            "has a pinned review_sha.")


def _pending_plan_review_error(artifact, reviewed, code_grade, feature_dir, branch_override):
    """Bind DEC-207's pre-signature review to its pending plan and checkout."""
    feature_dir, dir_error = _resolve_feature_dir(artifact, feature_dir)
    if dir_error:
        return dir_error
    if code_grade != "n_a":
        return "a plan review has no code diff; code_grade must be 'n_a'."
    plan_path, path_error = _resolve_plan_review_path(reviewed)
    if path_error:
        return path_error
    expected_path = os.path.realpath(os.path.join(feature_dir, "plan.yaml"))
    if plan_path != expected_path:
        return (f"reviewed plan target {plan_path!r} is not this feature's "
                f"plan.yaml ({expected_path}).")
    return (
        _pending_plan_status_error(plan_path)
        or _pinned_feature_review_error(feature_dir)
        or _branch_corroboration_error(
            feature_dir, _current_branch_or_none(branch_override, feature_dir)
        )
    )


def _skipped_member_error(fields):
    """Validate the one optional external member that may legitimately not run."""
    status = fields.get("status")
    if status is None:
        return False, None
    if str(status).lower() != "skipped":
        return False, f"member status {status!r} must be exactly 'skipped' when present."
    if fields.get("verdict"):
        return True, "a skipped member did not run and must not also claim a verdict."
    if not str(fields.get("persona", "")).strip():
        return True, "a skipped member must name its persona."
    if not str(fields.get("reason", "")).strip():
        return True, "a skipped member must name the host reason it did not run."
    if fields.get("persona") != "fable-advisor":
        return True, ("only the optional fable-advisor may be recorded as skipped; "
                      "mandatory members must carry their verdict.")
    return True, None


def code_grade_bound_to_review(artifact, reviewed, code_grade, feature_dir=None,
                               branch_override=_BRANCH_UNSET, review_pin=None):
    """Bind a code review to review_sha, or a DEC-207 plan review to its pending plan.

    The code path runs unconditionally for pass, fail, grade_2, and n_a: a forged
    range must not describe a diff nobody reviewed. Plan mode is a distinct target,
    not a missing SHA fallback, and accepts only code_grade n_a.

    Only `head` is bound — `base` has no independent system-of-record value
    today (batch contract). `head` is what varies between an honest review (it
    equals `review_sha`) and a forged one (a convenient, resolvable stand-in
    that is not).

    Wave 3 hardening: even an honest head==review_sha binding still trusts the
    digest's OWN `artifact` to pick WHICH feature.json supplied that
    review_sha — a reviewer can point `artifact` at a different shipped
    feature and reuse ITS pin. `_branch_corroboration_error` closes that with
    the one thing no digest controls: the checkout's actual current branch.

    #1677: `review_pin` is the dispatcher's pin (`HARNESS-REVIEW-PIN:` in the assignment),
    accepted when feature.json has none and required to agree with it otherwise; see
    `_review_binding`.

    Returns an error string, or `None` when the binding holds.
    """
    if _is_plan_review(reviewed):
        return _pending_plan_review_error(
            artifact, reviewed, code_grade, feature_dir, branch_override
        )
    feature_dir, root, review_sha, binding_error = _review_binding(artifact, feature_dir, review_pin)
    if binding_error:
        return binding_error
    head_error = _head_is_pin_error(root, reviewed, review_sha)
    if head_error or feature_dir is None:
        return head_error
    return _branch_corroboration_error(
        feature_dir, _current_branch_or_none(branch_override, feature_dir)
    )


def _head_is_pin_error(root, reviewed, review_sha):
    """The error when `reviewed`'s head is not the pinned commit, else None."""
    _base, head, range_error = _parse_reviewed_range(reviewed)
    if range_error:
        return range_error
    if root is None:
        return "reviewed range could not be resolved: no checkout root resolves from this vantage."
    head_oid = resolve_reviewed_commit(root, head)
    if head_oid is None:
        return "reviewed range could not be resolved to commit revisions."
    pin_oid = resolve_reviewed_commit(root, review_sha)
    if pin_oid is None:
        return (f"code_grade cannot be bound to review_sha: the pinned review_sha "
                f"({review_sha!r}) does not resolve to a commit.")
    if head_oid != pin_oid:
        return (f"reviewed head {head!r} does not resolve to the pinned review_sha "
                f"({review_sha}) — write the range that ends at the pin (feature.json's "
                f"review_sha, or the dispatch's HARNESS-REVIEW-PIN), not a convenient no-op.")
    return None


def validate(persona, obj, config_path=None, feature_dir=None, branch_override=_BRANCH_UNSET,
             review_pin=None, mission=None):
    """Every contract error for one digest object — schema first, then the semantic
    gates — or [] when it is valid. `obj` is the returned value itself; anything that is
    not a mapping is one error naming the object shape. An unknown persona is refused,
    never guessed; a schema that cannot load is OUR defect and raises."""
    if not isinstance(obj, dict):
        return [OBJECT_REQUIRED]
    try:
        canonical = digest_schema.canonical_persona(persona)
    except digest_schema.DigestSchemaError as error:
        return [f"{error} Cannot validate; refusing to pass it."]
    family = norm(canonical)
    err = _schema_messages(canonical, family, obj,
                           digest_schema.validate_object(canonical, obj))
    seen = obj.get("DIGEST") if isinstance(obj.get("DIGEST"), dict) else {}
    verdict = obj.get("VERDICT") if isinstance(obj.get("VERDICT"), str) else None
    err += _semantic_errors(canonical, family, verdict, seen, obj.get("artifact"), mission,
                            config_path=config_path, feature_dir=feature_dir,
                            branch_override=branch_override, review_pin=review_pin)
    return err


# --- Schema error wording. digest_schema.py reports `path: message` in jsonschema's words;
# the three shapes an agent most often gets wrong are reworded so the repair is named:
# a missing field says which value validates (REQ-11), an unexpected key says whether it
# is drift of a real key or undeclared, and an enum miss lists the legal values.
_REQUIRED_RE = re.compile(r"^'(?P<field>[^']+)' is a required property$")
_EXTRA_RE = re.compile(r"^Additional properties are not allowed \((?P<keys>.*) (?:was|were) "
                       r"unexpected\)$")
_ENUM_MISS_RE = re.compile(r"(is not one of|is not valid under any of the given schemas)")
_TASK_PATTERN_RE = re.compile(r"does not match '\^\(T-")
_UNSET_PATTERN_RE = re.compile(r"does not match '\^\(\[Nn\]\[Oo\]\[Nn\]\[Ee\]")
_COMMON_REF = "common.json#/$defs/"


def _schema_messages(canonical, family, obj, schema_errors):
    messages = (_schema_message(canonical, family, obj, *raw.partition(": ")[::2])
                for raw in schema_errors)
    return [message for message in messages if message is not None]


def _schema_message(canonical, family, obj, path, message):
    """One schema error in repair-naming words, or None when the semantic layer reports the
    same fault in its own single error (D-08(c): exactly one error per fault)."""
    parts = [] if path == "<root>" else path.split("/")
    digest = obj.get("DIGEST") if isinstance(obj.get("DIGEST"), dict) else {}
    if len(parts) == 2 and parts[0] == "DIGEST" and _semantics_own(parts[1], digest, message):
        return None
    reworded = _structure_message(canonical, family, parts, message) or (
        len(parts) == 2 and parts[0] == "DIGEST"
        and _field_message(canonical, parts[1], digest, message))
    return reworded or f"{_location(parts)}: {message}"


def _semantics_own(field, digest, message):
    """The schema's `task: none` → `task_verify` unset rule, which _unbound_field_errors
    already reports naming the actionable field."""
    return (field in CONDITIONAL and _placeholder(digest.get(CONDITIONAL[field]))
            and not _placeholder(digest.get(field)) and _UNSET_PATTERN_RE.search(message))


def _location(parts):
    """`findings[0].kind` for DIGEST/findings/0/kind — the field as the agent wrote it."""
    names = parts[1:] if parts[:1] == ["DIGEST"] and len(parts) > 1 else parts
    text = ""
    for name in names:
        text += f"[{name}]" if name.isdigit() else (f".{name}" if text else name)
    return text or "the returned object"


def _structure_message(canonical, family, parts, message):
    """A missing top-level or DIGEST field, or an unexpected DIGEST key, reworded."""
    required = _REQUIRED_RE.match(message)
    if required and parts in ([], ["DIGEST"]):
        return _missing_message(canonical, family, parts, required.group("field"))
    extra = _EXTRA_RE.match(message)
    if extra and parts == ["DIGEST"]:
        return _undeclared_message(canonical, extra.group("keys"))
    return None


def _field_message(canonical, field, digest, message):
    """A top-level DIGEST field's task-id, enum or conditional miss, reworded; None keeps
    jsonschema's."""
    value = digest.get(field)
    if field == "task" and _TASK_PATTERN_RE.search(message):
        return (f"task={value!r} is not a task id — write your task's `T-NN` id exactly "
                f"as your dispatch carries it (T-05), or `none` if this dispatch carries "
                f"no PLAN task.")
    if canonical == "harness-orchestrator" and field in ("judgement", "cycles_used"):
        return _rejection_message(field, value, digest.get("status"))
    if _ENUM_MISS_RE.search(message):
        return _enum_message(canonical, field, value)
    return None


def _rejection_message(field, value, status):
    """FEAT-1714's `status: rejected` pairing: one judgement mapping and zero cycles on a
    rejection, and `judgement: none` on every other status."""
    if field == "cycles_used":
        return (f"cycles_used={value!r} on status: rejected — a first-run rejection spends "
                f"no cycle; write 0." if status == "rejected" else None)
    if status != "rejected":
        return (f"judgement={value!r} on status: {status} — judgement is `none` unless "
                f"status is rejected.")
    if isinstance(value, dict):
        return None  # a mapping's own key faults are reported at their paths
    return (f"judgement={value!r} on status: rejected — a rejection carries one mapping "
            f"{{kind: reject, superseded_by: <positive int or none>, reason: <one line, "
            f"at most 240 characters>}}.")


def _at(obj, parts):
    for part in parts:
        if isinstance(obj, dict):
            obj = obj.get(part)
        elif isinstance(obj, list) and part.isdigit() and int(part) < len(obj):
            obj = obj[int(part)]
        else:
            return None
    return obj


def _resolved(node):
    """`node` with a common.json `$ref` followed; wording only, never validation."""
    ref = node.get("$ref") if isinstance(node, dict) else None
    if isinstance(ref, str) and ref.startswith(_COMMON_REF):
        return _resolved(digest_schema.common_defs().get(ref[len(_COMMON_REF):], {}))
    return node if isinstance(node, dict) else {}


def _field_schema(canonical, field):
    return _digest_properties(canonical).get(field) or {}


def _enum_values(node):
    node = _resolved(node)
    values = list(node.get("enum") or [])
    if "const" in node:
        values.append(node["const"])
    for option in node.get("anyOf") or []:
        values += _enum_values(option)
    return values


def _accepts_unset(node):
    node = node if isinstance(node, dict) else {}
    if node.get("$ref") == _COMMON_REF + "unset":
        return True
    return any(_accepts_unset(option) for option in _resolved(node).get("anyOf") or [])


def _enum_message(canonical, field, value):
    node = _field_schema(canonical, field)
    legal = [v for v in _enum_values(node) if isinstance(v, str)]
    unset = " (or `none`/`n/a` where it genuinely does not apply)" if _accepts_unset(node) else ""
    if not legal:
        # boolean_nullable: a string like "mostly" silently soft-fails a hard gate.
        return f"{field}={value!r} must be a bool, true or false{unset}."
    if isinstance(value, list):
        return f"{field}={value!r} must be a single value from {sorted(legal)}{unset}, not a list."
    return f"{field}={value!r} is not in {sorted(legal)}{unset}{_near_miss(legal, value)}."


def _near_miss(allowed, val):
    """` (did you mean …?)` when a string value shares a prefix with a legal one, else ``."""
    if isinstance(val, str):
        near = [a for a in allowed if a.startswith(val[:3]) or val.startswith(a[:3])]
        if near:
            return f" (did you mean {near[0]!r}?)"
    return ""


def _missing_message(canonical, family, parts, field):
    if not parts:
        return (f"missing {field!r} — the returned object carries exactly VERDICT, DIGEST and "
                f"artifact at its top level; {OBJECT_REQUIRED}")
    return (f"missing {field!r} — every field is required; write "
            f"{_missing_field_hint(canonical, family, field)}. An absent field is ambiguous; "
            f"an explicit empty one asserts you looked.")


# REQ-11: a hint must name a value that will actually VALIDATE. `task_verify` once
# inherited "write `none`" — which the gate then rejects alongside PASS — and `task`
# "write `[]`", which its own pattern rejects. Most specific first.
_TASK_HINT = ("your task's `T-NN` id exactly as your dispatch carries it (T-05), or `none` "
              "if this dispatch carries no PLAN task")
# FEAT-59 SC-17. `[]` is REJECTED alongside PASS + matrix_ok: true.
_FAIL_FIRST_HINT = ("one `{ sc: SC-NN, evidence: <path or receipt line> }` per `verify: "
                    "automated` SC showing the test FAILED before the fix; `[]` only when "
                    "matrix_ok is n/a or the verdict is not PASS")


def _missing_field_hint(canonical, family, field):
    node = _field_schema(canonical, field)
    legal = sorted(v for v in _enum_values(node) if isinstance(v, str))
    if field == "task":
        return _TASK_HINT
    if field in GATE_FIELDS.get(family, ()) and legal:
        return _gate_hint(field, legal)
    if field == "fail_first":
        return _FAIL_FIRST_HINT
    return _value_hint(node, legal)


def _value_hint(node, legal):
    """The FEAT-1928 ruling: a field that does not apply is spelled, never omitted — so a
    field whose schema admits the unset sentinel names `none` as that spelling."""
    unset = (", or `none` if it does not apply"
             if _accepts_unset(node) and "none" not in legal else "")
    if legal:
        return f"one of {legal} — a single enum value, never a list{unset}"
    return _type_hint(node) + unset


def _gate_hint(field, legal):
    """WORDING: never say a placeholder is disallowed — `suite: n/a` with BLOCKED is legal
    (REQ-03/SC-06). The gate is on the PAIRING, so the hint says so. JOINTLY FOLLOWABLE
    (SC-18c): `task: none` lifts the obligation, so the hint offers that exit too."""
    hint = (f"one of {legal} — what gets rejected for this role is a placeholder "
            f"ALONGSIDE `VERDICT: PASS`, never the placeholder itself (`n/a` with FAIL "
            f"or BLOCKED is the honest refusal)")
    if field in CONDITIONAL:
        hint += (f", or `n/a` if this dispatch carries no PLAN task "
                 f"and you wrote `{CONDITIONAL[field]}: none`")
    return hint


_TYPE_HINTS = {
    "array": "`[]` if there are none",
    "integer": "an integer",
    "boolean": "true or false",
    "string": "a non-empty string (the literal `none` if genuinely not applicable)",
    "object": "the mapping its schema declares, every key present",
}


def _type_hint(node):
    resolved = _resolved(node)
    # A nullable field is anyOf(<its type>, unset): the hint names the real branch.
    kind = resolved.get("type") or next(
        (_resolved(option).get("type") for option in resolved.get("anyOf") or []
         if not _accepts_unset(option)), None)
    return _TYPE_HINTS.get(kind, "a value")


def _undeclared_message(canonical, keys_text):
    declared = set(_digest_properties(canonical))
    keys = re.findall(r"'([^']*)'", keys_text)
    drifted = [(key, want) for key in keys for want in sorted(declared)
               if key != want and key.replace("-", "_").lower() == want]
    if drifted:
        return "; ".join(f"key {key!r} is drifted spelling of {want!r} — the runner routes on "
                         f"the exact name and will not see it." for key, want in drifted)
    names = ", ".join(repr(key) for key in keys)
    return (f"undeclared digest key(s): {names}. The digest contract is closed: "
            f"{os.path.join('.claude/skills/harness/bin/digest-schemas', canonical + '.json')} "
            f"declares every DIGEST key. A per-dispatch answer is not a digest key: put a PASS "
            f"qualification in adequacy_notes or a per-step fact in the run state steps "
            f"evidence container.")


def _digest_properties(canonical):
    return digest_schema.load_schema(canonical)["properties"]["DIGEST"]["properties"]


# --- The semantic layer: what a schema cannot say.
_GATED = ("suite", "matrix_ok", "task_verify", "code_grade", "reviewed")


def _semantic_errors(canonical, family, verdict, seen, artifact, mission, *,
                     config_path, feature_dir, branch_override, review_pin):
    passing = verdict == "PASS"
    err = [error for field in _GATED if field in seen
           for error in _gate_field_errors(field, seen[field], seen, family, mission, passing)]
    err += _family_errors(family, verdict, seen, artifact, feature_dir)
    if canonical == "harness-code-reviewer":
        err += _reviewer_errors(seen, artifact, verdict, family, mission,
                                config_path=config_path, feature_dir=feature_dir,
                                branch_override=branch_override, review_pin=review_pin)
    if canonical == "harness-eng-lead":
        err += _amendments_errors(seen)
    return err


def _family_errors(family, verdict, seen, artifact, feature_dir):
    if family == "qa":
        return _qa_errors(seen, verdict, feature_dir)
    if family in ("dev", "dev-ops"):
        return _dev_receipt_errors(seen, verdict, artifact, feature_dir)
    if family == "lead":
        return _lead_rollup_errors(seen, verdict)
    return []


def _gate_field_errors(field, val, seen, persona, mission, passing):
    """One gate field's errors: pinned by the mission, lifted by `task: none`, declined
    beside PASS, or reported FAILED beside PASS — each a return, most specific first."""
    # #1855: on a mission with no gate subject the field is PINNED to its did-nothing
    # spelling — one error, one actionable field; no gate below ever sees it.
    pinned = _mission_pinned_value(field, persona, mission)
    if pinned is not None:
        if val != pinned:
            return [f"{field}={val!r} on a {mission} dispatch — this mission reviews no diff "
                    f"and runs no suite, so a gate value here is decoration rather than "
                    f"evidence. Write `{field}: {pinned}`."]
        return []
    # D-08(b)/(c). BEFORE the placeholder branch: after it, D-08(b) is unreachable.
    if _unbound(field, seen):
        return _unbound_field_errors(field, val)
    if _placeholder(val):
        return _declined_gate_errors(field, val, seen, persona, passing)
    return _fail_value_errors(field, val, persona, passing)


def _unbound_field_errors(field, val):
    if _placeholder(val):
        # D-08(b): `n/a` is the honest DEC-121 spelling for a field with no answer, and
        # the n/a-with-PASS gate does NOT bind here — there was no gate to decline.
        return []
    # D-08(c): exactly ONE error, naming the actionable field.
    return [f"{field}={val!r} but {CONDITIONAL[field]}=none — a dispatch "
            f"carrying no PLAN task has no verify: command to report on. "
            f"Write `{field}: n/a`, or name the task's T-NN id in "
            f"`{CONDITIONAL[field]}`."]


def _declined_gate_errors(field, val, seen, persona, passing):
    # DEC-173: declining a GATE while claiming PASS is the fail-open the did-nothing
    # spelling would otherwise have created.
    if field in GATE_FIELDS.get(persona, ()) and passing \
            and not _nothing_to_gate(field, persona, seen):
        return [f"{field}={val!r} declines to report a gate, but VERDICT is "
                f"PASS — a gate that did not run cannot have passed. Return "
                f"BLOCKED or FAIL, or report the real result."]
    return []


# THE FAIL-VALUE GATE. Deliberately OUTSIDE the placeholder branch — nesting it inside is
# exactly why `suite: fail` + PASS was accepted for five features.
def _fail_value_errors(field, val, persona, passing):
    expected = GATE_FAIL_VALUES.get(persona, {})
    if field in expected and passing:
        want = expected[field]
        # TYPE-STRICT: `0 == False` is True in Python, so a bare equality would fire on
        # `matrix_ok: 0`.
        if val == want and isinstance(val, type(want)):
            return [f"{field}={val!r} reports a gate as FAILED, but VERDICT is "
                    f"PASS — a gate that failed cannot have passed. Fix until it "
                    f"passes, or return FAIL or BLOCKED."]
    return []


def _artifact_text(artifact):
    """The artifact path as written, or "" when the return names none (the schema says so)."""
    return artifact.strip() if isinstance(artifact, str) else ""


def _dev_receipt_errors(seen, verdict, artifact, feature_dir):
    """harness-digest-dev: a `task_verify: pass` return names a receipt that exists and
    carries the task's verify command. Silent when no checkout root resolves."""
    path = _artifact_text(artifact)
    if not (verdict == "PASS" and seen.get("task_verify") == "pass" and path):
        return []
    fd, _dir_error = _resolve_feature_dir(path, feature_dir)
    if not fd or not os.path.isdir(fd):
        return []  # no feature on disk to hold a receipt
    error = _receipt_error(fd, _repo_root_for_feature(fd), path,
                           str(seen.get("task", "")).strip())
    return [error] if error else []


# --- FEAT-59 SC-17: a green suite with no fail-first evidence is not a pass. Bound to the
# same triple #919 re-verifies — VERDICT PASS + matrix_ok true — so `matrix_ok: n/a` and
# every non-PASS verdict may truthfully carry `[]`. Entry shape is the schema's.
def _qa_errors(seen, verdict, feature_dir):
    return (_qa_fail_first_errors(seen, verdict == "PASS")
            + _qa_kinds_errors(seen, verdict, feature_dir)
            + _qa_unearned_fail_errors(seen, verdict))


def _qa_unearned_fail_errors(seen, verdict):
    """harness-verification-rules § test-first audit: violations are findings in the
    artifact and never fail the gate by themselves. A FAIL with every gate green
    reports a failure no gate produced."""
    green = (seen.get("suite") == "pass" and seen.get("matrix_ok") is True
             and seen.get("failures") == 0 and bool(seen.get("fail_first")))
    if verdict != "FAIL" or not green:
        return []
    return ["VERDICT: FAIL with suite: pass, matrix_ok: true, failures: 0 and fail_first "
            "evidence present — no gate failed. A test-first violation or a coverage "
            "concern is a finding in the artifact (and a coverage_gaps entry), not a "
            "verdict; return PASS with it recorded, or name the gate that failed."]


def _qa_fail_first_errors(seen, passing):
    fail_first = seen.get("fail_first")
    if fail_first == [] and passing and seen.get("matrix_ok") is True:
        return ["fail_first: [] alongside matrix_ok: true and VERDICT: PASS — a "
                "green suite with no fail-first evidence is not a pass. For each "
                "`verify: automated` SC name the test and the evidence it FAILED "
                "before the fix ({ sc: SC-NN, evidence: <path or receipt line> }), "
                "or return FAIL."]
    return []


def _qa_kinds_errors(seen, verdict, feature_dir):
    kinds = seen.get("kinds")
    qa_root = (_repo_root_for_feature(feature_dir) if feature_dir
               else _root_or_none())
    test_kinds = _load_test_kinds(qa_root)[0] if qa_root else None
    err = _qa_kind_errors(kinds, verdict, test_kinds) if isinstance(kinds, list) and kinds else []
    if verdict == "PASS" and seen.get("matrix_ok") is True and feature_dir and qa_root:
        err += _matrix_floor_errors(kinds, _matrix_floor(qa_root, feature_dir, test_kinds))
    return err


_MATRIX_UNSTARTED = ("todo",)


def _load_matrix_inputs(root, feature_dir):
    """`(test_matrix, tasks)` from the checkout's harness.json and the plan, or `(None, None)`."""
    try:
        matrix = artifact_accessors.load_harness_json(
            os.path.join(root, ".harness", "harness.json")).get("test_matrix")
        tasks = artifact_accessors.load_plan(os.path.join(feature_dir, "plan.yaml")).get("tasks")
    except (OSError, artifact_accessors.ArtifactAccessError, harness_yaml.YamlParseError):
        return None, None
    if not isinstance(matrix, dict) or not isinstance(tasks, list):
        return None, None
    return matrix, tasks


def _always_kinds(matrix, task):
    if not isinstance(task, dict) or task.get("status") in _MATRIX_UNSTARTED:
        return ()
    row = matrix.get(task.get("change_type")) or {}
    return tuple(k for k in row.get("always") or [] if isinstance(k, str))


def _excluded_kinds(test_kinds):
    return {k for k, p in (test_kinds or {}).items()
            if isinstance(p, dict) and (p.get("status") == "excluded" or p.get("cmd") is None)}


def _matrix_floor(root, feature_dir, test_kinds):
    """harness-verification-rules § the matrix is a floor: the kinds `test_matrix.<change_type>.always`
    requires across the plan's started tasks, minus kinds the policy excludes. The `when:` half is
    qa's judgement (DEC-212) and is not computed here. None when the floor cannot be derived."""
    matrix, tasks = _load_matrix_inputs(root, feature_dir)
    if matrix is None:
        return None
    floor = {k for task in tasks for k in _always_kinds(matrix, task)}
    return sorted(floor - _excluded_kinds(test_kinds))


def _satisfied_kinds(kinds):
    return {str(entry.get("kind", "")).strip() for entry in kinds
            if isinstance(entry, dict) and entry.get("state") == "satisfied"}


def _matrix_floor_errors(kinds, floor):
    """`matrix_ok: true` on a PASS claims every floor kind ran and passed; the `kinds:` list
    must say so, kind by kind."""
    if not floor:
        return []
    if not isinstance(kinds, list) or not kinds:
        return [f"matrix_ok: true but kinds: [] reports no kind — the matrix floor for this plan is "
                f"{', '.join(floor)}; report each with its state, or the claim is unverifiable."]
    missing = [k for k in floor if k not in _satisfied_kinds(kinds)]
    if not missing:
        return []
    plural = "it" if len(missing) == 1 else "them"
    return [f"matrix_ok: true but the matrix floor requires {', '.join(missing)} "
            f"(test_matrix.<change_type>.always for this plan's tasks) and kinds: does not report "
            f"{plural} satisfied. The floor is never lowered: run the kind, or return FAIL with it "
            f"missing."]


def _reviewer_errors(seen, artifact, verdict, persona, mission, *,
                     config_path, feature_dir, branch_override, review_pin):
    passing = verdict == "PASS"
    review_policy = load_policy(review_config_path(config_path))["review"]
    code_grade = seen.get("code_grade")
    reviewed = seen.get("reviewed")
    err = _code_grade_errors(artifact, code_grade, reviewed, persona, mission, verdict, seen,
                             feature_dir=feature_dir, branch_override=branch_override,
                             review_pin=review_pin)
    err += _findings_rank_errors(seen.get("findings"))
    if code_grade == "fail" and passing:
        err.append("code_grade='fail' reports a gate as FAILED, but VERDICT is PASS — "
                   "a gate that failed cannot have passed.")
    err += _review_policy_errors(seen, review_policy, passing)
    return err


def _findings_rank_errors(findings):
    if not (isinstance(findings, list) and findings):
        return []
    error = _findings_order_error(findings)
    return [error] if error else []


def _review_policy_errors(seen, review_policy, passing):
    must_fix = seen.get("must_fix")
    severity_max = seen.get("severity_max")
    if isinstance(must_fix, list) and severity_max in SEV \
            and evaluate_review(review_policy, must_fix, severity_max) == "FAIL" \
            and passing:
        return [f"review policy {review_policy!r} reports a gate as FAILED, but "
                "VERDICT is PASS — a gate that failed cannot have passed."]
    return []


def _code_grade_errors(artifact, code_grade, reviewed, persona, mission, verdict, seen, *,
                       feature_dir, branch_override, review_pin):
    err = []
    # #1855: a distill dispatch has no diff to bind or grade; the gate check above
    # already pinned `code_grade`/`reviewed` to their did-nothing spelling.
    grades_a_diff = _mission_pinned_value("code_grade", persona, mission) is None
    # SEC-01 still runs before branching on the grade. DEC-207 adds one
    # separately-bound target: plan:<path> for a pending pre-signature plan.
    binding_error = grades_a_diff and code_grade_bound_to_review(
        artifact, reviewed, code_grade, feature_dir, branch_override, review_pin
    )
    if binding_error:
        err.append(binding_error)
    if grades_a_diff and code_grade in CODE_GRADE_VALUES and not _is_plan_review(reviewed):
        err += _ordinary_review_errors(artifact, code_grade, reviewed, verdict, seen,
                                       feature_dir, review_pin, bool(binding_error))
    return err


def _ordinary_review_errors(artifact, code_grade, reviewed, verdict, seen, feature_dir, review_pin,
                            bound_failed):
    # BUG-1081: the mechanical result is RECOMPUTED here, for every ordinary
    # code review, and the digest's enum is rejected when it disagrees. Before
    # this, only `n_a` was re-derived and `pass`/`fail`/`grade_2` were taken on
    # the reviewer's word, so a skipped, crashed or misreported grader passed.
    err = []
    grade_error = code_grade_enforcement_error(
        artifact, reviewed, code_grade, feature_dir, review_pin)
    if grade_error:
        err.append(grade_error)
    if not bound_failed and verdict in ("PASS", "FAIL"):
        err += _bound_tree_errors(artifact, feature_dir, review_pin, seen)
        err += _bound_artifact_errors(artifact, feature_dir, review_pin, seen, code_grade)
    return err


def _bound_artifact_errors(artifact, feature_dir, review_pin, seen, code_grade):
    """Grade-2 reasons name the graded functions; inspection SCs are cited in the
    artifact. Both read the checkout the review is bound to."""
    fd, root, review_sha, _e = _review_binding(artifact, feature_dir, review_pin)
    if not (root and review_sha):
        return []
    err = []
    if code_grade == "grade_2":
        err.append(_grade_2_reasons_error(seen.get("grade_2_reasons") or [],
                                          _grade_2_qualnames(root, review_sha)))
    path = _artifact_text(artifact)
    if path:
        err.append(_inspection_citation_error(fd, root, path))
    return [e for e in err if e]


def _bound_tree_errors(artifact, feature_dir, review_pin, seen):
    """The dirty-tree and human-commit checks over the checkout the review is bound to."""
    _fd, root, review_sha, _e = _review_binding(artifact, feature_dir, review_pin)
    if not (root and review_sha):
        return []
    return [error for error in (_dirty_tree_error(root),
                                _human_commits_error(root, review_sha,
                                                     seen.get("human_commits_in_scope")))
            if error]


# --- LEAD ROLL-UP: the top verdict must be the WORST member verdict (SPEC 10.4).
#
# This is the only part of collation that is arithmetic rather than judgement, and
# it was the one thing stated in prose with a validator sitting next to it that
# could check it and didn't — the DEC-110 / DEC-119 shape exactly. A lead
# reporting PASS over a failing member is the single most consequential digest
# error possible: the orchestrator routes on VERDICT and never opens member
# entries (SPEC 8), so a masked FAIL ships.
#
# ESCALATE outranks FAIL deliberately: a decision only the user can make must not
# be hidden behind a failure the team could have fixed.
def _lead_rollup_errors(seen, top):
    members = seen.get("members")
    err = _empty_members_errors(members, seen.get("steps_run"))
    if isinstance(members, list) and members:
        err += _member_rank_errors(members, top)
    return err


def _empty_members_errors(members, steps_run):
    # F1 cross-check: `members: []` alongside `steps_run: 3` used to sail
    # through — SPEC 10.4 calls `members` "NOT optional", and a team that ran
    # steps but reported zero members is never legitimate. Checked whether or
    # not the roll-up itself can run, since an empty list makes the roll-up a
    # no-op (there is nothing to rank).
    if (isinstance(members, list) and isinstance(steps_run, int)
            and len(members) == 0 and steps_run > 0):
        return [f"members: [] but steps_run={steps_run} — a team that ran "
                f"{steps_run} step(s) reported zero members; that is never "
                f"legitimate (SPEC 10.4: members is NOT optional)."]
    return []


RANK = {"PASS": 0, "FAIL": 1, "ESCALATE": 2, "BLOCKED": 3}


def _member_rank_errors(members, top):
    worst, worst_src, err = _worst_member(members)
    if worst is None:
        err.append("members records no member actually ran — a lead verdict cannot "
                   "claim an outcome for an entirely skipped team.")
    if worst and top in RANK and RANK[top] < RANK[worst]:
        err.append(f"VERDICT is {top} but a member returned {worst} "
                   f"({worst_src!r}). The team verdict is the WORST member verdict "
                   f"— BLOCKED > ESCALATE > FAIL > PASS. The orchestrator routes on "
                   f"your VERDICT and never opens member entries, so reporting "
                   f"{top} here hides the {worst}.")
    return err


def _worst_member(members):
    """(worst verdict, its entry's head, errors) over the members that actually ran."""
    err = []
    worst, worst_src = None, None
    for item in members:
        v, error = _member_verdict(item)
        if error:
            err.append(error)
        elif _outranks(v, worst):
            worst, worst_src = v, str(item)[:60]
    return worst, worst_src, err


def _outranks(v, worst):
    """A ranked member verdict `v` that is worse than the worst seen so far (None = none yet)."""
    return v is not None and (worst is None or RANK[v] > RANK[worst])


def _member_verdict(item):
    """(ranked verdict or None for a skipped member, error or None) for one entry. Read by
    KEY from the entry's mapping (F1): a headline reading "verdict: PASS on retry" is text."""
    fields = item if isinstance(item, dict) else {}
    skipped, skip_error = _skipped_member_error(fields)
    if skip_error:
        return None, skip_error
    if skipped:
        return None, None
    mv = fields.get("verdict")
    if not mv:
        return None, (f"a members entry has no verdict: — {str(item)[:60]!r}. "
                      f"Every member entry needs one; the team verdict is the "
                      f"worst of them and cannot be computed otherwise.")
    v = str(mv).upper()
    if v not in RANK:
        return None, (f"member verdict {mv!r} is not one of "
                      f"{sorted(RANK)} — the roll-up cannot rank it.")
    return v, None


def _root_or_none():
    """This checkout's root, from harness_boundary — or None if there is not one (FEAT-42
    T-17).

    NONE RATHER THAN A RAISE. Every caller here treats an unresolvable root as "the errand
    could not be run", never as a verdict: this hook validates digests, and the registry and
    the artifact-shape check are side errands that may not change what it returns.
    """
    try:
        sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
        import harness_boundary
        return harness_boundary.resolve_root(
            os.path.dirname(os.path.realpath(__file__)), strict=False)
    except (ImportError, OSError, ValueError):
        return None

def _hook_feature_dir(artifact, feature):
    """Resolve an unmerged feature from an installed validator's owner checkout."""
    owner_root = _root_or_none()
    if owner_root is None or not feature:
        return None
    try:
        sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
        import inflight_registry
        checkout_root = inflight_registry.feature_root(owner_root, feature)
        feature_dir, error = _feature_dir_from_artifact(artifact, checkout_root)
        return None if error else feature_dir
    except (ImportError, OSError, ValueError):
        return None




# --- SC-07 (DEC-156, DEC-208): the lead's durable record. The lead writes only the human
# assessment in runs/<id>/digest.md; after its object passes every live check, this is the
# one writer of the fenced YAML under it. Identical to the file's last fenced mapping: no
# write. Different: one more block after the existing bytes, so the last mapping wins and
# nothing earlier is rewritten. A historical block is comparison input only — it is never
# validated against today's schema. A digest that cannot be resolved to a safe existing
# regular file, or cannot be written, refuses the return: the file is what a successor
# context reads.
def _durable_refusal(agent, why):
    print(f"check-digest: REFUSED {agent}'s return: {why} Your return is valid; the "
          f"durable digest is what a successor reads, so it must be written before you "
          f"finish (DEC-156).", file=sys.stderr)
    return 2




def check_artifact_file(agent, obj, payload):
    """Append the validated lead object to its durable digest.md (SC-07), or refuse."""
    import digest_destination
    path = _artifact_text(obj.get("artifact"))
    if not path.endswith("digest.md"):
        return _durable_refusal(agent, f"a lead's artifact is its run's digest.md, and "
                                       f"{obj.get('artifact')!r} is not one.")
    try:
        with digest_destination.authorized_digest(
                _root_or_none(), agent, payload, path) as (found, target):
            why = _append_record(found, obj, target)
    except (digest_destination.AuthorizationError, OSError, ValueError, TypeError) as error:
        return _durable_refusal(agent, str(error))
    return _durable_refusal(agent, why) if why else 0


def _last_record(text, where):
    """The file's last fenced mapping — comparison input only, never schema-validated."""
    try:
        return digest_record.last_fenced_mapping(text, where)
    except digest_record.DigestRecordError:
        return None


def _append_record(found, obj, target):
    """Append `obj` as one fenced block unless it equals the last one; the refusal reason,
    or None when the record now ends with `obj`. The dumper is harness_yaml's (D-12: one
    yaml import in the tree); without PyYAML the record cannot be written, so it refuses."""
    if harness_yaml.yaml is None:
        return f"its durable digest {found} cannot be written (PyYAML is not installed)."
    try:
        last = _last_record(target.read(), found)
    except (OSError, UnicodeDecodeError) as error:
        return f"its durable digest {found} cannot be read ({error})."
    if last == obj:
        return None
    try:
        target.write("\n```yaml\n" + harness_yaml.yaml.safe_dump(obj, sort_keys=False)
                     + "```\n")
        target.flush()
    except OSError as error:
        return f"its durable digest {found} cannot be written ({error})."
    print(f"check-digest: appended the validated digest to {found}"
          f"{' as a correction' if last is not None else ''}.", file=sys.stderr)
    return None


def _qa_claims_unconditional_pass(obj):
    """True iff the return is VERDICT: PASS with suite: pass AND matrix_ok: true — the one
    claim #919 exists to independently re-verify."""
    seen = obj.get("DIGEST") if isinstance(obj.get("DIGEST"), dict) else {}
    return (obj.get("VERDICT") == "PASS" and seen.get("suite") == "pass"
            and seen.get("matrix_ok") is True)


def _artifact_holder(artifact):
    """The linked worktree (or owner root) holding the digest's absolute artifact, or None
    when the digest names none, a relative one, or one outside the family (#1883)."""
    owner_root = _root_or_none()
    if not isinstance(artifact, str) or not artifact.strip() or not owner_root:
        return None
    path = artifact.strip()
    return _worktree_holding(owner_root, path) if os.path.isabs(path) else None


def _resolve_run_unit_tests_bin(payload, artifact=None):
    """The suite entrypoint to independently re-run, or None if it cannot be resolved.

    RUN_UNIT_TESTS_BIN is test-only: it lets a fixture point this check at a fast stub
    instead of spawning the real multi-minute suite for every hook-mode case.

    A NAMED FEATURE MUST RESOLVE TO ITS OWN CHECKOUT, OR NOT AT ALL (code review of
    #1185). check_artifact_file's owner_root/feature_root pattern falls back to
    owner_root on any lookup failure, and that is safe THERE because a wrong root
    means the specific run digest simply 404s, loudly. run-unit-tests.py is a static,
    always-present path: a wrong-root fallback here never 404s, it just silently
    re-runs the suite against the WRONG checkout and reports that mismatched result as
    though it verified the claim — reproducing #919's exact failure mode inside the
    gate built to close it. So a feature_root lookup failure returns None (cannot
    resolve) rather than substituting owner_root; the caller's existing "could not
    independently re-run" fail-open path is where that lands.
    """
    # THE ARTIFACT'S CHECKOUT FIRST (#1883). `feature_root` resolves by worktree NAME and
    # substitutes the owner root when nothing is named after the feature — measured on a
    # branch worktree called `process-gaps`: the suite re-ran against the owner checkout
    # on a stale branch and refused a qa PASS on that tree's failure. The digest's own
    # artifact line names the checkout it was written from; when that lies inside the
    # owner's worktree family it is the checkout to re-run, deterministically.
    run_bin = os.environ.get("RUN_UNIT_TESTS_BIN")
    if run_bin:
        return run_bin
    holder = _artifact_holder(artifact)
    if holder:
        return os.path.join(holder, ".claude", "skills", "harness", "bin",
                            "run-unit-tests.py")
    owner_root = _root_or_none()
    feature = payload.get("harness_feature")
    if not feature:
        base = owner_root
    elif not owner_root:
        base = None
    else:
        try:
            sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
            import inflight_registry
            base = inflight_registry.feature_root(owner_root, feature)
        except (ImportError, OSError, ValueError):
            base = None
    if not base:
        return None
    return os.path.join(base, ".claude", "skills", "harness", "bin",
                        "run-unit-tests.py")


def _claimed_kinds(seen):
    """The test kinds the qa return's `kinds` names, in order, deduplicated — the matrix
    the claim is about. Empty when the digest names none (the runner's default set then
    governs)."""
    entries = seen.get("kinds") if isinstance(seen.get("kinds"), list) else []
    kinds = [str(entry.get("kind", "")).strip() for entry in entries if isinstance(entry, dict)]
    return list(dict.fromkeys(k for k in kinds if k))


def _reverify_suite(run_bin, kinds=()):
    """Run the Python runner — with `sys.executable`, never a shell: run-unit-tests.py has
    been a Python file since #1674 and bash reading it exited 2 on every honest PASS
    (BUG-1756) — once per claimed kind (`--kind <k>`), or once bare when the claim names
    none. Returns the first non-zero CompletedProcess, else the last one; None if it could
    not be run at all (missing file, spawn failure, timeout) — every such case is our gap,
    not theirs."""
    if not run_bin or not os.path.isfile(run_bin):
        return None
    invocations = [["--kind", k] for k in kinds] or [[]]
    result = None
    for extra in invocations:
        try:
            result = subprocess.run([sys.executable, run_bin, *extra], capture_output=True,
                                    text=True, timeout=1800)
        except (OSError, subprocess.SubprocessError, ValueError):
            return None
        if result.returncode != 0:
            return result
    return result


def check_qa_matrix_claim(agent, obj, payload):
    """Issue #919: independently re-run the suite before trusting an unconditional
    qa PASS, rather than trusting the claim on its own strength.

    FEAT-37's qa gate reported the matrix green at a SHA where CI failed on the first
    open PR: the qa note's discovered-script count was not read from a real run's own
    output, and "ALL PASSED" was recorded anyway. `GATE_FAIL_VALUES` above can only catch a digest
    that CONTRADICTS itself (`suite: fail` beside `VERDICT: PASS`); it cannot catch a
    wrong-but-internally-consistent claim, because nothing before this re-executes the
    thing being claimed. This does — the report is evidence only once it is checked.

    FIRES ONLY on the highest-stakes claim: VERDICT: PASS with suite: pass AND
    matrix_ok: true. A FAIL/BLOCKED/n/a claim already carries its own honesty
    (`validate()` above already refuses `suite: fail` + PASS); re-running to confirm a
    claimed failure buys nothing this hook is positioned to check for free.

    FAIL OPEN, LOUDLY when the suite cannot be located or run at all (missing root,
    missing script, a spawn OSError, a timeout) — check-domain.py's precedent: a hook
    whose own execution environment is broken must never be the reason a legitimate qa
    return is blocked. FAIL CLOSED when the suite DOES run and disagrees with the
    claim — that disagreement is exactly the gap #919 exists to close.
    """
    if not _qa_claims_unconditional_pass(obj):
        return 0
    run_bin = _resolve_run_unit_tests_bin(payload, obj.get("artifact"))
    result = _reverify_suite(run_bin, _claimed_kinds(obj.get("DIGEST") or {}))
    if result is None:
        print(f"check-digest: could not independently re-run the suite at {run_bin!r} "
              f"— {agent}'s matrix_ok: true / suite: pass claim was NOT verified; this "
              f"is our gap, not theirs.", file=sys.stderr)
        return 0
    if result.returncode == 0:
        return 0
    print(f"{agent} reported VERDICT: PASS with suite: pass and matrix_ok: true, but "
          f"an independent re-run of run-unit-tests.py at this checkout exited "
          f"{result.returncode} — the gate reported evidence it did not have (issue "
          f"#919). Re-run the suite yourself, fix what fails, and return again once "
          f"it is genuinely green. Tail of the independent run:", file=sys.stderr)
    for line in ((result.stdout or "") + (result.stderr or "")).splitlines()[-20:]:
        print(f"  {line}", file=sys.stderr)
    return 2


def _exact_run_identity(d):
    """(feature, runtime agent id) when the payload names both exactly, else (None, None).

    BUG-1898: these two values are the ONLY claim selector the hook may use. A missing,
    blank, padded or non-string value is absent — never a reason to widen the selector to
    the persona, which is how a suite run or a re-validation released a live stranger."""
    feature = d.get("harness_feature")
    agent_id = d.get("harness_agent_id")
    exact = all(isinstance(value, str) and value and value == value.strip()
                for value in (feature, agent_id))
    return (feature, agent_id) if exact else (None, None)


def _identity_refusal(agent, verdict):
    """No exact identity: release nothing. A BLOCKED return is the one way out for a run
    T-02 holds without a claim, so it proceeds to validation; any other return is refused."""
    if verdict == "BLOCKED":
        print(f"check-digest: {agent}'s BLOCKED return names no exact feature and runtime "
              "id; no claim was looked up or released.", file=sys.stderr)
        return None
    print(f"check-digest: REFUSED {agent}'s return: it names no exact harness_feature and "
          "harness_agent_id, so its claim cannot be found without guessing by persona, and "
          "nothing was released. A run that holds no claim of its own yields a BLOCKED "
          "digest naming why.", file=sys.stderr)
    return 2


def _dispatches(agent):
    """Only a lead or the orchestrator dispatches, so only they can hold live children."""
    return norm(agent) in ("lead", "orchestrator")


def _held_children(reg, root, agent, feature, agent_id):
    """Live claims whose parent is this exact run, in `root`'s registry. Raises
    UnreadableRegistry rather than reading "cannot read" as "no children"."""
    if not _dispatches(agent):
        return []
    return [
        claim for claim in reg.live_claims(root, None, parent_agent_id=agent_id)
        if claim.get("feature", reg.LEGACY_FEATURE) == feature
    ]


def _children_refusal(reg, root, agent, children):
    for line in reg.children_refusal_lines(
            agent, [(claim.get("agent"), claim) for claim in children]):
        print(line, file=sys.stderr)
    print("  your own claim is kept. If one of these is stranded rather than running, "
          "release exactly it:", file=sys.stderr)
    for claim in children:
        print("  %s" % reg.release_cmd(
            root, claim.get("agent"), claim.get("feature"),
            agent_id=claim.get("agent_id"), claim_id=claim.get("claim_id"),
        ), file=sys.stderr)
    return 2


def _unreadable_registry(agent, root, error, verdict):
    """F-01: "cannot read" is never "no live child". A dispatching parent's return is held
    unless it is BLOCKED — its one way out while the operator repairs the file; a leaf holds
    no children and goes on. Either way nothing is written, so the file stays as found."""
    if _dispatches(agent) and verdict != "BLOCKED":
        print(f"check-digest: REFUSED {agent}'s return: {root}'s claim registry is unreadable "
              f"({error!r}), so this run cannot tell whether it holds a live child. Nothing was "
              "released. A retry cannot succeed until the operator repairs the registry; "
              "yield a BLOCKED digest naming this cause.", file=sys.stderr)
        return 2
    print(f"check-digest: could not read {root}'s claim registry ({error!r}); nothing was "
          "released and the registry was left as found.", file=sys.stderr)
    return None


def _registry_errand(reg, d, agent, verdict):
    """T-09 (#551) and BUG-1898: release this run's claim, or refuse the return while it
    holds a live child. Returns an exit code to return, or None to go on validating.

    Exact or nothing: the claim is selected by feature AND runtime id only, in the registry
    `feature_root` places the feature in — the one resolver dispatch-guard and the OMP hook
    also use, so the claim a guard wrote is the claim released here. A parent with a live
    child keeps its own claim (DEC-233), and every recovery command names one claim."""
    feature, agent_id = _exact_run_identity(d)
    if feature is None:
        return _identity_refusal(agent, verdict)
    owner_root = _root_or_none()
    if owner_root is None:
        print("check-digest: no checkout root from this vantage; the #551 claim was "
              "neither released nor checked.", file=sys.stderr)
        return None
    return _settle_in(reg, verdict, agent, reg.feature_root(owner_root, feature), feature,
                      agent_id)


def _settle_in(reg, verdict, agent, root, feature, agent_id):
    """Settle this exact run in `root`'s registry: refuse while it holds a live child, else
    release its own claim. Strict reads come before any write: the locked writer parses a
    corrupt file as empty, so releasing into an unreadable registry would erase every claim
    it holds."""
    try:
        own = reg.live_claims(root, None, agent_id=agent_id)
        children = _held_children(reg, root, agent, feature, agent_id)
    except (reg.UnreadableRegistry, OSError) as error:
        return _unreadable_registry(agent, root, error, verdict)
    if children:
        return _children_refusal(reg, root, agent, children)
    if own:
        _release_own(reg, root, agent, feature, agent_id)
    return None


def _release_own(reg, root, agent, feature, agent_id):
    try:
        if reg.release(root, agent=agent, feature=feature, agent_id=agent_id):
            print(f"check-digest: released {agent}'s claim {agent_id} for {feature}.",
                  file=sys.stderr)
    except (reg.UnreadableRegistry, reg.harness_merge.MergeRefusal, OSError) as error:
        print(f"check-digest: could not release {agent}'s claim ({error!r}); it expires with "
              "its supervisor. Not blocking on our own errand.", file=sys.stderr)


_ABSENT = object()  # distinguishes an absent `digest_object` from a present null


def _object_refusal(agent, value):
    shape = "absent" if value is _ABSENT else f"a {type(value).__name__}"
    print(f"check-digest: {agent or 'this agent'}'s yield carried no digest object (`data` "
          f"was {shape}); {OBJECT_REQUIRED}", file=sys.stderr)
    return 2


def hook_mode():
    """The yield hook: reject a malformed digest object at source.

    Exit 2 blocks the yield as a retryable tool error, so the agent must fix its return
    before it can finish — enforcement rather than a request. The payload's
    `digest_object` is the raw `data` of the yield; it is validated as given and NOTHING
    else is read as a digest — no assistant text, no string `data`, no repair.

    Pass-throughs, each deliberate and each only for a real mapping:

    1. A PRESENT non-harness `agent_type` (`Explore`, `general-purpose`) has no digest
       contract and is never governed.
    2. A MISSING `agent_type` passes loudly (F6): the key may have been renamed and this
       hook gone dark. A non-mapping is still refused — it cannot be a digest either way.
    3. `stop_hook_active` — a re-run after a block — passes a mapping unvalidated.
    4. Our own failure is harness_boundary.hook_guard's (FEAT-65): an unreadable payload
       or an exception out of validate() prints the guard's template and exits 0. An
       unknown persona is a local, typed decline.
    """
    d = artifact_accessors.read_hook_payload(sys.stdin.read(), "yield hook payload")
    agent = d.get("agent_type")
    obj = d.get("digest_object", _ABSENT)
    passed = _pass_through(d, agent, obj)
    if passed is not None:
        return passed
    # T-09 (#551): release first, then the return contract. Reversed, an agent refused at
    # step two would never have its own claim released and would leak it until the TTL.
    refused = _settle_claim(d, agent, obj.get("VERDICT") if isinstance(obj, dict) else None)
    if refused is not None:
        return refused
    if not isinstance(obj, dict):
        return _object_refusal(agent, obj)
    return _validate_hook_object(d, agent, obj)


def _governed_agent(agent):
    return isinstance(agent, str) and agent.startswith("harness-")


def _pass_through(d, agent, obj):
    """The exit code of a return this hook does not govern, or None to govern it."""
    if agent and not _governed_agent(agent):
        return 0
    if agent and not d.get("stop_hook_active"):
        return None
    if not isinstance(obj, dict):
        return _object_refusal(agent, obj)
    if not agent:
        print("check-digest: hook payload has no agent_type — passing through. If this "
              "is unexpected, the payload key may have been renamed and this hook is "
              "silently no-oping project-wide.", file=sys.stderr)
    return 0


def _settle_claim(d, agent, verdict):
    """The registry side errand: refuses only for a live child or an unreadable registry
    under a dispatching parent, and never changes the digest verdict."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
        import inflight_registry
    except ImportError as error:
        print(f"check-digest: inflight_registry unavailable ({error!r}) — the #551 claim was "
              f"neither released nor checked. This is our gap, not theirs.", file=sys.stderr)
        return None
    return _registry_errand(inflight_registry, d, agent, verdict)


def _hook_options(d):
    pin = d.get("harness_review_pin")
    mission = d.get("harness_mission")
    return (pin.strip() if isinstance(pin, str) and pin.strip() else None,
            mission.strip() if isinstance(mission, str) else None)


def _validate_hook_object(d, agent, obj):
    try:
        family = norm(digest_schema.canonical_persona(agent))
    except digest_schema.DigestSchemaError:
        print(f"check-digest: no schema for {agent} — passing through rather than "
              f"blocking on our own gap.", file=sys.stderr)
        return 0
    # Only the policy refusal is answered here, because it is THEIR verdict (exit 2); every
    # other exception is our failure and hook_guard's loud fail-open.
    review_pin, mission = _hook_options(d)
    try:
        errs = validate(agent, obj, review_pin=review_pin, mission=mission,
                        feature_dir=_hook_feature_dir(obj.get("artifact"),
                                                      d.get("harness_feature")))
    except GatePolicyError as error:
        print(f"check-digest: {error}", file=sys.stderr)
        return 2
    if errs:
        return _contract_refusal(errs)
    if family == "lead":
        return check_artifact_file(agent, obj, d)
    if family == "qa":
        return check_qa_matrix_claim(agent, obj, d)
    return 0


def _contract_refusal(errs):
    print("Your return does not satisfy the digest contract, so it cannot be accepted. "
          "Fix these and return again — every field is required; say nothing with an "
          "explicit `[]`, or `none` for a scalar that genuinely does not apply:",
          file=sys.stderr)
    for e in errs:
        print(f"  - {e}", file=sys.stderr)
    return 2


def cli_object(text, where):
    """`(mapping, None)` for CLI input, or `(None, error)`. One JSON object is the live
    shape; anything else is read as a durable digest.md and its last fenced mapping is the
    object — feature-record.py close-run validates a run's digest.md this way, against the
    same live schema. No other text is parsed."""
    try:
        return digest_schema.decode_object_json(text, where), None
    except digest_schema.DigestSchemaError as json_error:
        try:
            return digest_record.last_fenced_mapping(text, where), None
        except digest_record.DigestRecordError as record_error:
            return None, (f"{where} is neither one JSON digest object ({json_error}) nor a "
                          f"durable digest.md with a fenced mapping ({record_error}).")


if __name__ == "__main__":
    if "--hook" in sys.argv:
        sys.exit(harness_boundary.hook_guard(hook_mode, "check-digest"))
    # F14: CLI mode crashed with UnicodeEncodeError under an ASCII locale (LC_ALL=C),
    # truncating the printed reasons before the operator saw them.
    try:
        sys.stdout.reconfigure(errors="backslashreplace")
    except (AttributeError, OSError, ValueError):
        pass
    if len(sys.argv) < 2:
        print("usage: validate-digest.py <persona> [file]   |   --hook"); sys.exit(2)
    if len(sys.argv) > 2:
        with open(sys.argv[2], encoding="utf-8") as source:
            text, where = source.read(), sys.argv[2]
    else:
        text, where = sys.stdin.read(), "stdin"
    obj, error = cli_object(text, where)
    errs = [error] if error else validate(sys.argv[1], obj)
    if errs:
        print("VERDICT: BLOCKED (contract violation)")
        for e in errs: print(f"  - {e}")
        sys.exit(1)
    print("digest ok")
